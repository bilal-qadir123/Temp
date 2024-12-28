from flask import Flask, render_template, request, redirect, url_for, session, make_response
from model import preprocess_user_input, predict_user_input
import re

app = Flask(__name__)

# Set a secret key for session management
app.secret_key = 'your_secret_key_here'

# Route for handling login form (Sign-in)
@app.route('/', methods=['GET', 'POST'])
def login():
    if 'email' in session:
        return redirect(url_for('index'))  # If user is already logged in, redirect to index
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        found = False

        # Check for admin credentials
        if email == 'admin@123' and password == 'admin':
            return redirect(url_for('admin'))  # Redirect to admin.html

        # Read the accounts.txt file to check for matching credentials
        with open('accounts.txt', 'r') as file:
            accounts = file.readlines()

            for account in accounts:
                account = account.strip()
                if not account:  # Skip empty lines
                    continue
                try:
                    stored_email, stored_password = account.split(',')
                except ValueError:
                    print(f"Skipping malformed line: {account}")
                    continue  # Skip lines that don't have exactly one comma
                if stored_email == email:
                    found = True
                    if stored_password == password:
                        # Store email in session and redirect to index
                        session['email'] = email
                        return redirect(url_for('index'))
                    else:
                        return render_template('login.html')

        if not found:
            return render_template('login.html')

    return render_template('login.html')

# Route for handling sign-up form submission
@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    # Check if the email is admin (reserved email)
    if email == 'admin@123':
        return render_template('login.html')

    # Check if the email already exists in the accounts.txt file
    with open('accounts.txt', 'r') as file:
        accounts = file.readlines()
        for account in accounts:
            account = account.strip()
            if not account:  # Skip empty lines
                continue
            try:
                stored_email, _ = account.split(',')
            except ValueError:
                print(f"Skipping malformed line: {account}")
                continue  # Skip lines that don't have exactly one comma
            if stored_email == email:
                # If email already exists, show error
                return render_template('login.html')

    # If the email is not found, create the new account
    with open('accounts.txt', 'a') as file:
        file.write(f"{email},{password}\n")

    # Store email in session and redirect to index page after successful signup
    session['email'] = email
    return redirect(url_for('index'))

# Route for handling sign-out
@app.route('/signout')
def signout():
    session.pop('email', None)  # Clear the email from the session

    # Create the response and set no-cache headers
    response = make_response(redirect(url_for('login')))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Route for handling index page
@app.route('/index', methods=['GET', 'POST'])
def index():
    # Get email from session
    email = session.get('email')

    # If no email is found in session, redirect to login page
    if not email:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_input = preprocess_user_input(request.form)
        prediction = predict_user_input(user_input)

        if prediction == 1:
            prediction_text = "Predicted Stress Type: Eustress (Moderate level)"
        elif prediction == 2:
            prediction_text = "Predicted Stress Type: No Stress (0 or very low)"
        else:
            prediction_text = "Predicted Stress Type: Distress (High)" 

        # Collect user input details
        user_details = {key: request.form[key] for key in request.form}

        # Redirect to the result page with prediction and user details
        return redirect(
            url_for('result', prediction=prediction_text, **user_details)
        )

    return render_template('index.html', email=email)


# Route for displaying prediction result
@app.route('/result')
def result():
    email = session.get('email')
    prediction = request.args.get('prediction', 'No Prediction Available')

    # Extract user details from request args
    user_details = {key: request.args.get(key) for key in request.args if key != 'prediction'}
    user_details_str = ", ".join([f"{key}={value}" for key, value in user_details.items()])

    # Read existing data from predictions.txt
    updated = False
    new_lines = []
    with open('predictions.txt', 'r') as file:
        lines = file.readlines()
        for line in lines:
            stored_email = line.split(',')[0].strip()
            if stored_email == email:
                # Overwrite the line if email matches
                new_lines.append(f"{email}, {prediction}, {user_details_str}\n")
                updated = True
            else:
                new_lines.append(line)

    # If no matching email, append a new line
    if not updated:
        new_lines.append(f"{email}, {prediction}, {user_details_str}\n")

    # Write back the updated data to predictions.txt
    with open('predictions.txt', 'w') as file:
        file.writelines(new_lines)

    # Print details to the terminal for debugging
    print(f"Stored Data: Email={email}, Prediction={prediction}, Details={user_details_str}")

    return render_template('result.html', prediction=prediction, email=email, user_details=user_details)



@app.route('/admin', methods=['GET'])
def admin():
    email = "admin@123"  # Admin's email (hardcoded for this example)
    
    # Prepare lists to store data
    email_prediction_details = []

    with open('predictions.txt', 'r') as file:
        for line in file:
            # Split the line into email, prediction, and details
            parts = line.strip().split(', ', 2)
            if len(parts) == 3:
                email_data, prediction, details = parts
                email_prediction_details.append((email_data, prediction, details))
            else:
                email_data, prediction = parts
                email_prediction_details.append((email_data, prediction, "No additional details"))

    # Calculate the counts
    total_students = len(email_prediction_details)
    eustress_count = sum(1 for _, prediction, _ in email_prediction_details if "Eustress" in prediction)
    no_stress_count = sum(1 for _, prediction, _ in email_prediction_details if "No Stress" in prediction)
    distress_count = sum(1 for _, prediction, _ in email_prediction_details if "Distress" in prediction)

    return render_template(
        'admin.html',
        email_prediction_details=email_prediction_details,
        account=email,
        total_students=total_students,
        eustress_count=eustress_count,
        no_stress_count=no_stress_count,
        distress_count=distress_count
    )




if __name__ == '__main__':
    app.run(debug=True)
