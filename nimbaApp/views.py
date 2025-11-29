from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Article, Categorie, Publicite, Newsletter
from .email_utils import envoyer_newsletter_nouvel_article, envoyer_email_bienvenue_newsletter
import logging

logger = logging.getLogger(__name__)


def is_staff_user(user):
    """Vérifie si l'utilisateur est un membre du staff"""
    return user.is_staff


@require_POST
def inscription_newsletter(request):
    """Inscription à la newsletter"""
    email = request.POST.get('email', '').strip()

    if not email:
        messages.error(request, 'Veuillez entrer une adresse email.')
        return redirect(request.META.get('HTTP_REFERER', 'nimbaApp:home'))

    try:
        # Vérifier si l'email existe déjà
        newsletter, created = Newsletter.objects.get_or_create(
            email=email,
            defaults={'est_actif': True}
        )

        if created:
            # Envoyer l'email de bienvenue
            try:
                envoyer_email_bienvenue_newsletter(email)
                logger.info(f"Email de bienvenue envoyé à {email}")
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi de l'email de bienvenue: {str(e)}")

            messages.success(request,
                             f'✅ Merci ! Vous êtes maintenant abonné à notre newsletter avec l\'adresse {email}')
        else:
            if newsletter.est_actif:
                messages.info(request, f'📧 Vous êtes déjà abonné avec l\'adresse {email}')
            else:
                # Réactiver l'abonnement
                newsletter.est_actif = True
                newsletter.save()
                messages.success(request, f'✅ Votre abonnement a été réactivé avec l\'adresse {email}')
    except Exception as e:
        logger.error(f"Erreur lors de l'inscription à la newsletter: {str(e)}")
        messages.error(request, 'Une erreur est survenue. Veuillez réessayer.')

    return redirect(request.META.get('HTTP_REFERER', 'nimbaApp:home'))


def home(request):
    """Page d'accueil publique"""
    # Article principal à la une (pour le carrousel principal)
    article_une = Article.objects.filter(est_publie=True, est_a_la_une=True).first()
    if not article_une:
        article_une = Article.objects.filter(est_publie=True).first()

    # Tous les articles récents (excluant l'article principal)
    if article_une:
        articles_recents = Article.objects.filter(est_publie=True).exclude(id=article_une.id)[:10]
    else:
        articles_recents = Article.objects.filter(est_publie=True)[:10]

    # Articles par catégorie
    categories = Categorie.objects.all()
    articles_par_categorie = {}
    for cat in categories:
        articles = Article.objects.filter(categorie=cat, est_publie=True)[:3]
        if articles:
            articles_par_categorie[cat] = articles

    # Publicités actives
    now = timezone.now()
    publicites_header = Publicite.objects.filter(
        position='header',
        est_active=True,
        date_debut__lte=now,
        date_fin__gte=now
    ).first()

    publicites_sidebar = Publicite.objects.filter(
        position='sidebar',
        est_active=True,
        date_debut__lte=now,
        date_fin__gte=now
    )[:3]

    context = {
        'article_une': article_une,
        'articles_recents': articles_recents,
        'articles_par_categorie': articles_par_categorie,
        'categories': categories,
        'publicites_header': publicites_header,
        'publicites_sidebar': publicites_sidebar,
    }
    return render(request, 'home.html', context)


def categorie_view(request, categorie):
    """Vue pour afficher les articles d'une catégorie"""
    cat = get_object_or_404(Categorie, nom=categorie)
    articles = Article.objects.filter(categorie=cat, est_publie=True)

    context = {
        'categorie': cat,
        'articles': articles,
        'categories': Categorie.objects.all(),
    }
    return render(request, 'categorie.html', context)


def article_detail(request, id):
    """Vue détaillée d'un article"""
    article = get_object_or_404(Article, id=id, est_publie=True)

    # Incrémenter les vues
    article.vues += 1
    article.save()

    # Articles similaires
    articles_similaires = Article.objects.filter(
        categorie=article.categorie,
        est_publie=True
    ).exclude(id=article.id)[:3]

    # Publicités
    now = timezone.now()
    publicites_article = Publicite.objects.filter(
        position='article',
        est_active=True,
        date_debut__lte=now,
        date_fin__gte=now
    ).first()

    context = {
        'article': article,
        'articles_similaires': articles_similaires,
        'categories': Categorie.objects.all(),
        'publicite_article': publicites_article,
    }
    return render(request, 'article_detail.html', context)


def connexion(request):
    """Page de connexion pour le propriétaire"""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('nimbaApp:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, 'Connexion réussie !')
            return redirect('nimbaApp:dashboard')
        else:
            messages.error(request, 'Identifiants incorrects ou accès non autorisé.')

    return render(request, 'connexion.html')


@login_required
@user_passes_test(is_staff_user)
def dashboard(request):
    """Dashboard du propriétaire"""
    articles_count = Article.objects.filter(auteur=request.user).count()
    publicites_count = Publicite.objects.filter(auteur=request.user).count()
    articles_recents = Article.objects.filter(auteur=request.user)[:5]
    total_vues = sum(article.vues for article in Article.objects.filter(auteur=request.user))

    # Statistique newsletter
    newsletter_count = Newsletter.objects.filter(est_actif=True).count()

    context = {
        'articles_count': articles_count,
        'publicites_count': publicites_count,
        'articles_recents': articles_recents,
        'total_vues': total_vues,
        'newsletter_count': newsletter_count,
    }
    return render(request, 'dashboard.html', context)


@login_required
@user_passes_test(is_staff_user)
def liste_articles(request):
    """Liste complète des articles du propriétaire"""
    articles = Article.objects.filter(auteur=request.user).order_by('-date_publication')

    context = {
        'articles': articles,
    }
    return render(request, 'liste_articles.html', context)


@login_required
@user_passes_test(is_staff_user)
def liste_publicites(request):
    """Liste complète des publicités du propriétaire"""
    publicites = Publicite.objects.filter(auteur=request.user).order_by('-date_creation')

    context = {
        'publicites': publicites,
    }
    return render(request, 'liste_publicites.html', context)


@login_required
@user_passes_test(is_staff_user)
def creer_article(request):
    """Page de création d'article"""
    if request.method == 'POST':
        titre = request.POST.get('titre')
        sous_titre = request.POST.get('sous_titre')
        contenu = request.POST.get('contenu')
        categorie_id = request.POST.get('categorie')
        image = request.FILES.get('image')
        est_a_la_une = request.POST.get('est_a_la_une') == 'on'
        est_publie = request.POST.get('est_publie') == 'on'

        if titre and contenu and categorie_id:
            categorie = get_object_or_404(Categorie, id=categorie_id)
            article = Article.objects.create(
                titre=titre,
                sous_titre=sous_titre,
                contenu=contenu,
                categorie=categorie,
                image=image,
                auteur=request.user,
                est_a_la_une=est_a_la_une,
                est_publie=est_publie,
            )

            # Envoyer la newsletter si l'article est publié
            if est_publie:
                try:
                    nb_abonnes = envoyer_newsletter_nouvel_article(article)
                    if nb_abonnes > 0:
                        messages.success(request,
                                         f'Article créé avec succès ! Newsletter envoyée à {nb_abonnes} abonné(s).')
                        logger.info(f"Article {article.id} créé et newsletter envoyée à {nb_abonnes} abonnés")
                    else:
                        messages.success(request, 'Article créé avec succès ! (Aucun abonné à la newsletter)')
                        logger.info(f"Article {article.id} créé mais aucun abonné actif")
                except Exception as e:
                    logger.error(f"Erreur lors de l'envoi de la newsletter pour l'article {article.id}: {str(e)}")
                    messages.warning(request,
                                     f'Article créé avec succès, mais erreur lors de l\'envoi de la newsletter: {str(e)}')
            else:
                messages.success(request, 'Article créé avec succès ! (Non publié, newsletter non envoyée)')

            return redirect('nimbaApp:dashboard')
        else:
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')

    categories = Categorie.objects.all()
    context = {'categories': categories}
    return render(request, 'creer_article.html', context)


@login_required
@user_passes_test(is_staff_user)
def creer_publicite(request):
    """Page de création de publicité"""
    if request.method == 'POST':
        titre = request.POST.get('titre')
        description = request.POST.get('description')
        lien = request.POST.get('lien')
        position = request.POST.get('position')
        image = request.FILES.get('image')
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')

        if titre and image and position and date_debut and date_fin:
            publicite = Publicite.objects.create(
                titre=titre,
                description=description,
                lien=lien,
                position=position,
                image=image,
                date_debut=date_debut,
                date_fin=date_fin,
                auteur=request.user,
            )
            messages.success(request, 'Publicité créée avec succès !')
            return redirect('nimbaApp:dashboard')
        else:
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')

    return render(request, 'creer_publicite.html')


@login_required
def logout_view(request):
    """Déconnexion"""
    logout(request)
    messages.success(request, 'Déconnexion réussie.')
    return redirect('nimbaApp:home')


def clic_publicite(request, id):
    """Enregistrer un clic sur une publicité"""
    publicite = get_object_or_404(Publicite, id=id)
    publicite.nombre_clics += 1
    publicite.save()

    if publicite.lien:
        return redirect(publicite.lien)
    return redirect('nimbaApp:home')


@login_required
@user_passes_test(is_staff_user)
def modifier_article(request, id):
    """Page de modification d'article"""
    article = get_object_or_404(Article, id=id, auteur=request.user)

    # Sauvegarder l'état de publication avant modification
    etait_publie = article.est_publie

    if request.method == 'POST':
        article.titre = request.POST.get('titre')
        article.sous_titre = request.POST.get('sous_titre')
        article.contenu = request.POST.get('contenu')

        categorie_id = request.POST.get('categorie')
        if categorie_id:
            article.categorie = get_object_or_404(Categorie, id=categorie_id)

        # Gestion de l'image
        if request.FILES.get('image'):
            article.image = request.FILES.get('image')

        article.est_a_la_une = request.POST.get('est_a_la_une') == 'on'
        article.est_publie = request.POST.get('est_publie') == 'on'

        article.save()

        # Envoyer la newsletter si l'article vient d'être publié
        if article.est_publie and not etait_publie:
            try:
                nb_abonnes = envoyer_newsletter_nouvel_article(article)
                if nb_abonnes > 0:
                    messages.success(request,
                                     f'Article modifié et publié ! Newsletter envoyée à {nb_abonnes} abonné(s).')
                    logger.info(f"Article {article.id} publié et newsletter envoyée à {nb_abonnes} abonnés")
                else:
                    messages.success(request, 'Article modifié et publié ! (Aucun abonné à la newsletter)')
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi de la newsletter pour l'article {article.id}: {str(e)}")
                messages.warning(request,
                                 f'Article modifié avec succès, mais erreur lors de l\'envoi de la newsletter: {str(e)}')
        else:
            messages.success(request, 'Article modifié avec succès !')

        return redirect('nimbaApp:liste_articles')

    categories = Categorie.objects.all()
    context = {
        'article': article,
        'categories': categories,
    }
    return render(request, 'modifier_article.html', context)


@login_required
@user_passes_test(is_staff_user)
def supprimer_article(request, id):
    """Supprimer un article"""
    article = get_object_or_404(Article, id=id, auteur=request.user)

    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Article supprimé avec succès !')
        return redirect('nimbaApp:liste_articles')

    return render(request, 'confirmer_suppression_article.html', {'article': article})


@login_required
@user_passes_test(is_staff_user)
def modifier_publicite(request, id):
    """Page de modification de publicité"""
    publicite = get_object_or_404(Publicite, id=id, auteur=request.user)

    if request.method == 'POST':
        publicite.titre = request.POST.get('titre')
        publicite.description = request.POST.get('description')
        publicite.lien = request.POST.get('lien')
        publicite.position = request.POST.get('position')
        publicite.date_debut = request.POST.get('date_debut')
        publicite.date_fin = request.POST.get('date_fin')
        publicite.est_active = request.POST.get('est_active') == 'on'

        # Gestion de l'image
        if request.FILES.get('image'):
            publicite.image = request.FILES.get('image')

        publicite.save()
        messages.success(request, 'Publicité modifiée avec succès !')
        return redirect('nimbaApp:liste_publicites')

    # Formater les dates pour les inputs datetime-local
    date_debut_formatted = publicite.date_debut.strftime('%Y-%m-%dT%H:%M') if publicite.date_debut else ''
    date_fin_formatted = publicite.date_fin.strftime('%Y-%m-%dT%H:%M') if publicite.date_fin else ''

    context = {
        'publicite': publicite,
        'date_debut_formatted': date_debut_formatted,
        'date_fin_formatted': date_fin_formatted,
    }
    return render(request, 'modifier_publicite.html', context)


@login_required
@user_passes_test(is_staff_user)
def supprimer_publicite(request, id):
    """Supprimer une publicité"""
    publicite = get_object_or_404(Publicite, id=id, auteur=request.user)

    if request.method == 'POST':
        publicite.delete()
        messages.success(request, 'Publicité supprimée avec succès !')
        return redirect('nimbaApp:liste_publicites')

    return render(request, 'confirmer_suppression_publicite.html', {'publicite': publicite})