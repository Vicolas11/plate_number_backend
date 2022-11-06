from flask import Flask, redirect, request, jsonify, send_file, render_template_string
from werkzeug.utils import secure_filename
from anpr import licensePlateRecognition
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.sql import func
from datetime import datetime
from database import Vehicle
from utils import removeFiles
from flask_cors import CORS
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
THRESH_FOLDER = os.path.join(PROJECT_ROOT, 'threshold')
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'uploads')

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(PROJECT_ROOT, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

# Settings for migrations
migrate = Migrate(app, db)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.String, unique=True, nullable=False)
    platenum = db.Column(db.String, unique=True, nullable=False)
    model = db.Column(db.String, unique=True, nullable=False)
    date = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"Vehicle: {self.platenum}"

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
            time_stramp = f"{datetime.timestamp(datetime.now())}".split(".")[0]
            file_name = filename.split('.')[0]
            ext = filename.split('.')[1]
            file_path = f"{file_name}{time_stramp}.{ext}"
            status = removeFiles(UPLOAD_FOLDER, THRESH_FOLDER)
            if status:
                img_path = os.path.join(app.config['UPLOAD_FOLDER'], file_path)
                file.save(img_path)

                license_num, thresh_path = licensePlateRecognition(img_path)
                # encodedImg = getImage(thresh_path)

                # Get Data from the dbase
                data = Vehicle.query.filter_by(platenum=license_num).first()
                if data:
                    dt_custom = data.date
                    dt = dt_custom.strftime("%d %B, %Y")
                    values = {
                        'owner': data.owner, 
                        'platenum': data.platenum, 
                        'model': data.model,
                        'date': dt
                    }                    
                    resp = jsonify({
                        'message' : 'File successfully uploaded',
                        'threshold': thresh_path,
                        'file': f'files/{file_path}',
                        'data': values,
                    })
                    resp.status_code = 201
                    return resp
                else:
                    values = {
                        'owner': None, 
                        'platenum': license_num, 
                        'model': None,
                        'date': None
                    }
                    resp = jsonify({
                        'message' : 'File successfully uploaded',
                        'threshold': thresh_path,
                        'file': f'files/{file_path}',
                        'data': values,
                    })
                    resp.status_code = 201
                    return resp
            else:
                resp = jsonify({'message' : 'Error in file deleting!'})
                resp.status_code = 400
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

@app.route('/add', methods=["GET","POST"])
def add_vehicle():
    p = Vehicle(owner="Jimmy Fox", platenum="LKJ935AE", model="TOYOTA")
    db.session.add(p)
    db.session.commit()
    return redirect('/')

@app.route('/fetched', methods=["GET"])
def vehicles():
    try:
        vehicle = vehicle.query.all()
        print(vehicle)
        resp = jsonify({'vehicle': f'${vehicle}'})    
        resp.status_code = 200
        return resp
    except Exception as err:
        print("ERROR ==> ", err)

if __name__ == "__main__":
    app.run(debug = False, port = 5000, threaded = True)
