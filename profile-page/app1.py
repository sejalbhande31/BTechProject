from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_mysqldb import MySQL
import os
from datetime import datetime
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import hashlib
from io import BytesIO
from collections import Counter

app = Flask(__name__)
CORS(app)  # Allow CORS for communication between frontend and backend

# MySQL Configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'sejal@2004'
app.config['MYSQL_DB'] = 'profile'

mysql = MySQL(app)


# Load the pre-trained ResNet model (adjust the path to your model)
MODEL_PATH = 'C:/Users/usre/Desktop/Facial Detection/AutismDataset/output_model/resnet_124x124.keras'  # Replace with your actual model path
model = load_model(MODEL_PATH)

@app.route('/')
def index():
    try:
        # Get all images from the database
        cur = mysql.connection.cursor()
        cur.execute("SELECT image FROM capturedimages")
        rows = cur.fetchall()

        results = []
        for row in rows:
            image_data = row[0]
            # Convert the binary image data to a PIL image
            img = image.load_img(BytesIO(image_data), target_size=(124,124))

            # Preprocess the image for ResNet model
            img_array = image.img_to_array(img)  # Convert image to numpy array
            img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension

            # Run the image through the model
            predictions = model.predict(img_array)
           
            # Extract the predicted class from the prediction array
            predicted_class = "Autistic" if predictions[0][0] > 0.5 else "Not Autistic"
            results.append(predicted_class)

        # Calculate majority result only if there are results
        if results:
            result_counts = Counter(results)
            majority_result = result_counts.most_common(1)[0][0]
        else:
            result_counts = {}
            majority_result = "No images to classify"

        # Return the results to the frontend
        return render_template('index1.html', result_counts=result_counts, majority_result=majority_result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
