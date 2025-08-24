import gradio as gr
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
from auth import oauth, GOOGLE_CLIENT_ID
from gradio_ui import login_page, main_app, secured_app

# Add this to handle .env file loading if not already done
import dotenv
dotenv.load_dotenv()

# The main FastAPI app
app = FastAPI()
# app.add_middleware(SessionMiddleware, secret_key="your-secret-key") # Change this!
app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key",
    same_site="none",
    https_only=True
)


# Define a simple home page or an authentication page
@app.get("/")
def read_root(request: Request):
    user = request.session.get("user")
    if user:
        # return f"Hello, {user.get('name')}! You are authenticated."
        return RedirectResponse(url="/gradio")
    else:
        return RedirectResponse(url="/login")

# Login route
# @app.get('/login')
# async def login(request: Request):
#     redirect_uri = request.url_for('auth_callback')
#     return await oauth.google.authorize_redirect(request, redirect_uri)

import os

@app.get('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth_callback')

    # Force https in prod (HF Spaces)
    if "HF_SPACE" in os.environ:  # HF sets env vars like HF_SPACE
        redirect_uri = redirect_uri.replace(scheme="https")

    return await oauth.google.authorize_redirect(request, str(redirect_uri))

# Auth callback route
@app.get('/auth/callback')
async def auth_callback(request: Request):
    try:
        # Get the token from the authorization callback
        token = await oauth.google.authorize_access_token(request)

        print("token = ", token)
        
        # Parse the ID token from the token response
        # authlib's authorize_access_token *should* return it if scopes are correct
        user_info = token["userinfo"]
        
        request.session['user'] = user_info
        return RedirectResponse(url="/gradio")
    
    except Exception as e:
        # Handle cases where `parse_id_token` fails or `id_token` is missing
        print(f"Error during auth callback: {e}")
        # return RedirectResponse(url="/login")

# Gradio authentication dependency
def auth_dependency(request: Request):
    user = request.session.get('user')
    if not user:
        # Instead of an APIError, redirect to login page
        return RedirectResponse(url="/login")
    return user.get('email')

# Mount Gradio app with dependency
main_gradio_app = main_app()
app = gr.mount_gradio_app(
    app,
    main_gradio_app,
    path="/gradio",
    auth_dependency=auth_dependency,
)

# Logout route
@app.get('/logout')
async def logout(request: Request):
    # request.session.pop('user', None)
    request.session['user'] = None
    return RedirectResponse(url="/gradio")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)