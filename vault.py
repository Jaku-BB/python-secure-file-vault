from os import path, mkdir, remove
from io import BytesIO
from cryptography.fernet import Fernet
from uuid import uuid4

VAULT_PATH = path.join('instance', 'vault')
TEMPORARY_VAULT_PATH = path.join('instance', 'temporary-vault')
ENCRYPTION_KEY_PATH = path.join('instance', 'encryption-key')


def get_or_generate_encryption_key():
    try:
        with open(ENCRYPTION_KEY_PATH, 'r') as file:
            return file.read()
    except FileNotFoundError:
        encryption_key = Fernet.generate_key()

        with open(ENCRYPTION_KEY_PATH, 'wb') as file:
            file.write(encryption_key)

        return encryption_key


def initialize_vault_directory():
    if not path.exists(VAULT_PATH):
        mkdir(VAULT_PATH)

    if not path.exists(TEMPORARY_VAULT_PATH):
        mkdir(TEMPORARY_VAULT_PATH)


def get_file(file_path):
    target_file = BytesIO()

    with open(file_path, 'rb') as file:
        target_file.write(file.read())

    target_file.seek(0)
    remove(file_path)

    return target_file


class Vault:
    def __init__(self):
        self.fernet = Fernet(get_or_generate_encryption_key())

    def encrypt_and_save_file(self, file):
        encrypted_file = self.fernet.encrypt(file.read())
        encrypted_file_name = str(uuid4())

        with open(path.join(VAULT_PATH, encrypted_file_name), 'wb') as file:
            file.write(encrypted_file)

        return encrypted_file_name

    def decrypt_and_get_path(self, file_name):
        try:
            with open(path.join(VAULT_PATH, file_name), 'rb') as file:
                decrypted_file = self.fernet.decrypt(file.read())
        except FileNotFoundError:
            return False

        temporary_file_path = path.join(TEMPORARY_VAULT_PATH, file_name)

        with open(temporary_file_path, 'wb') as file:
            file.write(decrypted_file)

        return temporary_file_path
