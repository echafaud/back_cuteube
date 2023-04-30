import fastapi_jsonrpc as jsonrpc
from pydantic import BaseModel
from starlette.responses import Response

from fastapi import Depends

from fastapi_users import exceptions, models
from fastapi_users.manager import BaseUserManager
from fastapi_users.router.common import ErrorCode

from src.auth.auth import Settings, advanced_authentication_backend
from src.auth.authenticator import Authenticator
from src.auth.exceptions import LoginBadCredentials
from src.auth.models import User
from src.auth.shemas import UserRead, UserCreate
from src.auth.user_manager import get_user_manager, AuthPasswordRequestForm

app = jsonrpc.API()
api_v1 = jsonrpc.Entrypoint('/api/v1/jsonrpc')


@Authenticator.load_config
def get_config():
    return Settings()


@api_v1.method(result_model=UserRead)
async def register(
        user_create: UserCreate,
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager)
):
    created_user = await user_manager.create(user_create, safe=True)

    return created_user


@api_v1.method()
async def login(response: Response, credentials: AuthPasswordRequestForm = Depends(),
                user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
                ):
    user = await user_manager.authenticate(credentials)
    advanced_authentication_backend.advanced_login(response, user)
    await user_manager.on_after_login(user)


# authenticator = Authenticator([auth_backend], get_user_manager)
adv_auth = Authenticator(get_user_manager, )

access_user = adv_auth.current_user(token_type="access")

refresh_user = adv_auth.current_user(token_type="refresh")
# curr_user = authenticator.current_user()


@api_v1.method()
async def logout(response: Response, user: User = Depends(access_user),
                 user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
                 ):
    advanced_authentication_backend.advanced_logout(response, user)
    await user_manager.on_after_logout(user)


@api_v1.method()
async def refresh(response: Response, user: User = Depends(refresh_user),
                  ):
    return advanced_authentication_backend.refresh(response, user)


@api_v1.method()
async def protected(user: User = Depends(access_user)) -> str:
    return user.username


app.bind_entrypoint(api_v1)
