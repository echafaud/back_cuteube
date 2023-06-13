import uuid
from uuid import UUID
from datetime import timedelta
from typing import Optional
from fastapi_users.password import PasswordHelperProtocol, PasswordHelper

from src.redis_manager.redis_manager import RedisManager
from src.user.exceptions import UserAlreadyExists, InvalidPassword, LoginBadCredentials, InvalidField, \
    UserVerifyException
from src.user.shemas import UserLogin, UserCreate
from src.user.models import User
from src.user.user_database_adapter import UserDatabaseAdapter
from src.user.tasks import send_verify_mail
import re


class AuthUserManager:
    def __init__(
            self,
            user_db: UserDatabaseAdapter,
            password_helper: Optional[PasswordHelperProtocol] = None,
            redis_manager: RedisManager = None,
    ):
        self.user_db = user_db
        self.redis_manager = redis_manager
        if password_helper is None:
            self.password_helper = PasswordHelper()
        else:
            self.password_helper = password_helper

    async def create(
            self,
            user_create: UserCreate,
            safe: bool = False,
    ) -> User:
        self.validate_password(user_create.password)
        self.base_field_validete(r'^[A-Za-z0-9_]*$', user_create.username,
                                 "Username", 'can contain only Latin letters, numbers and the symbol _')
        self.base_field_validete(r'^[а-яА-ЯёЁa-zA-Z0-9_]*$', user_create.name, "Name",
                                 'can contain only Cyrillic letters, Latin letters, numbers and the symbol _')

        existing_user = await self.user_db.get_by_username(user_create.username) or await self.user_db.get_by_email(
            user_create.email)
        if existing_user is not None:
            raise UserAlreadyExists

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)
        user_dict["username"] = user_dict["username"].lower()

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user)

        return created_user

    async def authenticate(
            self,
            credentials: UserLogin
    ) -> User:
        user = await self.user_db.get_by_email(credentials.username) or await self.user_db.get_by_username(
            credentials.username)
        if user is None:
            # Run the hasher to mitigate timing attack
            # Inspired from Django: https://code.djangoproject.com/ticket/20760
            self.password_helper.hash(credentials.password)
            raise LoginBadCredentials

        verified, updated_password_hash = self.password_helper.verify_and_update(
            credentials.password, user.hashed_password
        )
        if not verified:
            raise LoginBadCredentials
        # Update password hash to a more robust one if needed
        if updated_password_hash is not None:
            await self.user_db.update(user, {"hashed_password": updated_password_hash})

        return user

    async def verify(self, user: User, token: UUID):
        verify_token = await self.redis_manager.get(f'verifyUser:{user.id}:UUID', execute=True)
        if not verify_token[0]:
            raise UserVerifyException(data={'reason': 'Link has expired'})
        if verify_token[0].decode('utf-8') != str(token):
            raise UserVerifyException(data={'reason': 'Invalid verification token'})

    async def update_verify(self, user: User):
        exp_time = await self.redis_manager.get_time_exp(f'verifyUser:{user.id}:UUID', execute=True)
        if timedelta(seconds=exp_time[0]) > timedelta(minutes=14):
            raise UserVerifyException(data={'reason': 'You can\'t update the link right away'})
        await self.on_after_register(user)

    def validate_password(
            self,
            password: str,
    ) -> None:
        if len(password) < 8:
            raise InvalidPassword(data={'reason': 'Password should beat least 8 characters'})
        elif re.search('[0-9]', password) is None:
            raise InvalidPassword(data={'reason': 'Password should have at least one numeral'})
        elif re.search('[A-Z]', password) is None:
            raise InvalidPassword(data={'reason': 'Password should have at least one uppercase letter'})
        elif re.search('[a-z]', password) is None:
            raise InvalidPassword(data={'reason': 'Password should have at least one lowercase letter'})
        elif re.search(r'[.,;?!\\+\-@#$%^&*\'"<>{}()\[\]|`~/_=]', password) is None:
            raise InvalidPassword(data={'reason': 'Password should have at least one special character'})
        elif re.search(re.compile(r'^[A-Za-z0-9.,;?!+@#$%^&*"\'<>{}()\[\]|`~/_=\\\-]*$'), password) is None:
            raise InvalidPassword(
                data={'reason': 'Password can contain only Latin letters, numbers and special characters'})

    def base_field_validete(
            self,
            regex: str,
            field: str,
            field_name: str,
            message: str,
            min_len: int = 2,
            max_len: int = 32
    ) -> None:
        if len(field) < min_len:
            raise InvalidField(data={'details': f'{field_name} should beat least {min_len} characters'})
        elif re.search(re.compile(regex), field) is None:
            raise InvalidField(
                data={'details': f'{field_name} {message}'})
        elif len(field) > max_len:
            raise InvalidField(data={'details': f'{field_name} must contain no more than {max_len} characters'})

    async def on_after_logout(
            self,
            user: User,
    ) -> None:
        await self.user_db.update(user, {"is_active": False})

    async def on_after_login(
            self,
            user: User,
    ) -> None:
        await self.user_db.update(user, {"is_active": True})

    async def on_after_register(self,
                                user: User,
                                ) -> None:
        token = str(uuid.uuid4())
        await self.redis_manager.set(f'verifyUser:{user.id}:UUID', token, timedelta(minutes=15), execute=True)
        user_data = {'id': user.id, 'username': user.username, 'email': user.email, 'token': token}
        send_verify_mail.delay(user_data)
