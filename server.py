from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    messages: list
    system: str = ""
    temperature: float = 0.7
    top_p: float = 0.9

@app.post("/chat")
async def chat(req: ChatRequest):
    payload = {
        "model": "persona-weave",
        "stream": False,
        "options": {
            "temperature": req.temperature,
            "top_p": req.top_p,
            "num_predict": 150,        # limit tokens for speed
        },
        "messages": [
            {"role": "system", "content": req.system},
            *req.messages,
        ],
    }
    async with httpx.AsyncClient(timeout=300) as client:
        res = await client.post("http://localhost:11434/api/chat", json=payload)
        data = res.json()
    return {"reply": data["message"]["content"]}