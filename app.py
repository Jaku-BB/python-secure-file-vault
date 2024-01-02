from flask import Flask, request, jsonify
from hasher import get_hashed_file_secret, verify_hashed_file_secret
from vault import Vault, initialize_vault_directory

app = Flask(__name__)
vault = Vault()


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
    encrypted_file_name = vault.encrypt_and_save_file(file)

    return jsonify({'result': 'success', 'fileName': encrypted_file_name}), 200


@app.post('/decrypt')
def decrypt():
    validation_result = validate_request_data('decrypt')

    if validation_result is not True:
        return jsonify({'result': 'error', 'errors': validation_result}), 400

    file_name = request.form['file_name']
    file_secret = request.form['file_secret']

    decrypted_file_path = vault.decrypt_and_get_path(file_name)

    if decrypted_file_path is False:
        return jsonify({'result': 'error', 'errors': [{'field': 'file_name', 'message': 'File not found!'}]}), 404

    return jsonify({'result': 'success'}), 200


if __name__ == '__main__':
    initialize_vault_directory()
    app.run(debug=True)
