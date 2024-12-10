from django.core.management.base import BaseCommand
from api.telegram_bot import main


class Command(BaseCommand):
    help = 'Inicia el bot de Telegram'

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando el bot de Telegram...")
        main()
