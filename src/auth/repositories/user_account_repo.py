from django.contrib.postgres.search import SearchVector

from auth.models import UserAccount
from auth.schema import UserAccountStatusChoices
from auth.utils.password_hasher import Hasher
from main.utils.base_classes import BaseRepository
from main.utils.logger import log


class UserAccountRepository(BaseRepository):

    async def activate_account(self, id: str) -> bool:
        log.debug(f'init activate user account with id: {id}')
        account = self.get_by_id(id)
        if not account: return False
        await self.update(id, {'status': UserAccountStatusChoices.ACTIVE})
        return True

    async def change_password(self, id: str, password: str) -> bool:
        log.debug(f'init change account password with id: {id}')
        account = await self.model.objects.filter(id=id).afirst()
        if not account: return False
        account.password = Hasher.get_password_hash(password)
        await account.asave()
        return True

    async def get_by_identifier(self, identifier: str) -> UserAccount:
        return await self.model.objects.filter(identifier=identifier).afirst()

    async def list(
            self,
            search: str = None,
            skip: int = 0,
            limit: int = 100,
            is_deleted: bool = None
    ) -> list[UserAccount]:
        log.debug(f'init list user accounts with skip: {skip}, limit: {limit}')

        query = self.model.objects
        if is_deleted is not None: query = query.filter(is_deleted=is_deleted)

        search_fields = ['identifier']
        if search:
            results = query.annotate(search=SearchVector(*search_fields)).filter(search=search)
            return await self.paginate_queryset(results, skip, limit)

        query = self.model.objects.all()
        result = await self.paginate_queryset(query, skip, limit)
        return result
