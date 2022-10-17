from flask import Flask, request, jsonify, send_file, render_template_string
from werkzeug.utils import secure_filename
from anpr import licensePlateRecognition
from encoded_img import getImage
from flask_cors import CORS
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'uploads')

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return render_template_string('<h1>Server is Available 🙌!</h1>')

@app.route('/file_upload', methods=['POST'])
def fileUpload():
    try:
        # check if the post request has the file part
        if 'file' not in request.files:
            resp = jsonify({'message' : 'No file part in the request'})
            resp.status_code = 400
            return resp
        # Get File
        file = request.files['file']
        
        if file.filename == '':
            resp = jsonify({'message' : 'No file selected for uploading'})
            resp.status_code = 400
            return resp
        
        if file:
            filename = secure_filename(file.filename)
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(img_path)

            license_num, thresh_path = licensePlateRecognition(img_path)
            # encodedImg = getImage(thresh_path)
            
            resp = jsonify({
                'message' : 'File successfully uploaded', 
                'platenumber': license_num,
            })
            resp.status_code = 201
            return resp
        else:
            resp = jsonify({'message' : 'Error in file upload!'})
            resp.status_code = 400
            return resp

    except Exception as err:
        resp = jsonify({'message' : 'Error in file upload!', 'error': f'{err}'})
        resp.status_code = 500
        return resp

@app.route('/files/<platenumber>', methods=['GET'])
def getFiles(platenumber):
    try:
        file = send_file(f'uploads/{platenumber}')
    except FileNotFoundError:     
        errType = 'File not Found!'
        resp = jsonify({
            'message': errType,
            'status': 500})
        return resp
    return file

@app.route('/threshold/<threshold>', methods=['GET'])
def getThreshold(threshold):
    try:
        file = send_file(f'threshold/{threshold}')
    except FileNotFoundError:     
        errType = 'File not Found!'
        resp = jsonify({
            'message': errType,
            'status': 500})
        return resp
    return file

if __name__ == "__main__":
    app.run(debug = False, port = 5000, threaded = True)
