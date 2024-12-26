from flask import Flask, render_template, request, redirect, url_for, session, make_response
from model import preprocess_user_input, predict_user_input

app = Flask(__name__)

# Set a secret key for session management
app.secret_key = 'your_secret_key_here'

# Route for handling login form (Sign-in)
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        found = False

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
                        return render_template('login.html', error="Incorrect password")

        if not found:
            return render_template('login.html', error="Email not found")

    return render_template('login.html')

# Route for handling sign-up form submission
@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

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
                return render_template('login.html', error="Email already exists")

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
            prediction_text = "Predicted Stress Type: Eustress"
        elif prediction == 2:
            prediction_text = "Predicted Stress Type: No Stress"
        else:
            prediction_text = "Predicted Stress Type: Distress"

        return redirect(url_for('result', prediction=prediction_text))

    return render_template('index.html', email=email)

# Route for displaying prediction result
@app.route('/result')
def result():
    prediction = request.args.get('prediction', 'No Prediction Available')
    return render_template('result.html', prediction=prediction)

if __name__ == '__main__':
    app.run(debug=True)
