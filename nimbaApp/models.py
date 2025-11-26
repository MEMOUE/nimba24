from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Categorie(models.Model):
    CATEGORIES_CHOICES = [
        ('politique', 'Politique'),
        ('societe', 'Société'),
        ('enquete', 'Enquête & Reportage'),
        ('culture', 'Culture & Tradition du Nimba'),
        ('diaspora', 'Diaspora du Nimba'),
        ('economie', 'Économie Locale'),
        ('sport', 'Sport & Jeunesse'),
    ]

    nom = models.CharField(max_length=50, choices=CATEGORIES_CHOICES, unique=True)
    description = models.TextField(blank=True)
    ordre = models.IntegerField(default=0, help_text="Ordre d'affichage")

    def __str__(self):
        return self.get_nom_display()

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['ordre', 'nom']


class Article(models.Model):
    titre = models.CharField(max_length=200, verbose_name='Titre')
    sous_titre = models.CharField(max_length=300, blank=True, verbose_name='Sous-titre')
    contenu = models.TextField(verbose_name='Contenu')
    image = models.ImageField(upload_to='articles/', blank=True, null=True, verbose_name='Image')
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='articles',
                                  verbose_name='Catégorie')
    date_publication = models.DateTimeField(default=timezone.now, verbose_name='Date de publication')
    date_modification = models.DateTimeField(auto_now=True, verbose_name='Dernière modification')
    est_publie = models.BooleanField(default=True, verbose_name='Publié')
    est_a_la_une = models.BooleanField(default=False, verbose_name='À la une')
    vues = models.IntegerField(default=0, verbose_name='Nombre de vues')

    def __str__(self):
        return self.titre

    class Meta:
        ordering = ['-date_publication']
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'


class Publicite(models.Model):
    POSITION_CHOICES = [
        ('header', 'Bannière en haut'),
        ('sidebar', 'Barre latérale'),
        ('footer', 'Bannière en bas'),
        ('article', 'Dans les articles'),
    ]

    titre = models.CharField(max_length=200, verbose_name='Titre de la publicité')
    description = models.TextField(blank=True, verbose_name='Description')
    image = models.ImageField(upload_to='publicites/', verbose_name='Image')
    lien = models.URLField(blank=True, verbose_name='Lien (URL)')
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, default='sidebar', verbose_name='Position')
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='publicites')
    date_debut = models.DateTimeField(verbose_name='Date de début')
    date_fin = models.DateTimeField(verbose_name='Date de fin')
    est_active = models.BooleanField(default=True, verbose_name='Active')
    nombre_clics = models.IntegerField(default=0, verbose_name='Nombre de clics')
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre

    def est_valide(self):
        """Vérifie si la publicité est dans sa période de validité"""
        now = timezone.now()
        return self.est_active and self.date_debut <= now <= self.date_fin

    class Meta:
        ordering = ['-date_creation']
        verbose_name = 'Publicité'
        verbose_name_plural = 'Publicités'