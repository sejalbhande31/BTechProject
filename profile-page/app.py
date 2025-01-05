from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_mysqldb import MySQL
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Allow CORS for communication between frontend and backend

# MySQL Configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'sejal@2004'
app.config['MYSQL_DB'] = 'profile'

mysql = MySQL(app)

# Directory to temporarily save uploaded images
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/")
def home():
    return render_template("detection.html")

import hashlib

@app.route("/upload", methods=["POST"])
def upload_image():
    try:
        image_file = request.files['image']
        if image_file:
            # Generate a unique filename using hash to avoid overwriting
            filename = image_file.filename
            # Hash the filename to ensure uniqueness (can also use current timestamp if needed)
            file_hash = hashlib.md5(filename.encode()).hexdigest()
            unique_filename = f"{file_hash}_{filename}"
            
            # Save the image to the 'uploads' folder
            image_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            image_file.save(image_path)  # Save the file to the folder

            # Insert the image into the database with the file path and timestamp
            with open(image_path, 'rb') as img_file:
                image_data = img_file.read()

            # Insert the image data and timestamp into the database
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO capturedimages (timestamp, image, filename) VALUES (NOW(), %s, %s)", (image_data, unique_filename))
            mysql.connection.commit()
            cur.close()

            return jsonify({"success": True, "message": "Image uploaded and stored successfully!"})
        else:
            return jsonify({"success": False, "message": "No image uploaded!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)







