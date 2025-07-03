from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import os
from ai_image import analyze_fishing_spot
from catch_logger import CatchLogger
from forecast import get_fishing_forecast

app = FastAPI(title="FishCast AI - Fishing Assistant API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize catch logger
catch_logger = CatchLogger()

class CatchEntry(BaseModel):
    species: str
    bait: str
    location: str
    date: str
    time: str
    notes: Optional[str] = ""

class ForecastRequest(BaseModel):
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

@app.get("/")
async def read_root():
    """Serve the main FishCast AI application"""
    return FileResponse('static/index.html')

@app.post("/api/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """
    Analyze a fishing spot image using Google AI Studio (Gemini)
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image bytes
        image_bytes = await file.read()
        
        # Validate file size (max 10MB)
        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image too large (max 10MB)")
        
        # Analyze the image
        analysis = analyze_fishing_spot(image_bytes)
        
        return JSONResponse(content={
            "success": True,
            "recommendation": analysis,
            "filename": file.filename,
            "api_provider": "Google AI Studio (Gemini)"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in analyze endpoint: {str(e)}")
        return JSONResponse(
            status_code=500, 
            content={
                "success": False,
                "error": f"Analysis failed: {str(e)}"
            }
        )

@app.post("/api/catches")
async def log_catch(catch_entry: CatchEntry):
    try:
        result = catch_logger.add_catch(catch_entry.dict())
        return {"message": f"Catch logged successfully! Total catches: {len(catch_logger.get_all_catches())}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/catches")
async def get_catches():
    try:
        catches = catch_logger.get_all_catches()
        return catches
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/forecast")
async def fishing_forecast(request: ForecastRequest):
    try:
        forecast = get_fishing_forecast(request.location, request.latitude, request.longitude)
        return forecast
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    api_key = os.getenv("GEMINI_API_KEY")
    api_configured = bool(api_key and api_key != "your_gemini_api_key_here")
    
    return {
        "status": "healthy", 
        "service": "FishCast AI",
        "ai_provider": "Google AI Studio (Gemini)",
        "api_configured": api_configured
    }

@app.get("/api/status")
async def api_status():
    """API configuration status for frontend"""
    api_key = os.getenv("GEMINI_API_KEY")
    api_configured = bool(api_key and api_key != "your_gemini_api_key_here")
    
    return {
        "api_configured": api_configured,
        "message": "✅ Ready to analyze fishing spots!" if api_configured else "❌ Please configure GEMINI_API_KEY",
        "setup_url": "https://aistudio.google.com/app/apikey" if not api_configured else None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
