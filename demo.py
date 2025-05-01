import os
from redaction_pipeline2 import RedactionPipeline
from web_text_redactor import app as flask_app
from webpage_redactor import WebpageRedactor
from img_paddle_ocr import extract_text
from audio_red2 import AudioRedactor

def demo_text_redaction():
    print("\n=== Text Redaction Demo ===")
    pipeline = RedactionPipeline()
    text = "Can you write an email to notify HR that John D'Souza (Emp ID: 00723) is resigning effective June 1st. His contact is john.dsouza@thalesgroup.com and phone is +91 98765 43210."
    result = pipeline.run_pipeline(text)
    print("Original text:", text)
    print("Redacted text:", result["llm_output"])
    print("Detected entities:", result["redaction_summary"])

def demo_webpage_redaction():
    print("\n=== Webpage Redaction Demo ===")
    redactor = WebpageRedactor()
    url = "https://example.com"  # Replace with your target URL
    try:
        text = redactor.redact_webpage(url)
        pipeline = RedactionPipeline()
        result = pipeline.run_pipeline(text)
        print("Redacted webpage content:", result["llm_output"])
    except Exception as e:
        print(f"Error redacting webpage: {e}")

def demo_image_redaction():
    print("\n=== Image Redaction Demo ===")
    image_path = "resume.png"  # Replace with your image path
    try:
        text = extract_text(image_path)
        pipeline = RedactionPipeline()
        result = pipeline.run_pipeline(text)
        print("Redacted image text:", result["llm_output"])
    except Exception as e:
        print(f"Error redacting image: {e}")

def demo_audio_redaction():
    print("\n=== Audio Redaction Demo ===")
    audio_file = "Recording (3).m4a"  # Replace with your audio file
    try:
        redactor = AudioRedactor()
        output_path, transcript_text = redactor.redact_audio(audio_file)
        pipeline = RedactionPipeline()
        result = pipeline.run_pipeline(transcript_text)
        print("Redacted audio transcript:", result["llm_output"])
    except Exception as e:
        print(f"Error redacting audio: {e}")

def run_flask_app():
    print("\n=== Starting Flask Web Interface ===")
    print("Visit http://localhost:5000 to use the web interface")
    flask_app.run(debug=True)

if __name__ == "__main__":
    # Run all demos
    demo_text_redaction()
    demo_webpage_redaction()
    demo_image_redaction()
    demo_audio_redaction()
    
    # Uncomment to run the Flask web interface
    # run_flask_app() 