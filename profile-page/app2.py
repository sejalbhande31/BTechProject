# from flask import Flask, render_template
# import numpy as np
# import mysql.connector
# from tensorflow.keras.models import load_model
# from tensorflow.keras.preprocessing import image
# from PIL import Image
# import io
# from collections import Counter

# app = Flask(__name__)

# # Load the trained model
# model = load_model(r'C:/Users/usre/Desktop/Facial Detection/AutismDataset/output_model/resnet_124x124.keras')  # Replace with the path to your .h5 model

# # Database connection setup
# db = mysql.connector.connect(
#     host="localhost",
#     user="root",      # Replace with your MySQL username
#     password="sejal@2004",  # Replace with your MySQL password
#     database="profile"    # Replace with your MySQL database name
# )

# cursor = db.cursor()

# # Function to load and preprocess an image
# def preprocess_image(img_data, target_size=(124, 124)):  # Resize to 124x124
#     img = Image.open(io.BytesIO(img_data))  # Convert LONGBLOB to an image
#     img = img.resize(target_size)  # Resize image to 124x124
#     img_array = np.array(img)
#     img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
#     img_array = img_array / 255.0  # Normalize the image
#     return img_array

# # Function to fetch all images from the database and classify them
# def classify_images_from_db():
#     results = []
    
#     # Query to fetch all images and associated metadata
#     cursor.execute("SELECT id, image FROM CapturedImages")
#     images = cursor.fetchall()
    
#     for img_id, img_data in images:
#         # Preprocess the image
#         img_array = preprocess_image(img_data)

#         # Get model prediction
#         prediction = model.predict(img_array)

#         # Assuming binary classification (output shape of [1, 1]):
#         # Use `prediction[0][0]` for binary classification (probability for "autistic")
#         result = 'autistic' if prediction[0][0] > 0.5 else 'non-autistic'
#         results.append(result)
    
#     return results

# # Function to calculate the majority result
# def calculate_majority(results):
#     result_counts = Counter(results)
#     majority_result = result_counts.most_common(1)[0][0]
#     return majority_result, result_counts

# @app.route('/')
# def index():
#     # Classify all images in the database
#     results = classify_images_from_db()

#     # Calculate majority result
#     majority_result, result_counts = calculate_majority(results)

#     # Return the results to the frontend
#     return render_template('index1.html', result_counts=result_counts, majority_result=majority_result)

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, render_template
import numpy as np
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image
import io
from collections import Counter

app = Flask(__name__)

# Load the trained model
model = load_model(r'C:/Users/usre/Desktop/Facial Detection/AutismDataset/output_model/resnet_124x124.keras')  # Replace with the path to your .h5 model

# Directory where the images are stored
IMAGES_FOLDER = 'C:/Users/usre/Desktop/Facial Detection/AutismDataset/valid/Non_Autistic'  # Replace with the folder path containing images

# Function to load and preprocess an image
def preprocess_image(img_path, target_size=(124, 124)):  # Resize to 124x124
    img = Image.open(img_path)  # Open the image file
    img = img.resize(target_size)  # Resize image to 124x124
    img_array = np.array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    img_array = img_array / 255.0  # Normalize the image
    return img_array

# Function to classify images from a folder
def classify_images_from_folder():
    results = []

    # Iterate through all image files in the folder
    for filename in os.listdir(IMAGES_FOLDER):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):  # Check if the file is an image
            img_path = os.path.join(IMAGES_FOLDER, filename)
            
            # Preprocess the image
            img_array = preprocess_image(img_path)

            # Get model prediction
            prediction = model.predict(img_array)

            # Assuming binary classification (output shape of [1, 1]):
            # Use `prediction[0][0]` for binary classification (probability for "autistic")
            result = 'autistic' if prediction[0][0] > 0.5 else 'non-autistic'
            results.append(result)
    
    return results

# Function to calculate the majority result
def calculate_majority(results):
    result_counts = Counter(results)
    majority_result = result_counts.most_common(1)[0][0]
    return majority_result, result_counts

@app.route('/')
def index():
    # Classify all images in the folder
    results = classify_images_from_folder()

    # Calculate majority result
    majority_result, result_counts = calculate_majority(results)

    # Return the results to the frontend
    return render_template('index1.html', result_counts=result_counts, majority_result=majority_result)

if __name__ == '__main__':
    app.run(debug=True)

