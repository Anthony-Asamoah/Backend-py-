"""
Dynamic Permission Generator

Generates permissions based on Django models in the format:
app_label.model_name:action

Examples:
- notification.notification_template:create
- notification.notification:read
- user_info.userinfo:update
- media.media:delete
"""
from typing import List, Set

from django.apps import apps
from main.utils.logger import log


class PermissionGenerator:
    """Generate permissions dynamically from Django models."""

    # Standard CRUD actions
    ACTIONS = ['create', 'read', 'update', 'delete']

    # Apps to exclude from permission generation
    EXCLUDED_APPS = [
        'contenttypes',
        'postgres',
        'sessions',
        'admin',
        'staticfiles',
    ]

    @classmethod
    def get_installed_apps(cls) -> List[str]:
        """Get list of installed apps excluding system apps."""
        return [
            app_config.label
            for app_config in apps.get_app_configs()
            if app_config.label not in cls.EXCLUDED_APPS
        ]

    @classmethod
    def get_models_for_app(cls, app_label: str) -> List[str]:
        """Get all model names for a given app."""
        try:
            app_config = apps.get_app_config(app_label)
            return [model.__name__.lower() for model in app_config.get_models()]
        except LookupError:
            log.warning(f"App '{app_label}' not found")
            return []

    @classmethod
    def generate_permission(cls, app_label: str, model_name: str, action: str) -> str:
        """Generate a single permission string."""
        return f"{app_label}.{model_name}:{action}"

    @classmethod
    def generate_wildcard_permissions(cls, app_label: str, model_name: str) -> List[str]:
        """Generate wildcard permissions for a model."""
        return [
            f"{app_label}.{model_name}:*",  # All actions for this model
            f"{app_label}.*:*",  # All models and actions in this app
        ]

    @classmethod
    def generate_all_permissions(cls) -> Set[str]:
        """Generate all permissions for all installed apps and models."""
        permissions = set()

        installed_apps = cls.get_installed_apps()
        log.info(f"Generating permissions for apps: {installed_apps}")

        for app_label in installed_apps:
            models = cls.get_models_for_app(app_label)

            if not models:
                continue

            # Add app-level wildcard
            permissions.add(f"{app_label}.*:*")

            for model_name in models:
                # Add model-level wildcard
                permissions.add(f"{app_label}.{model_name}:*")

                # Add action-specific permissions
                for action in cls.ACTIONS:
                    perm = cls.generate_permission(app_label, model_name, action)
                    permissions.add(perm)

        log.info(f"Generated {len(permissions)} permissions")
        return permissions

    @classmethod
    def parse_permission(cls, permission: str) -> tuple:
        """
        Parse a permission string into components.

        Args:
            permission: Permission string (e.g., 'notification.notification_template:create')

        Returns:
            Tuple of (app_label, model_name, action)
            Returns (None, None, None) if invalid format
        """
        try:
            resource, action = permission.split(':')
            app_label, model_name = resource.split('.')
            return app_label, model_name, action
        except ValueError:
            log.warning(f"Invalid permission format: {permission}")
            return None, None, None

    @classmethod
    def check_permission_match(cls, required: str, granted: str) -> bool:
        """
        Check if a granted permission matches a required permission.

        Supports wildcards:
        - app.*:* matches app.model:action
        - app.model:* matches app.model:action
        - exact match: app.model:action

        Args:
            required: Required permission (e.g., 'notification.notification_template:create')
            granted: Granted permission (may contain wildcards)

        Returns:
            True if granted permission matches required permission
        """
        req_app, req_model, req_action = cls.parse_permission(required)
        grant_app, grant_model, grant_action = cls.parse_permission(granted)

        if not all([req_app, req_model, req_action]):
            return False

        if not all([grant_app, grant_model, grant_action]):
            return False

        # Check app match
        if grant_app != '*' and grant_app != req_app:
            return False

        # Check model match
        if grant_model != '*' and grant_model != req_model:
            return False

        # Check action match
        if grant_action != '*' and grant_action != req_action:
            return False

        return True


# Convenience instance
permission_generator = PermissionGenerator()