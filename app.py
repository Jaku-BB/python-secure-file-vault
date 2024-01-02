from flask import Flask, request, jsonify, send_file
from hasher import get_hashed_file_secret, verify_hashed_file_secret
from vault import Vault, initialize_vault_directory
from sqlite3 import connect

DATABASE_PATH = 'file-vault-data.db'

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

    connection = connect(DATABASE_PATH)
    connection.execute('INSERT INTO file_vault (file_name, original_file_name, file_secret) VALUES (?, ?, ?)',
                       (encrypted_file_name, file.filename, hashed_file_secret))

    connection.commit()
    connection.close()

    return jsonify({'result': 'success', 'fileName': encrypted_file_name}), 200


@app.post('/decrypt')
def decrypt():
    validation_result = validate_request_data('decrypt')

    if validation_result is not True:
        return jsonify({'result': 'error', 'errors': validation_result}), 400

    file_name = request.form['file_name']
    file_secret = request.form['file_secret']

    connection = connect(DATABASE_PATH)
    result = connection.execute('SELECT original_file_name, file_secret FROM file_vault WHERE file_name = ?',
                                (file_name,)).fetchone()

    connection.close()

    if result is None:
        return jsonify({'result': 'error', 'errors': [{'field': 'file_name', 'message': 'File not found!'}]}), 404

    hashed_file_secret = result[1]

    if not verify_hashed_file_secret(hashed_file_secret, file_secret):
        return jsonify({'result': 'error', 'errors':
                        [{'field': 'file_secret', 'message': 'File secret is incorrect!'}]}), 403

    decrypted_file_path = vault.decrypt_and_get_path(file_name)

    if decrypted_file_path is False:
        return jsonify({'result': 'error', 'errors': [{'field': 'file_name', 'message': 'File not found!'}]}), 404

    return send_file(decrypted_file_path, as_attachment=True, download_name=result[0])


if __name__ == '__main__':
    initialize_vault_directory()

    connection = connect(DATABASE_PATH)
    connection.execute('CREATE TABLE IF NOT EXISTS file_vault (id INTEGER PRIMARY KEY, file_name TEXT, '
                       'original_file_name TEXT, file_secret TEXT)')

    connection.close()

    app.run(debug=True)
