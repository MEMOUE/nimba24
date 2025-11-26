from django.apps import AppConfig


class NimbaappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nimbaApp'

    def ready(self):
        """Créer les catégories par défaut au démarrage de l'application"""
        # Import ici pour éviter les problèmes de circular imports
        from .models import Categorie

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
            Categorie.objects.get_or_create(
                nom=nom,
                defaults={'description': description, 'ordre': ordre}
            )