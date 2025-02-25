from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.auth_handler import AuthHandler
from app.models.models import UserLogin, UserResponse
from typing import Dict, Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
auth_handler = AuthHandler()

# Store users in memory for demo (replace with database in production)
users = {}

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register")
async def register(user_data: UserLogin):
    if user_data.username in users:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_password = auth_handler.get_password_hash(user_data.password)
    users[user_data.username] = hashed_password
    
    return {"message": "User registered successfully"}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username not in users or not auth_handler.verify_password(
        form_data.password, users[form_data.username]
    ):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    token = auth_handler.encode_token(form_data.username)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/chat")
async def chat(message: str, current_user: str = Depends(auth_handler.verify_token)):
    # Simple echo response for testing
    return {"response": f"Received message: {message}"}

# Optional test endpoint
@app.get("/")
async def root():
    return {"message": "API is running"}