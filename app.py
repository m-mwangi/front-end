from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import requests
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["ALLOWED_EXTENSIONS"] = {"csv"}
app.secret_key = "your_secret_key"  # Required for flash messages
FASTAPI_PREDICT_URL = "https://matern-ai-1.onrender.com/predict"
FASTAPI_TRAIN_URL = "https://matern-ai-1.onrender.com/retrain"
RENDER_URL = "https://matern-ai-1.onrender.com"
# Ensure upload directory exists
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    prediction_message = None
    form_data = {}

    if request.method == 'POST':
        form_data = request.form.to_dict()

        try:
            # Convert form data to floats
            input_data = {
                "Age": float(form_data.get("Age", 0)),
                "SystolicBP": float(form_data.get("SystolicBP", 0)),
                "DiastolicBP": float(form_data.get("DiastolicBP", 0)),
                "BS": float(form_data.get("BS", 0)),
                "BodyTemp": float(form_data.get("BodyTemp", 0)),
                "HeartRate": float(form_data.get("HeartRate", 0))
            }

            # Send data as QUERY PARAMETERS to FastAPI
            response = requests.post(FASTAPI_PREDICT_URL, params=input_data)

            print(f"API Response Status: {response.status_code}")
            print(f"API Response Body: {response.text}")  # Debugging output

            if response.status_code == 200:
                prediction_result = response.json().get("Predicted Risk Level", "Unknown result")
                prediction_message = f"Predicted Risk: {prediction_result}"
            elif response.status_code == 422:
                prediction_message = "Error: Invalid input data. Please check your values."
            else:
                prediction_message = f"Error: API returned {response.status_code}"

        except Exception as e:
            prediction_message = f"Error: {str(e)}"

    return render_template('predict.html', form_data=form_data, prediction_message=prediction_message)

@app.route('/preprocess')
def preprocess():
    return render_template('preprocess.html')

@app.route('/visualizations')
def visualizations():
    return render_template('visualizations.html')

@app.route('/upload-data', methods=['POST'])
def upload_data():
    if 'file' not in request.files:
        return jsonify({"detail": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"detail": "No selected file"}), 400

    # Log file content type to debug
    print(f"File content type: {file.content_type}")

    # Send the file to FastAPI backend
    response = requests.post(f'{RENDER_URL}/upload/', files={'file': (file.filename, file.stream, file.content_type)})


    if response.status_code == 200:
        data = response.json()
        return jsonify(data)
    else:
        return jsonify(response.json()), response.status_code

@app.route('/retrain', methods=['GET', 'POST'])
def retrain():
    if request.method == 'GET':
        return render_template('retrain.html')

    try:
        # Check if file exists in request
        if 'file' not in request.files:
            return jsonify({"detail": "No file part"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"detail": "No selected file"}), 400

        # Ensure the file is a CSV
        if file and file.filename.endswith('.csv'):
            files = {'file': (file.filename, file.stream, file.content_type)}

            # Step 1: Upload the file first
            upload_response = requests.post(f'{RENDER_URL}/upload/', files=files)
            
            if upload_response.status_code == 200:
                # Step 2: Call retraining after successful upload
                retrain_response = requests.post(f'{RENDER_URL}/retrain/', json={"file_path": "new_data.csv"})
                retrain_response.raise_for_status()
                
                return jsonify(retrain_response.json())

            return jsonify({"detail": "File upload failed", "error": upload_response.text}), upload_response.status_code

        return jsonify({"detail": "Invalid file type. Please upload a CSV file."}), 400

    except requests.exceptions.RequestException as e:
        print(f"Error communicating with FastAPI: {e}")
        return jsonify({"detail": f"Error retraining model: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)