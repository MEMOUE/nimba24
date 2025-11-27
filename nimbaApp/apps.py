from django.apps import AppConfig


class NimbaappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nimbaApp'

    def ready(self):
        """Créer les catégories par défaut au démarrage de l'application"""
        # Ne rien faire ici pour éviter les problèmes lors des migrations
        pass