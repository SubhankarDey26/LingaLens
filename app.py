from flask import Flask, request, jsonify
from flask_cors import CORS
import pytesseract
from PIL import Image
from googletrans import Translator
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set Tesseract path (update this path for your system)
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\KIIT\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_text(text, target_language):
    try:
        translator = Translator()
        translation = translator.translate(text, dest=target_language)
        return translation.text
    except Exception as e:
        return str(e)

@app.route('/translate', methods=['POST'])
def translate():
    try:
        if 'text' in request.form:
            # Handle direct text input
            text = request.form['text']
            target_language = request.form['language']
            translated_text = process_text(text, target_language)
            return jsonify({
                'original_text': text,
                'translated_text': translated_text
            })
            
        elif 'image' in request.files:
            # Handle image upload
            file = request.files['image']
            target_language = request.form['language']
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Perform OCR
                img = Image.open(filepath)
                extracted_text = pytesseract.image_to_string(img)
                
                # Translate extracted text
                translated_text = process_text(extracted_text, target_language)
                
                # Clean up - delete uploaded file
                os.remove(filepath)
                
                return jsonify({
                    'original_text': extracted_text,
                    'translated_text': translated_text
                })
                
        return jsonify({'error': 'No text or image provided'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)