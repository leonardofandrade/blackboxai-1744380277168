from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Sets the admin password'

    def handle(self, *args, **kwargs):
        try:
            admin = User.objects.get(username='admin')
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Successfully set admin password'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Admin user does not exist'))
