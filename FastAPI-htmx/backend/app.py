from fastapi import FastAPI, HTTPException, APIRouter, Request, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import boto3
import os
from typing import Optional

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

# Create API v1 router
v1_router = APIRouter(prefix="/api/v1")

@v1_router.post("/chat")
async def chat_api(request: Request, chat_message: Optional[ChatMessage] = None, message: Optional[str] = Form(None)):
    try:
        # Determine if this is HTMX form submission or JSON API call
        is_htmx = request.headers.get("hx-request") == "true"
        content_type = request.headers.get("content-type", "")
        
        # Get message from either JSON body or form data
        user_message = ""
        if message:  # Form data
            user_message = message
        elif chat_message:  # JSON data
            user_message = chat_message.message
        else:
            # Try to get from request body if neither worked
            if "application/json" in content_type:
                body = await request.json()
                user_message = body.get("message", "")
        
        if not user_message or not user_message.strip():
            if is_htmx:
                return templates.TemplateResponse("error.html", {
                    "request": request,
                    "error": "Message cannot be empty"
                })
            else:
                raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
        
        conversation = [
            {
                "role": "user",
                "content": [{"text": user_message}]
            }
        ]
        
        response = bedrock_client.converse(
            modelId=model_id,
            messages=conversation,
            inferenceConfig={
                "maxTokens": 1000,
                "temperature": 0.7
            }
        )
        
        response_text = response['output']['message']['content'][0]['text']
        
        # Return appropriate response based on request type
        if is_htmx:
            return templates.TemplateResponse("chat_messages.html", {
                "request": request,
                "user_message": user_message,
                "ai_response": response_text
            })
        else:
            return ChatResponse(response=response_text)
        
    except Exception as e:
        if is_htmx:
            return templates.TemplateResponse("error.html", {
                "request": request,
                "error": str(e)
            })
        else:
            raise HTTPException(status_code=500, detail=str(e))

# Main chat interface endpoint
@app.get("/chat", response_class=HTMLResponse)
async def chat_interface(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Include the v1 router in the main app
app.include_router(v1_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
