from flask import Flask, render_template, request
import joblib
import numpy as np
import pandas as pd

app = Flask(__name__)

# Load model, scaler, and training columns
model = joblib.load('logistic_regression_model.pkl')
scaler = joblib.load('scaler.pkl')
model_columns = joblib.load('model_columns.pkl')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # 1. Capture numerical inputs from form
        page_values = float(request.form['page_values'])
        product_related = float(request.form['product_related'])
        product_related_duration = float(request.form['product_related_duration'])
        bounce_rates = float(request.form['bounce_rates'])
        exit_rates = float(request.form['exit_rates'])
        special_day = float(request.form['special_day'])
        weekend = int(request.form['weekend'])
        
        # 2. Capture categorical inputs from form dropdowns
        selected_month = request.form['month']
        selected_visitor = request.form['visitor_type']

        # 3. Initialize a dictionary of zeros matching all trained columns
        input_data = {col: 0 for col in model_columns}

        # Fill in numerical inputs
        input_data['PageValues'] = page_values
        input_data['ProductRelated'] = product_related
        input_data['ProductRelated_Duration'] = product_related_duration
        input_data['BounceRates'] = bounce_rates
        input_data['ExitRates'] = exit_rates
        input_data['SpecialDay'] = special_day
        input_data['Weekend'] = weekend

        # Fill in one-hot encoded categorical inputs dynamically
        month_col = f"Month_{selected_month}"
        if month_col in input_data:
            input_data[month_col] = 1

        visitor_col = f"VisitorType_{selected_visitor}"
        if visitor_col in input_data:
            input_data[visitor_col] = 1

        # 4. Convert to DataFrame and Scale
        input_df = pd.DataFrame([input_data])
        input_scaled = scaler.transform(input_df)

        # 5. Predict
        prediction = model.predict(input_scaled)[0]
        probability = model.predict_proba(input_scaled)[0][1] * 100

        result_text = "Will Make a Purchase (Revenue = True)" if prediction == 1 else "Will Not Make a Purchase (Revenue = False)"
        return render_template('index.html', prediction_text=f"{result_text} (Confidence: {probability:.2f}%)")

    except Exception as e:
        return render_template('index.html', prediction_text=f"Error: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)