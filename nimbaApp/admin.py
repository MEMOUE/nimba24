from django.contrib import admin
from .models import Categorie, Article, Publicite, Newsletter


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_inscription', 'est_actif')
    list_filter = ('est_actif', 'date_inscription')
    search_fields = ('email',)
    date_hierarchy = 'date_inscription'
    readonly_fields = ('date_inscription',)

    actions = ['activer_abonnes', 'desactiver_abonnes']

    def activer_abonnes(self, request, queryset):
        queryset.update(est_actif=True)
        self.message_user(request, f"{queryset.count()} abonné(s) activé(s)")

    activer_abonnes.short_description = "Activer les abonnés sélectionnés"

    def desactiver_abonnes(self, request, queryset):
        queryset.update(est_actif=False)
        self.message_user(request, f"{queryset.count()} abonné(s) désactivé(s)")

    desactiver_abonnes.short_description = "Désactiver les abonnés sélectionnés"


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('get_nom_display', 'description', 'ordre')
    search_fields = ('nom',)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('titre', 'categorie', 'auteur', 'date_publication', 'est_publie', 'vues')
    list_filter = ('categorie', 'est_publie', 'date_publication')
    search_fields = ('titre', 'contenu')
    date_hierarchy = 'date_publication'
    readonly_fields = ('vues', 'date_modification')

    fieldsets = (
        ('Informations principales', {
            'fields': ('titre', 'sous_titre', 'categorie', 'auteur')
        }),
        ('Contenu', {
            'fields': ('contenu', 'image')
        }),
        ('Publication', {
            'fields': ('est_publie', 'est_a_la_une', 'date_publication')
        }),
        ('Statistiques', {
            'fields': ('vues', 'date_modification'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.auteur = request.user
        super().save_model(request, obj, form, change)


@admin.register(Publicite)
class PubliciteAdmin(admin.ModelAdmin):
    list_display = ('titre', 'position', 'date_debut', 'date_fin', 'est_active', 'nombre_clics')
    list_filter = ('position', 'est_active')
    search_fields = ('titre', 'description')
    date_hierarchy = 'date_debut'

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.auteur = request.user
        super().save_model(request, obj, form, change)