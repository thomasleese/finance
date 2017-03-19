from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from finance.models import Profile
from finance.importer import Importer


class Command(BaseCommand):
    help = 'Import an OFX file.'

    def add_arguments(self, parser):
        parser.add_argument('username')
        parser.add_argument('filename', nargs='+')

    def handle(self, *args, **kwargs):
        user = User.objects.get(username=kwargs['username'])
        profile = Profile.objects.get(user=user)

        for filename in kwargs['filename']:
            importer = Importer(profile, filename)
            importer.run()

            self.stdout.write(self.style.SUCCESS(filename))
