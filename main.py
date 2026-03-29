from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Dhan-I Backend", description="AI-powered Cognitive Financial Twin")

# Enable CORS for localhost:3000 and the Vercel frontend domain
origins = [
    "http://localhost:3000",
    "https://dhan-i.vercel.app",  # Production Vercel URL placeholder
    "*" # Wildcard fallback for Hackathon demo purposes just in case
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from data_pipeline.bronze import router as bronze_router
app.include_router(bronze_router, tags=["Pipeline"])

from api.routes import router as logic_router
app.include_router(logic_router, tags=["LangGraph"])



@app.get("/")
def read_root():
    return {"status": "healthy", "service": "Dhan-I API"}

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

