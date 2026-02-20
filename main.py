import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.routes import analysis, health

app = FastAPI(
    title="PharmaGuard API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(analysis.router, prefix="/api", tags=["Analysis"])

# FRONTEND CONNECTION
# Ye line 'Frontend' folder ki files ko connect karegi
if os.path.exists("Frontend"):
    app.mount("/Frontend", StaticFiles(directory="Frontend"), name="Frontend")

# Home route jo index.html dikhayega
@app.get("/")
async def serve_frontend():
    return FileResponse("Frontend/index.html")