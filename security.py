
from argon2 import PasswordHasher, exceptions


ph = PasswordHasher()


def hash_password(password):
    return ph.hash(password)

def verify_password(password, hashed_password):
    try:
        ph.verify(hashed_password, password)
        return True
    except exceptions.VerifyMismatchError:
        return False