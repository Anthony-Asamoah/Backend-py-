from auth.schemas.user_account import UserAccountOut, CurrentAccountOut
from main.utils.logger import log
from user_info.use_cases import user_info_service


async def get_authenticated_user(cls, current_user: UserAccountOut) -> CurrentAccountOut:
    log.debug(f'init get {current_user.identifier} info')

    return CurrentAccountOut(
        **current_user.model_dump(),
        user_info=await user_info_service.repo.get_by_id(current_user.id)
    )
