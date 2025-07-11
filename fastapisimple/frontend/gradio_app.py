import gradio as gr
import requests
import os

# Backend API URL
BACKEND_URL = os.getenv('BACKEND_URL', 'http://backend:8000')

def chat_with_backend(message, history):
    """
    Send message to FastAPI backend and return response
    """
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={"message": message},
            timeout=30
        )
        
        if response.status_code == 200:
            response_text = response.json().get("response", "No response")
            return response_text
        else:
            return f"Backend error: {response.status_code}"
            
    except Exception as e:
        return f"Connection failed: {str(e)}"

# Create simple Gradio ChatInterface
demo = gr.ChatInterface(
    fn=chat_with_backend,
    title="Chat with AWS Bedrock",
    retry_btn=None,
    undo_btn=None,
    clear_btn="Clear Chat",
)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,  # Gradio default port
        share=False
    )
