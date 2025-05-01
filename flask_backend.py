from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
import time
import whisper
from paddleocr import PaddleOCR
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Gemini
GOOGLE_API_KEY = "AIzaSyCePl8wfB1sKqH2fOyRk1TytdluP99_uo0"
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Gemini model with safety settings
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
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
    },
]

# Initialize all models
try:
    # Initialize Gemini
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        safety_settings=safety_settings
    )
    print("✅ Gemini model initialized")

    # Initialize Whisper for audio
    whisper_model = whisper.load_model("base")
    print("✅ Whisper model initialized")

    # Initialize PaddleOCR for images
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    print("✅ PaddleOCR model initialized")

    logger.info("All models initialized successfully")

except Exception as e:
    logger.error(f"Error initializing models: {str(e)}")
    model = None
    whisper_model = None
    ocr = None

def get_fallback_response(message):
    """
    Generate a fallback response when Gemini API is not available
    """
    message = message.lower()
    
    # Basic response patterns
    if any(greeting in message for greeting in ["hello", "hi", "hey", "hy"]):
        return "Hello! How can I help you today?"
    elif "how are you" in message:
        return "I'm doing well, thank you for asking! How can I assist you?"
    elif "bye" in message or "goodbye" in message:
        return "Goodbye! Have a great day!"
    elif "python" in message or "code" in message:
        return """Here's a simple Python example:

```python
def greet(name):
    return f"Hello, {name}!"

# Example usage
print(greet("User"))
```

Would you like me to explain how this code works?"""
    elif "help" in message:
        return "I can help you with various tasks, including writing Python code, answering questions, and more. Just let me know what you need!"
    else:
        return "I understand your message. How can I help you with that?"

def get_gemini_response(prompt):
    """
    Get response from Gemini LLM with fallback to basic responses
    """
    if model is None:
        return get_fallback_response(prompt)
    
    try:
        response = model.generate_content(prompt)
        if response.text:
            return response.text
        else:
            return get_fallback_response(prompt)
    except Exception as e:
        print(f"Error getting response from Gemini: {str(e)}")
        # If we hit rate limits or other API errors, use fallback
        return get_fallback_response(prompt)

def process_audio(audio_file):
    """Process audio file using Whisper"""
    try:
        if whisper_model is None:
            return "Audio processing model not available."
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            audio_file.save(temp_file.name)
            temp_path = temp_file.name

        # Transcribe audio
        result = whisper_model.transcribe(temp_path)
        os.unlink(temp_path)  # Clean up temp file
        
        return result["text"]
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        return f"Error processing audio: {str(e)}"

def process_image(image_file):
    """Process image using PaddleOCR"""
    try:
        if ocr is None:
            return "Image processing model not available."
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            image_file.save(temp_file.name)
            temp_path = temp_file.name

        # Extract text from image
        result = ocr.ocr(temp_path, cls=True)
        os.unlink(temp_path)  # Clean up temp file
        
        # Extract text from OCR result
        extracted_text = ""
        if result and result[0]:
            for line in result[0]:
                extracted_text += line[1][0] + "\n"
        
        return extracted_text.strip()
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return f"Error processing image: {str(e)}"

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Endpoint to process chat messages and return a response using Gemini.
    """
    try:
        # Get the message from the request
        data = request.json
        message = data.get('message', '')
        
        # Log the received message (for debugging)
        print(f"Received message: {message}")
        
        # Process the message and generate a response
        if not message:
            return jsonify({"response": "I didn't receive any message. Please try again."})
        
        # Get response from Gemini or fallback
        response = get_gemini_response(message)
        
        return jsonify({"response": response})
            
    except Exception as e:
        logger.error(f"Error in /api/chat: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Endpoint to handle file uploads (images, audio).
    """
    try:
        # Get the file and message
        file = request.files.get('file')
        message = request.form.get('message', '')
        file_type = request.form.get('type', '')
        
        if not file or not file_type:
            return jsonify({"response": "No file or type provided. Please try again."})
        
        print(f"Received {file_type} file: {file.filename}, Message: {message}")
        
        # Process file based on type
        if file_type == 'audio':
            extracted_text = process_audio(file)
        elif file_type == 'image':
            extracted_text = process_image(file)
        else:
            return jsonify({"response": "Unsupported file type. Please upload an audio or image file."})
        
        # Create prompt for Gemini
        prompt = f"""
        I received a {file_type} file. Here's the extracted content:
        {extracted_text}
        
        User's message: {message}
        
        Please analyze this content and provide a helpful response.
        """
        
        # Get response from Gemini
        response = get_gemini_response(prompt)
        
        return jsonify({
            "response": response,
            "extracted_text": extracted_text
        })
            
    except Exception as e:
        logger.error(f"Error in /api/upload: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/webpage', methods=['POST'])
def process_webpage():
    try:
        data = request.json
        url = data.get('url', '')
        message = data.get('message', '')

        if not url:
            return jsonify({'error': 'No URL provided'}), 400

        # For now, just acknowledge the URL and return a message
        return jsonify({
            'message': f'Received URL: {url}. Webpage processing will be implemented soon.',
            'status': 'success'
        })

    except Exception as e:
        logger.error(f"Error in webpage endpoint: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

if __name__ == '__main__':
    print("Starting Flask backend on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)