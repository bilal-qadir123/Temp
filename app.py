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

        return redirect(url_for('result', prediction=prediction_text)) 

    return render_template('index.html', email=email)

# Route for displaying prediction result
@app.route('/result')
def result(): 
    email = session.get('email') 
    prediction = request.args.get('prediction', 'No Prediction Available')

    # Slice the prediction string from the 4th index onwards
    prediction_type = prediction[23:]  # This removes the first 4 characters ("Pred")

    # Read the predictions.txt file to check if the email already exists
    found = False
    with open('predictions.txt', 'r') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            stored_email, _ = line.strip().split(',')
            if stored_email == email:
                # If the email is found, overwrite the prediction (after the email)
                lines[i] = f"{email},{prediction_type}\n"
                found = True
                break
    
    # If email not found, add the email and the prediction type
    if not found:
        lines.append(f"{email},{prediction_type}\n")

    # Write the updated predictions back to the file
    with open('predictions.txt', 'w') as file:
        file.writelines(lines)

    return render_template('result.html', prediction=prediction, email=email)

@app.route('/admin', methods=['GET'])
def admin():
    email = "admin@123"  # Get the email from the session
    
    emails = []
    predictions = []
    
    with open('predictions.txt', 'r') as file:
        for line in file:
            email_data, prediction = line.strip().split(',')
            emails.append(email_data)
            predictions.append(prediction)

    # Extract numbers from emails and prepare tuples
    email_prediction_pairs = []
    for email_data, prediction in zip(emails, predictions):
        numbers_from_email = ''.join(re.findall(r'\d+', email_data))  # Extract numbers from email
        email_prediction_pairs.append((numbers_from_email, email_data, prediction))

    # Calculate the counts
    total_students = len(email_prediction_pairs)
    eustress_count = predictions.count('Eustress (Moderate level)')
    no_stress_count = predictions.count('No Stress (0 or very low)')
    distress_count = predictions.count('Distress (High)')

    return render_template(
        'admin.html',
        email_prediction_pairs=email_prediction_pairs,
        account=email,
        total_students=total_students,
        eustress_count=eustress_count,
        no_stress_count=no_stress_count,
        distress_count=distress_count
    )



if __name__ == '__main__':
    app.run(debug=True)
