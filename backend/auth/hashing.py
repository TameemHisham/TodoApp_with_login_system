from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plain password."""
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return password_hash.verify(plain_password, hashed_password)


if __name__ == "__main__":
    testVal = "123"
    hashed_testVal = hash_password("123")
    print(hashed_testVal)
    print(verify_password(testVal, hashed_testVal))
