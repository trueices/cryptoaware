from fastapi import FastAPI
from app.api.routers import chat

app = FastAPI()

# Include your routers #
app.include_router(chat.router, tags=["chat"])

# Check the connection #
@app.get("/")
async def root():
    return {"Seccessfully connected!"}
