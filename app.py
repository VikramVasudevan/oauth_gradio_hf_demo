import gradio as gr
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

# ------------------------------------------------------------
# FastAPI app
# ------------------------------------------------------------
app = FastAPI()

# ------------------------------------------------------------
# Root redirect to secure app
# ------------------------------------------------------------
@app.get("/")
async def root():
    return RedirectResponse(url="/secure")

# ------------------------------------------------------------
# Gradio protected app using Hugging Face authentication
# ------------------------------------------------------------
def protected_app(request: gr.Request):
    """
    Gradio function that runs per user request.
    Uses request.client to check HF login.
    """
    if not getattr(request.client, "is_authenticated", False):
        return "Access denied. Please log in via Hugging Face."
    username = getattr(request.client, "username", "Unknown")
    return f"Hello {username}! You are logged in via Hugging Face."

# Build the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("## Protected Gradio App (Hugging Face Auth)")
    output = gr.Textbox(label="Welcome message", interactive=False)
    demo.load(fn=protected_app, inputs=None, outputs=output)

# Mount Gradio at /secure
from gradio.routes import mount_gradio_app
mount_gradio_app(app, demo, path="/secure")

# ------------------------------------------------------------
# Optional: logout route (clears HF session in browser)
# ------------------------------------------------------------
@app.get("/logout")
async def logout():
    # HF login is managed by Hugging Face, so redirecting user
    return RedirectResponse("https://huggingface.co/logout")

# ------------------------------------------------------------
# Run locally
# ------------------------------------------------------------
if __name__ == "__main__":
    demo.launch()
