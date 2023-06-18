import fastapi_jsonrpc as jsonrpc

from fastapi import Request
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.comment.endpoints import comment_router
from src.config import ORIGINS
from src.like.endpoints import like_router
from src.subscription.endpoints import subscription_router
from src.user.endpoints import user_router
from src.user.exceptions import AccessDenied
from src.video.endpoints import video_router
from src.video.exceptions import UploadVideoException
from src.view.endpoints import view_router

app = jsonrpc.API()



def error_handler(request: Request, exc: jsonrpc.BaseError):
    content = exc.get_resp()
    return JSONResponse(
        status_code=200,
        content=content,
    )


app.add_exception_handler(AccessDenied, error_handler)
app.add_exception_handler(UploadVideoException, error_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "X-CSRF-Token"],
)

app.bind_entrypoint(user_router)
app.bind_entrypoint(video_router)
app.bind_entrypoint(like_router)
app.bind_entrypoint(comment_router)
app.bind_entrypoint(view_router)
app.bind_entrypoint(subscription_router)
