import os
import base64
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def analyze_fishing_spot(image_bytes):
    """
    Analyze a fishing spot image using Google AI Studio (Gemini) API
    """
    try:
        # Get API key from environment
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            return """Error: GEMINI_API_KEY not configured properly. 

To fix this:
1. Go to https://aistudio.google.com/app/apikey
2. Create a free API key
3. Add it to your .env file: GEMINI_API_KEY=your_actual_api_key
4. Restart the application

The free tier includes generous limits for testing."""
        
        # Convert image bytes to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Create the fishing-specific prompt as requested
        fishing_prompt = "Based on this fishing spot image, where should I cast my line? Consider shade, visible cover, and fish-holding structure."

        # Try Gemini 2.5 Pro first, then fallback to Flash
        models_to_try = [
            "gemini-2.5-pro",
            "gemini-2.5-flash"
        ]
        
        analysis_result = None
        
        for model in models_to_try:
            try:
                # Prepare the API request
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        
                headers = {
                    'Content-Type': 'application/json',
                    'X-goog-api-key': api_key
                }
                
                # Prepare the request payload
                payload = {
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": fishing_prompt
                                },
                                {
                                    "inline_data": {
                                        "mime_type": "image/jpeg",
                                        "data": image_base64
                                    }
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.7,
                        "topK": 40,
                        "topP": 0.95,
                        "maxOutputTokens": 1000
                    },
                    "safetySettings": [
                        {
                            "category": "HARM_CATEGORY_HARASSMENT",
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        },
                        {
                            "category": "HARM_CATEGORY_HATE_SPEECH",
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        },
                        {
                            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        },
                        {
                            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                        }
                    ]
                }
                
                # Make the API call
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                # Check if request was successful
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract the generated text
                    if 'candidates' in result and len(result['candidates']) > 0:
                        candidate = result['candidates'][0]
                        if 'content' in candidate and 'parts' in candidate['content']:
                            analysis = candidate['content']['parts'][0]['text']
                            return f"[Using {model}] {analysis}"
                        elif 'finishReason' in candidate and candidate['finishReason'] == 'SAFETY':
                            return "The image was blocked by safety filters. Please try a different fishing spot image."
                        else:
                            return "Error: Unexpected response format from Google AI Studio API."
                    else:
                        return "Error: No analysis generated. The image might not be suitable for analysis or was filtered for safety reasons."
                        
                elif response.status_code == 404:
                    # Model not available, try next one
                    print(f"Model {model} not available, trying next...")
                    continue
                    
                elif response.status_code == 429:
                    return """Error: API quota exceeded. 

You have reached the free tier limit for Google AI Studio. The free tier includes:
- 15 requests per minute
- 1,500 requests per day
- 1 million tokens per day

Please wait a few minutes and try again, or come back tomorrow for your daily quota to reset."""
                    
                elif response.status_code == 400:
                    try:
                        error_detail = response.json().get('error', {}).get('message', 'Bad request')
                    except:
                        error_detail = 'Invalid request format'
                    return f"Error: Invalid request to Google AI Studio API. {error_detail}"
                    
                elif response.status_code == 403:
                    return """Error: API key is invalid or doesn't have permission. 

Please check:
1. Your GEMINI_API_KEY in the .env file is correct
2. The API key is enabled for the Gemini API
3. You haven't exceeded your quota limits

Get a new API key at: https://aistudio.google.com/app/apikey"""
                    
                else:
                    try:
                        error_info = response.json()
                        print(f"Model {model} failed with status {response.status_code}: {error_info}")
                        continue
                    except:
                        print(f"Model {model} failed with status {response.status_code}")
                        continue
                        
            except requests.exceptions.Timeout:
                print(f"Model {model} timed out, trying next...")
                continue
                
            except requests.exceptions.ConnectionError:
                print(f"Connection error with model {model}, trying next...")
                continue
                
            except Exception as e:
                print(f"Error with model {model}: {str(e)}, trying next...")
                continue
        
        # If we get here, all models failed
        return "Error: All Gemini models failed. Please try again later or check your API configuration."
        
    except requests.exceptions.Timeout:
        return "Error: Request to Google AI Studio API timed out. Please try again."
        
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to Google AI Studio API. Please check your internet connection."
        
    except json.JSONDecodeError:
        return "Error: Invalid response from Google AI Studio API. Please try again."
        
    except Exception as e:
        print(f"Error analyzing image: {str(e)}")
        return f"Sorry, I couldn't analyze this image right now. Error: {str(e)}"
