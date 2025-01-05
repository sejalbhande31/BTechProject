import datetime
from flask_mysqldb import MySQL
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
from PIL import Image
from io import BytesIO
import hashlib
from flask_cors import CORS
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
from collections import Counter

app = Flask(__name__)
app.secret_key = 'sejal@2004@2412'  # Secret key for session management
CORS(app)  # Allow CORS for communication between frontend and backend


# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'sejal@2004',
    'database': 'profile'
}
@app.route('/')
def index():
    return render_template('index.html')  # Returns an index.html page


# Load the pre-trained ResNet model (adjust the path to your model)
MODEL_PATH = 'C:/Users/usre/Desktop/Facial Detection/AutismDataset/output_model/resnet_124x124.keras'  # Replace with your actual model path
model = load_model(MODEL_PATH)

# Directory where the images are stored
IMAGES_FOLDER = 'C:/Users/usre/Desktop/Facial Detection/AutismDataset/valid/Non_Autistic'  # Replace with the folder path containing images


@app.route('/autismInfo')
def autismInfo():
    return render_template('autismInfo.html') 

@app.route('/autismSigns')
def autismSigns():
    return render_template('autismSigns.html') 

@app.route('/detectArticle')
def detectArticle():
    return render_template('detectArticle.html') 

# Route to render the signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        parent_name = request.form.get('parent-name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
       

        # Check if passwords match
        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match!'}), 400

        # Insert into the database
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            query = """
                INSERT INTO users (parent_name, phone, email, password)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (parent_name, phone, email, password))
            conn.commit()

            flash('Profile created successfully!', 'success')
            return redirect(url_for('login'))

        except Error as e:
             flash(f'Error: {str(e)}', 'danger')
             return redirect(url_for('signup'))

        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    return render_template('signup.html')
   

# Route to render the login page and handle login logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # Query to check if email exists in the database
            query = "SELECT * FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()

            # Check if user exists and password matches
            if user and user[4] == password:  # user[3] is the 'password' field in the 'users' table
                # Store user data in session
                session['user_id'] = user[0]  # Assuming 'user_id' is in the first column
                flash('Login successful!', 'success')
                return redirect(url_for('parentDashboard'))  # Redirect to home or dashboard page
            else:
                flash('Invalid email or password. Please try again.', 'danger')
                return redirect(url_for('login'))  # Redirect back to login

        except Error as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('login'))

        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    return render_template('login.html')

@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    if request.method == 'POST':
        # Always update parent details
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')

        query_update_users = """
            UPDATE users
            SET phone = %s, email = %s, password = %s
            WHERE user_id = %s
        """
        cursor.execute(query_update_users, (phone, email, password, user_id))
        conn.commit()

        # Check if child details already exist
        cursor.execute("SELECT child_id FROM children WHERE parent_id = %s", (user_id,))
        child_exists = cursor.fetchone()

        # Insert or update child details
        if child_exists:
            # Update child's age if already exists
            age = request.form.get('child-age')
            if age:
                query_update_child_age = """
                    UPDATE children
                    SET age = %s
                    WHERE parent_id = %s
                """
                cursor.execute(query_update_child_age, (age, user_id))
                conn.commit()
        else:
            # Insert new child details
            full_name = request.form.get('child-full-name')
            dob = request.form.get('child-dob')
            age = request.form.get('child-age')
            gender = request.form.get('gender')

            query_insert_children = """
                INSERT INTO children (parent_id, full_name, dob, age, gender)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query_insert_children, (user_id, full_name, dob, age, gender))
            conn.commit()

        return redirect(url_for('parentDashboard', success='true'))

    # Fetch current user and child data
    cursor.execute("SELECT parent_name, phone, email FROM users WHERE user_id = %s", (user_id,))
    user_data = cursor.fetchone()

    cursor.execute("SELECT full_name, dob, age, gender FROM children WHERE parent_id = %s", (user_id,))
    child_data = cursor.fetchone()

    if not user_data:
        return "User not found!", 404

    # Prepare data for rendering
    parent_name, phone, email = user_data
    if child_data:
        child_full_name, child_dob, child_age, gender = child_data
        return render_template('update_profile.html',
                               parent_name=parent_name,
                               phone=phone,
                               email=email,
                               child_full_name=child_full_name,
                               child_dob=child_dob,
                               child_age=child_age,
                               gender=gender,
                               has_child=True)
    else:
        return render_template('update_profile.html',
                               parent_name=parent_name,
                               phone=phone,
                               email=email,
                               has_child=False)




# Function to generate a random OTP
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

# Function to send OTP to email
def send_otp_to_email(email, otp):
    try:
        msg = MIMEMultipart()
        msg['From'] = 'sejalbhande31@gmail.com'  # Your email
        msg['To'] = email
        msg['Subject'] = 'SpectrumCare: OTP for Password Reset'
        body = f'Your OTP for resetting your password is: {otp}'
        msg.attach(MIMEText(body, 'plain'))

        # Use your email provider's SMTP server (Gmail, for example)
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login('sejalbhande31@gmail.com', 'bfcj bkog qcih dcuz')  # Login with your email credentials
            text = msg.as_string()
            server.sendmail(msg['From'], msg['To'], text)
    except Exception as e:
        print(f"Failed to send OTP: {str(e)}")

# Route to handle forgot password page and OTP generation
@app.route('/forgotPassword', methods=['GET', 'POST'])
def forgotPassword():
    if request.method == 'POST':
        email = request.form.get('email')
        

        # Validate email (phone is optional, so we focus on email)
        if not email:
            flash('Please enter a valid email address.', 'danger')
            return redirect(url_for('forgotPassword'))

        otp = generate_otp()  # Generate OTP
        session['otp'] = otp  # Save OTP in session
        session['email'] = email  # Save email for comparison

        # Send OTP to the user's email
        send_otp_to_email(email, otp)

        flash('OTP sent to your email! Please check your inbox.', 'success')
        return redirect(url_for('verifyOtp'))  # Redirect to OTP verification page
    
    return render_template('forgotPassword.html')  # Show the forgot password page


# Route to handle OTP verification and password reset
@app.route('/verifyOtp', methods=['GET', 'POST'])
def verifyOtp():
    if request.method == 'POST':
        otp = request.form.get('otp')
        new_password = request.form.get('new-password')
        confirm_password = request.form.get('confirm-password')

        # Check if OTP matches the one in session
        if otp != session.get('otp'):
            flash('Invalid OTP. Please try again.', 'danger')
            return redirect(url_for('verifyOtp'))

        # Check if passwords match
        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('verifyOtp'))

        # Update password in the database
        email = session.get('email')
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            query = "UPDATE users SET password = %s WHERE email = %s"
            cursor.execute(query, (new_password, email))
            conn.commit()

            flash('Password reset successfully!', 'success')
            return redirect(url_for('login'))  # Redirect to login page
        except Error as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('verifyOtp'))
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    return render_template('verifyOtp.html')  # Page where OTP is verified and password is reset 


@app.route('/parentDashboard')
def parentDashboard():
    user_id = session.get('user_id')
    
    if user_id:  # If the user is logged in
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)  # Enable dictionary cursor

        query = """
            SELECT c.full_name, c.dob, c.gender, c.age, u.parent_name
            FROM users u
            JOIN children c ON u.user_id = c.parent_id
            WHERE u.user_id = %s;
        """
        cursor.execute(query, (user_id,))  # Pass user_id as a parameter to the query
        result = cursor.fetchone() 

        if result:  # If data is found
            # Extract the child data from the result
            child_name = result['full_name']
            child_dob = result['dob']
            child_gender = result['gender']
            child_age = result['age']
            parent_name = result['parent_name']

            # Close the cursor and connection
            cursor.close()
            conn.close()

            # Pass the data to the template
            return render_template('parentDashboard.html', 
                                   child_name=child_name, 
                                   child_dob=child_dob, 
                                   child_gender=child_gender, 
                                   child_age=child_age, 
                                   parent_name=parent_name)
        else:
            # If no data found for the user, redirect to login
            cursor.close()
            conn.close()
            return redirect(url_for('login'))
    else:
        # If the user is not logged in, redirect to login
        return redirect(url_for('login'))


@app.route('/resources')
def resources_support():
    return render_template('resources_support.html')
@app.route('/faq')
def faqSection():
    return render_template('faqSection.html')
@app.route('/logOut')
def logOut():
    session.pop('user_id',None)
    return redirect(url_for('index'))

@app.route('/detectGuide')
def detectGuide():
    return render_template('detectGuide.html')

@app.route('/detection')
def detection():
    return render_template('detection.html') 

@app.route('/intervention')
def intervention():
    return render_template('intervention.html')

@app.route('/countingGame')
def countingGame():
    return render_template('countingGame.html')

@app.route('/mazeGame')
def mazeGame():
    return render_template('mazeGame.html')

@app.route('/flashcardGame')
def flashcardGame():
    return render_template('flashCardGame.html')

@app.route('/flashCategory')
def flashCategory():
    category = request.args.get('category')
    return render_template('flashCategory.html',category=category)

@app.route('/submit_score',methods=['POST'])
def submit_score():
   try:
    data = request.json
    score = data['score']
    game_type = data['game_type']

    print(f"Inserting score: {score}, game_type: {game_type}")

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    query = "INSERT INTO game_scores (score, game_type) VALUES (%s, %s)"
    cursor.execute(query, (score, game_type))
    conn.commit()

    print("Score inserted successfully!")
   except Exception as e:
    print(f"Error: {str(e)}")
    return jsonify({'error': str(e)}), 500


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
            result = 'Autistic' if prediction[0][0] > 0.5 else 'Non-Autistic'
            results.append(result)
    
    return results

# Function to calculate the majority result
def calculate_majority(results):
    result_counts = Counter(results)
    majority_result = result_counts.most_common(1)[0][0]
    return majority_result, result_counts

import mysql.connector

@app.route('/index1')
def index1():
    # Classify all images in the folder
    results = classify_images_from_folder()

    # Calculate majority result
    majority_result, result_counts = calculate_majority(results)
  

    # Return the results to the frontend
    return render_template('index1.html', result_counts=result_counts, majority_result=majority_result)


@app.route('/questionnaire')
def questionnaire():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Fetch the child's ID for the logged-in user
    cursor.execute("SELECT child_id FROM children WHERE parent_id = %s", (user_id,))
    child_data = cursor.fetchone()
    conn.close()

    if child_data:
        child_id = child_data[0]
        session['child_id'] = child_id  # Set child_id in session
    else:
        return "No child data found for the logged-in user.", 404

    return render_template('questionnaire.html', child_id=child_id)

@app.route('/submit_survey', methods=['POST'])
def submit_survey():
    if 'child_id' not in session:
        return jsonify({'error': 'Child ID not found in session'}), 400

    children_id = session['child_id']
    responses = request.json.get('responses', [])

    # Debugging: Print the child_id and responses
    print(f"Child ID: {children_id}")
    print(f"Received responses: {responses}")

    # Validate responses
    if len(responses) != 10:
        return jsonify({'error': 'Incomplete responses'}), 400

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Insert responses into the survey_responses table
        for question_number, response in enumerate(responses, start=1):
            query = """
                INSERT INTO survey_responses (children_id, question_number, response)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (children_id, question_number, response))

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify('Survey responses saved successfully!'), 200
    except Exception as e:
        print(f"Error: {str(e)}")  # Debugging: Print the error
        return jsonify({'error': str(e)}), 500


# Directory to temporarily save uploaded images
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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
            # cur =  mysql.connector.connect(**db_config)
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO capturedimages (timestamp, image, filename) VALUES (NOW(), %s, %s)", (image_data, unique_filename))
            conn.commit()
            cursor.close()

            return jsonify({"success": True, "message": "Image uploaded and stored successfully!"})
        else:
            return jsonify({"success": False, "message": "No image uploaded!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
