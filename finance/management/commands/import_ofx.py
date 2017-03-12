from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from finance.importer import Importer


class Command(BaseCommand):
    help = 'Import an OFX file.'

    def add_arguments(self, parser):
        parser.add_argument('username')
        parser.add_argument('filename', nargs='+')

    def handle(self, *args, **kwargs):
        user = User.objects.get(username=kwargs['username'])

        for filename in kwargs['filename']:
            importer = Importer(user, filename)
            importer.run()

            self.stdout.write(self.style.SUCCESS(filename))
