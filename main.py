# main.py
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from processor import run_processor
import uuid

app = Flask(__name__)
CORS(app)

@app.route('/process_excel', methods=['POST'])
def process_excel():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    session_id = str(uuid.uuid4())
    input_dir = f'temp/input_{session_id}'
    output_dir = f'temp/output_{session_id}'

    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    filepath = os.path.join(input_dir, file.filename)
    file.save(filepath)

    try:
        zip_path = run_processor(filepath, output_dir)
        return send_file(zip_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs('temp', exist_ok=True)
    app.run(host='0.0.0.0', port=10000)
