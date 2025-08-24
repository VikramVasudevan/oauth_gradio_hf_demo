import os
import gradio as gr
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
from auth import oauth
from gradio_ui import main_app

import dotenv
dotenv.load_dotenv()

app = FastAPI()

# --- Middleware to force HTTPS on HF ---
class HttpsRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.scheme == "http" and request.url.hostname.endswith(".hf.space"):
            url = str(request.url).replace("http://", "https://", 1)
            return RedirectResponse(url)
        return await call_next(request)

app.add_middleware(HttpsRedirectMiddleware)

app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key",
    same_site="none",
    https_only=True,
)

@app.get("/")
async def root(request: Request):
    # Localhost → relative path (safe, avoids https redirect loop)
    if request.url.hostname in ("127.0.0.1", "localhost"):
        return RedirectResponse(url="/secure")

    # HF Spaces (or anywhere else) → force HTTPS absolute path
    base_url = str(request.base_url).rstrip("/")
    url = f"{base_url}/secure"
    url = url.replace("http://", "https://")  # patch for HF mixed-content issue
    return RedirectResponse(url)

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
