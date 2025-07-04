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

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main FishCast AI application"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎣 FishCast AI - Smart Fishing Assistant</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
            color: white;
        }

        .header h1 {
            font-size: 3.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            animation: fadeInDown 1s ease-out;
        }

        .header p {
            font-size: 1.3rem;
            opacity: 0.9;
            animation: fadeInUp 1s ease-out 0.3s both;
        }

        .main-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            animation: fadeInUp 1s ease-out 0.6s both;
        }

        .upload-section {
            text-align: center;
            margin-bottom: 40px;
        }

        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 60px 20px;
            background: linear-gradient(45deg, #f8f9ff, #e8f0ff);
            transition: all 0.3s ease;
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }

        .upload-area:hover {
            border-color: #5a67d8;
            background: linear-gradient(45deg, #f0f4ff, #dde7ff);
            transform: translateY(-2px);
        }

        .upload-area.dragover {
            border-color: #4c51bf;
            background: linear-gradient(45deg, #e6f3ff, #cce7ff);
            transform: scale(1.02);
        }

        .upload-icon {
            font-size: 4rem;
            color: #667eea;
            margin-bottom: 20px;
            animation: bounce 2s infinite;
        }

        .upload-text {
            font-size: 1.2rem;
            color: #4a5568;
            margin-bottom: 15px;
        }

        .upload-subtext {
            color: #718096;
            font-size: 0.9rem;
        }

        .file-input {
            display: none;
        }

        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 50px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }

        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .preview-section {
            display: none;
            margin: 30px 0;
            text-align: center;
        }

        .image-preview {
            max-width: 100%;
            max-height: 400px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }

        .results-section {
            display: none;
            margin-top: 40px;
        }

        .results-card {
            background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
            border-radius: 15px;
            padding: 30px;
            border-left: 5px solid #667eea;
        }

        .results-title {
            font-size: 1.5rem;
            color: #2d3748;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .results-content {
            font-size: 1.1rem;
            line-height: 1.8;
            color: #4a5568;
            white-space: pre-wrap;
        }

        .loading {
            display: none;
            text-align: center;
            margin: 30px 0;
        }

        .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid #e2e8f0;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        .error {
            background: linear-gradient(135deg, #fed7d7 0%, #feb2b2 100%);
            color: #c53030;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 5px solid #e53e3e;
        }

        .success {
            background: linear-gradient(135deg, #c6f6d5 0%, #9ae6b4 100%);
            color: #2f855a;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 5px solid #38a169;
        }

        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 30px;
            margin-top: 50px;
        }

        .feature-card {
            background: rgba(255, 255, 255, 0.9);
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }

        .feature-card:hover {
            transform: translateY(-5px);
        }

        .feature-icon {
            font-size: 3rem;
            color: #667eea;
            margin-bottom: 20px;
        }

        .feature-title {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 15px;
            color: #2d3748;
        }

        .feature-desc {
            color: #718096;
            line-height: 1.6;
        }

        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% {
                transform: translateY(0);
            }
            40% {
                transform: translateY(-10px);
            }
            60% {
                transform: translateY(-5px);
            }
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 2.5rem;
            }
            
            .main-card {
                padding: 20px;
                margin: 10px;
            }
            
            .upload-area {
                padding: 40px 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-fish"></i> FishCast AI</h1>
            <p>AI-Powered Fishing Assistant - Find the Perfect Casting Spot</p>
        </div>

        <div class="main-card">
            <div class="upload-section">
                <div class="upload-area" id="uploadArea">
                    <div class="upload-icon">
                        <i class="fas fa-cloud-upload-alt"></i>
                    </div>
                    <div class="upload-text">
                        Drop your fishing spot photo here
                    </div>
                    <div class="upload-subtext">
                        or click to browse (JPG, PNG, GIF up to 10MB)
                    </div>
                    <input type="file" id="fileInput" class="file-input" accept="image/*">
                </div>
                
                <div class="preview-section" id="previewSection">
                    <img id="imagePreview" class="image-preview" alt="Preview">
                    <div>
                        <button class="btn" id="analyzeBtn">
                            <i class="fas fa-search"></i> Analyze Fishing Spot
                        </button>
                    </div>
                </div>
            </div>

            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>🤖 AI is analyzing your fishing spot...</p>
            </div>

            <div class="results-section" id="resultsSection">
                <div class="results-card">
                    <div class="results-title">
                        <i class="fas fa-bullseye"></i>
                        Casting Recommendations
                    </div>
                    <div class="results-content" id="resultsContent"></div>
                </div>
            </div>
        </div>

        <div class="features">
            <div class="feature-card">
                <div class="feature-icon">
                    <i class="fas fa-eye"></i>
                </div>
                <div class="feature-title">AI Vision Analysis</div>
                <div class="feature-desc">Advanced computer vision identifies water structures, cover, and optimal fishing zones</div>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">
                    <i class="fas fa-crosshairs"></i>
                </div>
                <div class="feature-title">Precision Targeting</div>
                <div class="feature-desc">Get specific casting recommendations based on shade, cover, and fish-holding structures</div>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">
                    <i class="fas fa-brain"></i>
                </div>
                <div class="feature-title">Expert Knowledge</div>
                <div class="feature-desc">Powered by Google's Gemini AI with extensive fishing expertise and pattern recognition</div>
            </div>
        </div>
    </div>

    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const previewSection = document.getElementById('previewSection');
        const imagePreview = document.getElementById('imagePreview');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const loading = document.getElementById('loading');
        const resultsSection = document.getElementById('resultsSection');
        const resultsContent = document.getElementById('resultsContent');

        // File upload handling
        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('dragleave', handleDragLeave);
        uploadArea.addEventListener('drop', handleDrop);
        fileInput.addEventListener('change', handleFileSelect);
        analyzeBtn.addEventListener('click', analyzeImage);

        function handleDragOver(e) {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        }

        function handleDragLeave(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        }

        function handleDrop(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        }

        function handleFileSelect(e) {
            const file = e.target.files[0];
            if (file) {
                handleFile(file);
            }
        }

        function handleFile(file) {
            if (!file.type.startsWith('image/')) {
                showError('Please select an image file (JPG, PNG, GIF)');
                return;
            }

            if (file.size > 10 * 1024 * 1024) {
                showError('File size must be less than 10MB');
                return;
            }

            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.src = e.target.result;
                previewSection.style.display = 'block';
                resultsSection.style.display = 'none';
                clearMessages();
            };
            reader.readAsDataURL(file);
        }

        async function analyzeImage() {
            const file = fileInput.files[0];
            if (!file) {
                showError('Please select an image first');
                return;
            }

            loading.style.display = 'block';
            resultsSection.style.display = 'none';
            analyzeBtn.disabled = true;
            clearMessages();

            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    showResults(result.recommendation);
                    showSuccess('Analysis complete! Check out your casting recommendations below.');
                } else {
                    showError(result.error || 'Analysis failed. Please try again.');
                }
            } catch (error) {
                showError('Network error. Please check your connection and try again.');
                console.error('Error:', error);
            } finally {
                loading.style.display = 'none';
                analyzeBtn.disabled = false;
            }
        }

        function showResults(recommendation) {
            resultsContent.textContent = recommendation;
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }

        function showError(message) {
            clearMessages();
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error';
            errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
            previewSection.appendChild(errorDiv);
        }

        function showSuccess(message) {
            clearMessages();
            const successDiv = document.createElement('div');
            successDiv.className = 'success';
            successDiv.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
            previewSection.appendChild(successDiv);
        }

        function clearMessages() {
            const messages = document.querySelectorAll('.error, .success');
            messages.forEach(msg => msg.remove());
        }
    </script>
</body>
</html>
    """

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
