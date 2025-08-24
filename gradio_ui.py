import gradio as gr

def main_app():
    with gr.Blocks() as demo:
        msg = gr.Markdown("Loading...")

        def render(request: gr.Request):
            user = request.session.get("user")
            if user:
                return f"👋 Hello {user.get('name')}!\n\n[Logout](/logout)"
            else:
                return "🔒 You are not logged in. [Login](/login)"

        # must pass lists
        demo.load(fn=render, inputs=[], outputs=[msg])
    return demo
