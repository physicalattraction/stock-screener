from django.conf import settings
from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    def __init__(self, stdout=None, stderr=None, no_color=False):
        super().__init__(stdout, stderr, no_color)
        self.settings = None

    def handle(self, *args, **options):
        self.settings = options.get('settings')
        call_command('runserver', str(options['port']), '--settings', self.settings)

    def add_arguments(self, parser):
        default_port = getattr(settings, 'RUNSERVER_PORT', 8000)
        parser.add_argument('--port', dest='port', type=int, action='store', default=default_port)
