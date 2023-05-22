import uuid
from typing import Optional, Union

from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users.password import PasswordHelperProtocol, PasswordHelper
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from fastapi import Depends, Request, Response
from fastapi_users import BaseUserManager, IntegerIDMixin, exceptions, models, schemas, UUIDIDMixin
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.param_functions import Form

from src.auth.exceptions import UserAlreadyExists, InvalidPassword, LoginBadCredentials
from src.auth.shemas import UserLogin
from src.auth.user_database_adapter import UserDatabaseAdapter
from src.database import get_async_session

from src.auth.models import User
from src.config import SECRET


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def create(
            self,
            user_create: schemas.UC,
            safe: bool = False,
            request: Optional[Request] = None,
    ) -> models.UP:
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_username(user_create.username)
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

        await self.on_after_register(created_user, request)

        return created_user

    async def validate_password(
            self, password: str, user: Union[schemas.UC, models.UP]
    ) -> None:
        if len(password) < 8:
            raise InvalidPassword(data={'reason': 'Password should beat least 8 characters'})
        elif not any(character.isdigit() for character in password):
            raise InvalidPassword(data={'reason': 'Password should have at least one numeral'})
        elif not any(character.isupper() for character in password):
            raise InvalidPassword(data={'reason': 'Password should have at least one uppercase letter'})
        elif not any(character.islower() for character in password):
            raise InvalidPassword(data={'reason': 'Password should have at least one lowercase letter'})

        return

    # todo validate username

    async def authenticate(
            self, credentials: UserLogin
    ) -> Optional[models.UP]:
        """
        Authenticate and return a user following an email and a password.

        Will automatically upgrade password hash if necessary.

        :param credentials: The user credentials.
        """
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
            return None
        # Update password hash to a more robust one if needed
        if updated_password_hash is not None:
            await self.user_db.update(user, {"hashed_password": updated_password_hash})

        return user

    async def on_after_logout(
            self, user: models.UP, request: Optional[Request] = None
    ) -> None:
        await self.user_db.update(user, {"is_active": False})

    async def on_after_login(
            self,
            user: models.UP,
            request: Optional[Request] = None,
            response: Optional[Response] = None,
    ) -> None:
        await self.user_db.update(user, {"is_active": True})
