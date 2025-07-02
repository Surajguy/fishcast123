# 🎣 FishCast API

A FastAPI backend for a fishing assistant app that uses Google's Gemini 2.5 AI to analyze fishing spot images and provide casting advice.

## Features

- **Image Analysis**: Upload fishing spot photos and get AI-powered casting recommendations
- **Gemini 2.5 Integration**: Uses Google AI Studio API with fallback between Pro and Flash models
- **Modular Design**: Clean, maintainable code structure
- **Error Handling**: Comprehensive error handling and user-friendly messages
- **Additional Tools**: Catch logging and fishing forecast features

## Quick Start

### 1. Setup Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd fishcast123

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 2. Get Google AI Studio API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a free API key
3. Add it to your `.env` file:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

### 3. Run the Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### 🖼️ Image Analysis
**POST** `/api/analyze`

Upload a fishing spot image and get casting advice.

**Request**: Multipart form data with image file
**Response**: JSON with casting recommendations

Example using curl:
```bash
curl -X POST "http://localhost:8000/api/analyze" \
     -F "file=@fishing_spot.jpg"
```

### 🏥 Health Check
**GET** `/health`

Check API status and configuration.

### 📝 Catch Logging
**POST** `/api/catches` - Log a new catch
**GET** `/api/catches` - Get all logged catches

### 🌤️ Fishing Forecast
**POST** `/api/forecast` - Get fishing forecast for a location

## Testing

Use the included test script:

```bash
python test_api.py
```

## How It Works

1. **Image Upload**: The `/api/analyze` endpoint accepts image uploads via multipart form data
2. **Base64 Conversion**: Images are converted to base64 format for the Gemini API
3. **AI Analysis**: The image and prompt are sent to Gemini 2.5 (Pro first, then Flash as fallback)
4. **Response**: Natural language casting advice is returned based on visible cover, shade, and structure

## Prompt Used

The AI receives this specific prompt along with your image:

> "Based on this fishing spot image, where should I cast my line? Consider shade, visible cover, and fish-holding structure."

## Error Handling

The API handles various scenarios:
- Invalid file types
- File size limits (10MB max)
- API quota exceeded
- Invalid API keys
- Model availability issues
- Network timeouts

## Free Tier Limits

Google AI Studio free tier includes:
- 15 requests per minute
- 1,500 requests per day  
- 1 million tokens per day

## Tech Stack

- **FastAPI**: Modern Python web framework
- **Google Gemini 2.5**: AI image analysis (Pro/Flash models)
- **Python-multipart**: File upload handling
- **Requests**: HTTP client for API calls
- **Python-dotenv**: Environment variable management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Add your license here]
