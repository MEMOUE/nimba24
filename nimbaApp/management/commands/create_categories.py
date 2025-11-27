from django.core.management.base import BaseCommand
from nimbaApp.models import Categorie


class Command(BaseCommand):
    help = 'Crée les catégories par défaut'

    def handle(self, *args, **options):
        categories_defaut = [
            ('politique', 'Actualités politiques du Nimba', 1),
            ('societe', 'Vie sociale et communautaire', 2),
            ('enquete', 'Enquêtes et reportages approfondis', 3),
            ('culture', 'Culture et traditions du Nimba', 4),
            ('diaspora', 'Nouvelles de la diaspora', 5),
            ('economie', 'Développement économique local', 6),
            ('sport', 'Sport et jeunesse', 7),
        ]

        for nom, description, ordre in categories_defaut:
            cat, created = Categorie.objects.get_or_create(
                nom=nom,
                defaults={'description': description, 'ordre': ordre}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Catégorie "{cat.get_nom_display()}" créée')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Catégorie "{cat.get_nom_display()}" existe déjà')
                )

        self.stdout.write(self.style.SUCCESS('\n✓ Toutes les catégories sont prêtes !'))