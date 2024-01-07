from os import path, mkdir, remove
from io import BytesIO
from cryptography.fernet import Fernet
from uuid import uuid4

VAULT_PATH = 'instance/vault'
TEMPORARY_VAULT_PATH = 'instance/vault-temporary'
ENCRYPTION_KEY_PATH = 'instance/encryption-key.key'


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

        with open(f'{VAULT_PATH}/{encrypted_file_name}', 'wb') as file:
            file.write(encrypted_file)

        return encrypted_file_name

    def decrypt_and_get_path(self, file_name):
        try:
            with open(f'{VAULT_PATH}/{file_name}', 'rb') as file:
                decrypted_file = self.fernet.decrypt(file.read())
        except FileNotFoundError:
            return False

        with open(f'{TEMPORARY_VAULT_PATH}/{file_name}', 'wb') as file:
            file.write(decrypted_file)

        return f'{TEMPORARY_VAULT_PATH}/{file_name}'
