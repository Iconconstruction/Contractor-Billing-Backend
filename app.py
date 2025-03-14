from flask import Flask, request, send_file
import pandas as pd
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS


app = Flask(__name__)

UPLOAD_FOLDER = 'invoices'
DATA_FILE = 'billing_data.xlsx'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/submit', methods=['POST'])
def submit_billing():
    contractor_name = request.form.get('contractorName')
    subdivision_lot = request.form.get('subdivisionLot')
    job_address = request.form.get('jobAddress')
    payment_amount = request.form.get('paymentAmount')
    invoice_file = request.files.get('invoiceFile')

    if not all([contractor_name, subdivision_lot, job_address, payment_amount, invoice_file]):
        return "Missing data", 400

    filename = secure_filename(invoice_file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    invoice_file.save(file_path)

    new_data = {
        'Contractor Name': [contractor_name],
        'Subdivision & Lot': [subdivision_lot],
        'Job Address': [job_address],
        'Payment Amount ($)': [payment_amount],
        'Invoice File': [file_path]
    }

    if os.path.exists(DATA_FILE):
        df = pd.read_excel(DATA_FILE)
        df = pd.concat([df, pd.DataFrame(new_data)], ignore_index=True)
    else:
        df = pd.DataFrame(new_data)

    df.to_excel(DATA_FILE, index=False)

    return "Submission Successful", 200


@app.route('/download', methods=['GET'])
def download_excel():
    if os.path.exists(DATA_FILE):
        return send_file(DATA_FILE, as_attachment=True)
    else:
        return "No data available", 404


if __name__ == '__main__':
    app.run(debug=True)
