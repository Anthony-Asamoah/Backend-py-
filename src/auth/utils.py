from main.settings import PWD_CONTEXT


class Hasher:
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return PWD_CONTEXT.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return PWD_CONTEXT.hash(password)