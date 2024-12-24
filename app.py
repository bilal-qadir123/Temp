from flask import Flask, render_template, request, redirect, url_for
from model import preprocess_user_input, predict_user_input

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def entry_form():
    if request.method == 'POST':
        user_input = preprocess_user_input(request.form)
        prediction = predict_user_input(user_input)

        if prediction == 1:
            prediction_text = "Predicted Stress Type: Eustress"
        elif prediction == 2:
            prediction_text = "Predicted Stress Type: No Stress"
        else:
            prediction_text = "Predicted Stress Type: Distress"

        print(f"Prediction: {prediction_text}")

        # Redirect to another page with prediction data
        return redirect(url_for('result_page', prediction=prediction_text))

    return render_template('index.html')


@app.route('/result', methods=['GET'])
def result_page():
    prediction_text = request.args.get('prediction', default=None, type=str)
    return render_template('result.html', prediction=prediction_text)

if __name__ == '__main__':
    app.run(debug=True)
