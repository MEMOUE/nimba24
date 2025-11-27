from django.urls import path
from . import views

app_name = 'nimbaApp'

urlpatterns = [
    # Pages publiques
    path('', views.home, name='home'),
    path('categorie/<str:categorie>/', views.categorie_view, name='categorie'),
    path('article/<int:id>/', views.article_detail, name='article_detail'),

    # Authentification
    path('connexion/', views.connexion, name='connexion'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard propriétaire
    path('dashboard/', views.dashboard, name='dashboard'),
    path('creer-article/', views.creer_article, name='creer_article'),
    path('creer-publicite/', views.creer_publicite, name='creer_publicite'),

    # Listes
    path('liste-articles/', views.liste_articles, name='liste_articles'),
    path('liste-publicites/', views.liste_publicites, name='liste_publicites'),

    # Modification et suppression
    path('modifier-article/<int:id>/', views.modifier_article, name='modifier_article'),
    path('supprimer-article/<int:id>/', views.supprimer_article, name='supprimer_article'),
    path('modifier-publicite/<int:id>/', views.modifier_publicite, name='modifier_publicite'),
    path('supprimer-publicite/<int:id>/', views.supprimer_publicite, name='supprimer_publicite'),

    # Publicités
    path('publicite/<int:id>/clic/', views.clic_publicite, name='clic_publicite'),
]