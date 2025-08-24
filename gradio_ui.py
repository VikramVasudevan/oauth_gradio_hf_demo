import gradio as gr
import starlette

def greet(request : gr.Request):
    return f"Hello {request.username}!"

def main_app():
    with gr.Blocks() as app:
        logged_in_user = gr.State()
        with gr.Row():
            gr.Markdown("## Welcome!")

        # Check user session dynamically
        @gr.render(inputs=logged_in_user)
        def render_app(user):
            if user:
                container = secured_app()
            else:
                container = login_page()
        
        def get_user(request: gr.Request):
            print("***** request.username = ", request.username)
            if(isinstance(request.username, str)):
                return request.username
            elif(isinstance(request.username, starlette.responses.RedirectResponse)):
                print("Probably redirected from logout flow?")
                return None
            else:
                return None

        gr.on(fn=get_user, outputs=logged_in_user)
    return app

def secured_app():
    with gr.Column() as container:
        gr.Markdown("## This is a protected Gradio App!")
        name_input = gr.Textbox(label="Your Name")
        logout_btn = gr.Button("Logout", link="/logout")
        gr.on(fn=greet, outputs=name_input)
    return container


def login_page():
    with gr.Column() as container:
        gr.Markdown("## You are not logged in")
        login_btn = gr.Button("Login", link="/login")
    return container
