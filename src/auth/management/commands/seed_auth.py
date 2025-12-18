from asgiref.sync import async_to_sync
from django.core.management.base import BaseCommand

from auth.models import Permission, Role, UserAccount
from auth.repositories import role_repo, user_account_repo
from auth.schemas.user_account import UserAccountStatusChoices
from auth.utils.password_hasher import Hasher
from auth.utils.permission_generator import permission_generator
from main import settings
from main.utils.logger import log


class Command(BaseCommand):
    help = 'Seed database with permissions, roles, and superuser (using dynamic permissions)'

    def handle(self, *args, **options):
        async_to_sync(self.async_handle)(*args, **options)

    async def async_handle(self, *args, **options):
        """Main seeding logic."""
        self.stdout.write(self.style.SUCCESS('Starting database seeding with dynamic permissions...'))

        # Step 1: Generate and create permissions dynamically
        permissions = await self.create_dynamic_permissions()
        self.stdout.write(self.style.SUCCESS(f'Created/verified {len(permissions)} permissions'))

        # Step 2: Create roles
        roles = await self.create_roles()
        self.stdout.write(self.style.SUCCESS(f'Created/verified {len(roles)} roles'))

        # Step 3: Assign permissions to roles
        await self.assign_permissions_to_roles(roles, permissions)
        self.stdout.write(self.style.SUCCESS('Assigned permissions to roles'))

        # Step 4: Create superuser
        superuser = await self.create_superuser()
        if superuser:
            self.stdout.write(self.style.SUCCESS(f'Created/verified superuser: {superuser.identifier}'))

            # Step 5: Assign admin role to superuser
            await self.assign_admin_role_to_superuser(superuser, roles['admin'])
            self.stdout.write(self.style.SUCCESS('Assigned admin role to superuser'))

        self.stdout.write(self.style.SUCCESS('\nDatabase seeding completed successfully!'))

    async def create_dynamic_permissions(self):
        """
        Create permissions dynamically from Django models.

        Format: app_label.model_name:action
        Examples:
            - notification.notification_template:create
            - notification.notification:read
            - user_info.userinfo:update
            - media.media:delete
        """
        # Generate all permissions from installed apps
        permission_names = permission_generator.generate_all_permissions()

        self.stdout.write(f'Generating {len(permission_names)} dynamic permissions...')

        permissions = {}
        for perm_name in permission_names:
            # Check if permission exists
            existing = await Permission.objects.filter(name=perm_name).afirst()

            if existing:
                log.debug(f'Permission already exists: {perm_name}')
                permissions[perm_name] = existing
            else:
                # Create new permission
                try:
                    perm = await Permission.objects.acreate(name=perm_name)
                    log.info(f'Created permission: {perm_name}')
                    permissions[perm_name] = perm
                except Exception as e:
                    log.error(f'Error creating permission {perm_name}: {e}')

        return permissions

    async def create_roles(self):
        """Create all roles."""
        role_names = ['admin', 'moderator', 'user']
        roles = {}

        for role_name in role_names:
            # Check if role exists
            existing = await role_repo.get_by_name(role_name)

            if existing:
                log.debug(f'Role already exists: {role_name}')
                roles[role_name] = existing
            else:
                # Create new role
                try:
                    role = await Role.objects.acreate(
                        name=role_name,
                        default=(role_name == 'user')  # Set 'user' as default role
                    )
                    log.info(f'Created role: {role_name}')
                    roles[role_name] = role
                except Exception as e:
                    log.error(f'Error creating role {role_name}: {e}')

        return roles

    async def assign_permissions_to_roles(self, roles, permissions):
        """
        Assign permissions to each role using the new dynamic format.

        Format: app.model:action
        Wildcards:
            - app.*:* = all models and actions in app
            - app.model:* = all actions on model
        """

        # Admin role: All permissions (wildcard for all apps)
        admin_permissions = [perm for perm in permissions.keys() if perm.endswith('*:*')]
        await self._assign_permissions(roles['admin'], admin_permissions, permissions)

        # Moderator role: Read all, manage user_info and media
        moderator_permissions = [
            'auth.useraccount:read',
            'auth.role:read',
            'auth.permission:read',
            'user_info.*:*',
            'media.*:*',
            'notification.notification:read',
            'notification.notificationdispatch:read',
        ]
        await self._assign_permissions(roles['moderator'], moderator_permissions, permissions)

        # User role: Basic permissions (own data)
        user_permissions = [
            'user_info.userinfo:read',
            'media.media:create',
            'media.media:read',
            'media.media:update',
            'notification.notification:read',
        ]
        await self._assign_permissions(roles['user'], user_permissions, permissions)

    async def _assign_permissions(self, role, permission_names, permissions):
        """Helper to assign multiple permissions to a role."""
        permission_ids = [
            str(permissions[pname].id)
            for pname in permission_names
            if pname in permissions
        ]

        if permission_ids:
            try:
                await role_repo.add_permissions(str(role.id), permission_ids)
                log.info(f'Assigned {len(permission_ids)} permissions to role: {role.name}')
            except ValueError as e:
                # Permissions might already be assigned, which is fine
                log.debug(f'Permissions may already be assigned to {role.name}: {e}')

    async def create_superuser(self):
        """Create superuser from environment variables."""
        # Get credentials from environment
        admin_identifier = settings.ADMIN_EMAIL or settings.ADMIN_PHONE
        admin_password = settings.ADMIN_PASSWORD

        if not admin_identifier or not admin_password:
            self.stdout.write(self.style.WARNING(
                'ADMIN_EMAIL (or ADMIN_PHONE) and ADMIN_PASSWORD not set in environment. '
                'Skipping superuser creation.'
            ))
            return None

        # Check if superuser already exists
        existing = await user_account_repo.get_by_identifier(admin_identifier)

        if existing:
            log.debug(f'Superuser already exists: {admin_identifier}')
            return existing

        # Create superuser
        try:
            superuser = await UserAccount.objects.acreate(
                identifier=admin_identifier,
                password=Hasher.get_password_hash(admin_password),
                status=UserAccountStatusChoices.ACTIVE,
                is_deleted=False
            )
            log.info(f'Created superuser: {admin_identifier}')
            return superuser
        except Exception as e:
            log.error(f'Error creating superuser: {e}')
            self.stdout.write(self.style.ERROR(f'Error creating superuser: {e}'))
            return None

    async def assign_admin_role_to_superuser(self, superuser, admin_role):
        """Assign admin role to superuser."""
        try:
            from asgiref.sync import sync_to_async

            # Check if role is already assigned
            has_role = await sync_to_async(superuser.roles.filter(id=admin_role.id).exists)()

            if not has_role:
                await sync_to_async(superuser.roles.add)(admin_role)
                log.info(f'Assigned admin role to superuser')
            else:
                log.debug(f'Admin role already assigned to superuser')

        except Exception as e:
            log.error(f'Error assigning admin role to superuser: {e}')
            self.stdout.write(self.style.ERROR(f'Error assigning admin role: {e}'))