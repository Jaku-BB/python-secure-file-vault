from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from hasher import get_hashed_file_secret, verify_hashed_file_secret
from vault import Vault, initialize_vault_directory, get_file

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///file-vault-data.db'

database = SQLAlchemy(app)
vault = Vault()


class FileVaultMetaData(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    file_name = database.Column(database.String(255), nullable=False)
    original_file_name = database.Column(database.String(255), nullable=False)
    file_secret = database.Column(database.String(255), nullable=False)


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

    file_vault_entry = FileVaultMetaData(file_name=encrypted_file_name, original_file_name=file.filename,
                                         file_secret=hashed_file_secret)

    database.session.add(file_vault_entry)
    database.session.commit()

    return jsonify({'result': 'success', 'fileName': encrypted_file_name}), 200


@app.post('/decrypt')
def decrypt():
    validation_result = validate_request_data('decrypt')

    if validation_result is not True:
        return jsonify({'result': 'error', 'errors': validation_result}), 400

    file_name = request.form['file_name']
    file_secret = request.form['file_secret']

    file_vault_entry = FileVaultMetaData.query.filter_by(file_name=file_name).first()

    if file_vault_entry is None:
        return jsonify({'result': 'error', 'errors': [{'field': 'file_name', 'message': 'File not found!'}]}), 404

    hashed_file_secret = file_vault_entry.file_secret

    if not verify_hashed_file_secret(hashed_file_secret, file_secret):
        return jsonify({'result': 'error', 'errors':
                        [{'field': 'file_secret', 'message': 'File secret is incorrect!'}]}), 403

    decrypted_file_path = vault.decrypt_and_get_path(file_name)

    if decrypted_file_path is False:
        return jsonify({'result': 'error', 'errors': [{'field': 'file_name', 'message': 'File not found!'}]}), 404

    file = get_file(decrypted_file_path)

    return send_file(file, as_attachment=True, download_name=file_vault_entry.original_file_name)


if __name__ == '__main__':
    initialize_vault_directory()

    with app.app_context():
        database.create_all()

    app.run()
