from flask import Flask, request, jsonify, render_template, redirect, url_for, flash,session 
import mysql.connector
from mysql.connector import Error
import os, random, string, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'sejal@2004@2412'  # Secret key for session management

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'sejal@2004',
    'database': 'profile'
}
@app.route('/')
def index():
    return render_template('index.html')  # index.html page

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
        child_name = request.form.get('child-name')
        child_age = request.form.get('child-age')

        # Check if passwords match
        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match!'}), 400

        # Insert into the database
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            query = """
                INSERT INTO users (parent_name, phone, email, password, child_name, child_age)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (parent_name, phone, email, password, child_name, int(child_age)))
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
    return render_template('parentDashboard.html') 


if __name__ == '__main__':
    app.run(debug=True)
