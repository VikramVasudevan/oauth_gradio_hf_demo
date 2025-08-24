import gradio as gr

# ------------------------------------------------------------
# Function that checks HF authentication
# ------------------------------------------------------------
def protected_app(request: gr.Request):
    """
    request.client.is_authenticated is True if the user is logged into HF
    """
    if not getattr(request.client, "is_authenticated", False):
        return "Access denied. Please log in via Hugging Face."

    username = getattr(request.client, "username", "Unknown")
    return f"Hello {username}! You are logged in via Hugging Face."

# ------------------------------------------------------------
# Build the Gradio app
# ------------------------------------------------------------
with gr.Blocks() as demo:
    gr.Markdown("## Protected Gradio App (Hugging Face Auth)")
    
    # Output box to show welcome message
    output = gr.Textbox(label="Welcome message", interactive=False)
    
    # Load the message when the app starts
    demo.load(fn=protected_app, inputs=None, outputs=output)

# ------------------------------------------------------------
# Launch the app (HF Spaces handles the server automatically)
# ------------------------------------------------------------
demo.launch()
