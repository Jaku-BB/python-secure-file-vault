from argon2 import PasswordHasher as Hasher, exceptions

hasher = Hasher()


def get_hashed_file_secret(file_secret):
    return hasher.hash(file_secret)


def verify_hashed_file_secret(hashed_file_secret, file_secret):
    try:
        hasher.verify(hashed_file_secret, file_secret)
        return True
    except exceptions.VerifyMismatchError:
        return False
