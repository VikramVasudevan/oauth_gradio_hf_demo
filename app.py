import gradio as gr
import time

# -------------------------------
# Function to check HF login
# -------------------------------
def protected_app(request: gr.Request):
    # tiny delay to ensure HF client is populated
    time.sleep(0.2)

    if getattr(request.client, "is_authenticated", False):
        username = getattr(request.client, "username", "Unknown")
        return f"Hello {username}! You are logged in via Hugging Face."
    else:
        return (
            "You are not logged in. "
            "Please open this Space directly at "
            "https://huggingface.co/spaces/vikramvasudevan/oauth_gradio_hf_demo "
            "and log in."
        )

# -------------------------------
# Build the Gradio app
# -------------------------------
with gr.Blocks() as demo:
    gr.Markdown("## Hugging Face Protected App")

    output = gr.Textbox(label="Welcome message", interactive=False)
    refresh_btn = gr.Button("Refresh Login Status")
    logout_btn = gr.Button("Logout from HF")

    # Update message on load
    demo.load(fn=protected_app, inputs=None, outputs=output)

    # Refresh login status when button clicked
    refresh_btn.click(fn=protected_app, inputs=None, outputs=output)

    # Open HF logout page when logout clicked
    logout_btn.click(lambda: "https://huggingface.co/logout", None, None, _js="(url)=>window.open(url, '_self')")

# -------------------------------
# Launch (HF handles the server)
# -------------------------------
demo.launch()
