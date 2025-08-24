import os
import gradio as gr
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
from auth import oauth
from gradio_ui import main_app

import dotenv
dotenv.load_dotenv()

app = FastAPI()

@app.middleware("http")
async def enforce_https(request: Request, call_next):
    # Allow local dev without HTTPS
    if request.url.hostname in ("127.0.0.1", "localhost"):
        return await call_next(request)

    # On HF, check forwarded proto
    proto = request.headers.get("x-forwarded-proto")
    if proto and proto != "https":
        url = request.url.replace(scheme="https")
        return RedirectResponse(url)

    return await call_next(request)

app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key",
    same_site="none",
    https_only=True,
)

@app.get("/")
async def root():
    return RedirectResponse("/secure")

@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    if "HF_SPACE" in os.environ:
        redirect_uri = redirect_uri.replace(scheme="https")
    return await oauth.google.authorize_redirect(request, str(redirect_uri))

@app.get("/auth/callback")
async def auth_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo")
        request.session["user"] = user_info
        return RedirectResponse("/secure")
    except Exception as e:
        print(f"Error during auth callback: {e}")
        return RedirectResponse("/secure")

@app.get("/logout")
async def logout(request: Request):
    request.session["user"] = None
    return RedirectResponse("/secure")

# Mount a single Gradio app at /
demo = main_app()
app = gr.mount_gradio_app(app, demo, path="/secure")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
