import argon2


class Authorization:
    def __init__(self):
        self.hasher = argon2.PasswordHasher()

    def generate_hash(self, secret):
        return self.hasher.hash(secret)

    def verify_hash(self, hashed_secret, secret):
        try:
            self.hasher.verify(hashed_secret, secret)
            return True
        except argon2.exceptions.VerifyMismatchError:
            return False
