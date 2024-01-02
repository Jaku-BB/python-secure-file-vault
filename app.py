from flask import Flask, request, jsonify
from hasher import get_hashed_file_secret, verify_hashed_file_secret
from dotenv import load_dotenv
from os import getenv

load_dotenv()
app = Flask(__name__)


def validate_environment():
    environment_variables = ['ENCRYPTION_KEY']

    for variable in environment_variables:
        if getenv(variable) is None:
            raise Exception(f'{variable} is not set!')


def validate_request_data(route):
    errors = []

    if route == 'encrypt':
        if 'file' not in request.files:
            errors.append({'field': 'file', 'message': 'File is required!'})

    if route == 'decrypt':
        if 'file_name' not in request.form:
            errors.append({'field': 'file_name', 'message': 'File name is required!'})

    if 'file_secret' not in request.form:
        errors.append({'field': 'file_secret', 'message': 'File secret is required!'})

    return errors if len(errors) > 0 else True


@app.post('/encrypt')
def encrypt():
    validation_result = validate_request_data('encrypt')

    if validation_result is not True:
        return jsonify({'result': 'error', 'errors': validation_result}), 400

    file = request.files['file']
    file_secret = request.form['file_secret']

    hashed_file_secret = get_hashed_file_secret(file_secret)

    return jsonify({'result': 'success'}), 200


@app.post('/decrypt')
def decrypt():
    validation_result = validate_request_data('decrypt')

    if validation_result is not True:
        return jsonify({'result': 'error', 'errors': validation_result}), 400

    file_name = request.form['file_name']
    file_secret = request.form['file_secret']

    return jsonify({'result': 'success'}), 200


if __name__ == '__main__':
    validate_environment()
    app.run(debug=True)
