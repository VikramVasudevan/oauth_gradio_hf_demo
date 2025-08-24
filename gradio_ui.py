import gradio as gr

def greet(request : gr.Request):
    return f"Hello {request.username}!"

def login_required_app():
    with gr.Blocks() as app:
        gr.Markdown("## This is a protected Gradio App!")
        name_input = gr.Textbox(label="Your Name")
        output = gr.Textbox(label="Greeting")
        name_input.submit(fn=greet, inputs=name_input, outputs=output)
        logout_btn = gr.Button("Logout", link="/logout")
        gr.on(fn=greet, inputs=None, outputs=name_input)
    return app


def login_page():
    with gr.Blocks() as app:
        gr.Markdown("## You are not logged in")
        login_btn = gr.Button("Login", link="/login")
    return app
