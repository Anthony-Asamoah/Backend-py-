from asgiref.sync import async_to_sync
from django.core.management.base import BaseCommand

from main.utils.logger import log
from notification.schemas.notification_template import NotificationTemplateCreate
from notification.use_cases.notification_template import notification_template_service


class Command(BaseCommand):
    help = 'Seed database with notification templates for user onboarding and authentication'

    def handle(self, *args, **options):
        async_to_sync(self.async_handle)(*args, **options)

    async def async_handle(self, *args, **options):
        """Main seeding logic."""
        self.stdout.write(self.style.SUCCESS('Starting notification template seeding...'))

        # Define template data
        templates_data = self.get_templates_data()

        # Create templates
        created_count = 0
        skipped_count = 0

        for template_data in templates_data:
            try:
                # Check if template already exists
                existing = await notification_template_service.get_by_name(template_data['name'])

                if existing:
                    log.debug(f'Template already exists: {template_data["name"]}')
                    self.stdout.write(f'  - Skipped: {template_data["name"]} (already exists)')
                    skipped_count += 1
                else:
                    # Create new template
                    payload = NotificationTemplateCreate(**template_data)
                    await notification_template_service.create(payload)
                    log.info(f'Created template: {template_data["name"]}')
                    self.stdout.write(self.style.SUCCESS(f'  - Created: {template_data["name"]}'))
                    created_count += 1

            except Exception as e:
                log.error(f'Error creating template {template_data["name"]}: {e}')
                self.stdout.write(self.style.ERROR(f'  - Error: {template_data["name"]} - {str(e)}'))

        # Print summary
        self.stdout.write(self.style.SUCCESS(f'\nSeeding completed!'))
        self.stdout.write(f'  Created: {created_count}')
        self.stdout.write(f'  Skipped: {skipped_count}')
        self.stdout.write(f'  Total: {len(templates_data)}')

    def get_templates_data(self):
        """Return list of template data dictionaries."""
        return [
            # 1. User Onboarding Template
            {
                "name": "USER-ONBOARDING",
                "subject": "Welcome to {{platform_name}}, {{user_name}}!",
                "heading": "Welcome Aboard!",
                "email_content": """
                    <p>Hi <strong>{{user_name}}</strong>,</p>

                    <p>Thank you for joining <strong>{{platform_name}}</strong>! We're excited to have you on board.</p>

                    <p>Your account has been successfully created with the following details:</p>
                    <ul>
                        <li><strong>Email:</strong> {{email}}</li>
                    </ul>

                    <p>Here are your next steps:</p>
                    <ol>
                        <li>Verify your email address</li>
                        <li>Complete your profile</li>
                        <li>Explore the platform features</li>
                    </ol>

                    <p>If you have any questions, feel free to reach out to our support team.</p>

                    <p>Best regards,<br>The {{platform_name}} Team</p>
                """,
                "short_content": "Welcome {{user_name}}! Your account on {{platform_name}} is ready. Verify your email to get started."
            },

            # 2. Email Verification Template
            {
                "name": "EMAIL-VERIFICATION",
                "subject": "Verify Your Email Address",
                "heading": "Verify Your Email",
                "email_content": """
                    <p>Hi <strong>{{user_name}}</strong>,</p>

                    <p>Thank you for signing up! To complete your registration, please verify your email address.</p>

                    <p style="margin: 30px 0; text-align: center;">
                        <strong>Verification Code:</strong><br>
                        <span style="font-size: 32px; letter-spacing: 5px; font-weight: bold; color: #007BFF;">{{verification_code}}</span>
                    </p>

                    <p>This verification code will expire in <strong>{{expiry_time}}</strong>.</p>

                    <p>If you didn't create an account, you can safely ignore this email.</p>

                    <p>Best regards,<br>The {{platform_name}} Team</p>
                """,
                "short_content": "Your verification code is {{verification_code}}. Valid for {{expiry_time}}."
            },

            # 3. Password Reset Template
            {
                "name": "PASSWORD-RESET",
                "subject": "Reset Your Password",
                "heading": "Password Reset Request",
                "email_content": """
                    <p>Hi <strong>{{user_name}}</strong>,</p>

                    <p>We received a request to reset your password for your <strong>{{platform_name}}</strong> account.</p>

                    <p>This link will expire in <strong>{{expiry_time}}</strong>.</p>

                    <p><strong>Important:</strong> If you didn't request a password reset, please ignore this email or contact support if you have concerns.</p>

                    <p>Best regards,<br>The {{platform_name}} Team</p>
                """,
                "short_content": "Reset your password using the link provided. Link expires in {{expiry_time}}."
            },

            # 4. Password Changed Confirmation Template
            {
                "name": "PASSWORD-CHANGED",
                "subject": "Your Password Has Been Changed",
                "heading": "Password Changed Successfully",
                "email_content": """
                    <p>Hi <strong>{{user_name}}</strong>,</p>

                    <p>This is a confirmation that your password for your <strong>{{platform_name}}</strong> account has been successfully changed.</p>

                    <p><strong>Change Details:</strong></p>
                    <ul>
                        <li><strong>Time:</strong> {{change_time}}</li>
                    </ul>

                    <div style="padding: 15px; background-color: #fff3cd; border-left: 4px solid #ffc107; border-radius: 5px; margin: 20px 0;">
                        <strong>⚠️ Didn't change your password?</strong><br>
                        Contact us immediately at: <strong>{{support_email}}</strong>
                    </div>

                    <p>For your security, we recommend:</p>
                    <ul>
                        <li>Using a strong, unique password</li>
                        <li>Never sharing your password with anyone</li>
                        <li>Enabling two-factor authentication if available</li>
                    </ul>

                    <p>Best regards,<br>The {{platform_name}} Team</p>
                """,
                "short_content": "Your password was changed at {{change_time}}. If this wasn't you, contact {{support_email}} immediately."
            },

            # 5. Account Deleted Template
            {
                "name": "ACCOUNT-DELETED",
                "subject": "Your {{platform_name}} Account Has Been Deleted",
                "heading": "Account Deletion Confirmation",
                "email_content": """
                    <p>Hi <strong>{{user_name}}</strong>,</p>

                    <p>This is to confirm that your <strong>{{platform_name}}</strong> account has been deleted on <strong>{{deletion_date}}</strong>.</p>

                    <p><strong>Data Retention:</strong></p>
                    <ul>
                        <li>Your personal data will be removed according to our privacy policy</li>
                        <li>Some anonymized data may be retained for legal and analytical purposes</li>
                        <li>Deletion will be completed within 30 days</li>
                    </ul>

                    <div style="padding: 15px; background-color: #f8d7da; border-left: 4px solid #dc3545; border-radius: 5px; margin: 20px 0;">
                        <strong>⚠️ Didn't request account deletion?</strong><br>
                        Contact us immediately at: <strong>{{support_email}}</strong>
                    </div>

                    <p>If you change your mind, you may be able to recover your account within the next 30 days by contacting support.</p>

                    <p>We're sorry to see you go. If you have any feedback about your experience, we'd love to hear from you.</p>

                    <p>Best regards,<br>The {{platform_name}} Team</p>
                """,
                "short_content": "Your account was deleted on {{deletion_date}}. Contact {{support_email}} if this wasn't you."
            },

            # 6. Role Assigned Template
            {
                "name": "ROLE-ASSIGNED",
                "subject": "New Roles Assigned - {{platform_name}}",
                "heading": "Your Permissions Have Been Updated",
                "email_content": """
                    <p>Hi <strong>{{user_name}}</strong>,</p>

                    <p>Your account permissions on <strong>{{platform_name}}</strong> have been updated.</p>

                    <p><strong>New Roles Assigned:</strong></p>
                    <div style="padding: 15px; background-color: #d4edda; border-left: 4px solid #28a745; border-radius: 5px; margin: 20px 0;">
                        {{roles_assigned}}
                    </div>

                    <p><strong>What this means:</strong></p>
                    <p>{{responsibilities}}</p>

                    <p><strong>Assigned by:</strong> {{assigned_by}}</p>
                    <p><strong>Date:</strong> {{assignment_date}}</p>

                    <p>With these new roles, you now have access to additional features and capabilities on the platform. Please review your new permissions and reach out if you have any questions.</p>

                    <p>If you believe this change was made in error, please contact your administrator or our support team.</p>

                    <p>Best regards,<br>The {{platform_name}} Team</p>
                """,
                "short_content": "New roles assigned: {{roles_assigned}} by {{assigned_by}}."
            },

            # 7. Role Removed Template
            {
                "name": "ROLE-REMOVED",
                "subject": "Roles Removed - {{platform_name}}",
                "heading": "Your Permissions Have Changed",
                "email_content": """
                    <p>Hi <strong>{{user_name}}</strong>,</p>

                    <p>Your account permissions on <strong>{{platform_name}}</strong> have been updated.</p>

                    <p><strong>Roles Removed:</strong></p>
                    <div style="padding: 15px; background-color: #fff3cd; border-left: 4px solid #ffc107; border-radius: 5px; margin: 20px 0;">
                        {{roles_removed}}
                    </div>

                    <p><strong>Impact:</strong></p>
                    <p>{{impact_explanation}}</p>

                    <p><strong>Removed by:</strong> {{removed_by}}</p>
                    <p><strong>Date:</strong> {{removal_date}}</p>

                    <p>Some features and capabilities may no longer be accessible with your current permissions. If you need access to these features, please contact your administrator.</p>

                    <p>If you believe this change was made in error, please contact your administrator or our support team immediately.</p>

                    <p>Best regards,<br>The {{platform_name}} Team</p>
                """,
                "short_content": "Roles removed: {{roles_removed}} by {{removed_by}}."
            },
        ]