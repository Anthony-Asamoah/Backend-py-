from auth.schemas.user_account import UserAccountStatusChoices


async def authorize_account(account) -> bool:
    if not account: return False
    checks = [
        account.is_deleted,
        account.status != UserAccountStatusChoices.ACTIVE,
    ]
    if any(checks): return False
    return True
