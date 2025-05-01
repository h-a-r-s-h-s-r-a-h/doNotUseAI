from flask import Flask, render_template, request, jsonify
from redaction_pipeline2 import RedactionPipeline
import os

app = Flask(__name__)
pipeline = RedactionPipeline()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/redact', methods=['POST'])
def redact_text():
    try:
        data = request.get_json()
        text = data.get('text', '')
        feedback = data.get('feedback', None)
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
            
        result = pipeline.run_pipeline(text, feedback=feedback)
        
        return jsonify({
            'success': True,
            'redacted_text': result['llm_output'],
            'entities': result['redacted_entities'],
            'summary': result['redaction_summary']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 