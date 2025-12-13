from auth.schema import UserAccountStatusChoices
from main.settings import PWD_CONTEXT


class Hasher:
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return PWD_CONTEXT.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return PWD_CONTEXT.hash(password)


async def authenticate_user(account, password) -> bool:
    if not account: return False
    checks = [
        account.is_deleted,
        account.status != UserAccountStatusChoices.ACTIVE,
    ]
    if any(checks): return False
    if not Hasher.verify_password(password, account.password): return False
    return True
