from auth.schemas.user_account import UserAccountStatusChoices
from auth.utils.password_hasher import Hasher


async def authenticate_account(account, password) -> bool:
    if not account: return False
    checks = [
        account.is_deleted,
        account.status != UserAccountStatusChoices.ACTIVE,
    ]
    if any(checks): return False
    if not Hasher.verify_password(password, account.password): return False
    return True
