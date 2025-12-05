from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Newsletter
import logging

logger = logging.getLogger(__name__)


def envoyer_newsletter_nouvel_article(article):
    """
    Envoie un email à tous les abonnés actifs de la newsletter
    lors de la publication d'un nouvel article
    """
    # Récupérer tous les abonnés actifs
    abonnes = Newsletter.objects.filter(est_actif=True)

    if not abonnes.exists():
        logger.info("Aucun abonné actif à la newsletter")
        return 0

    # Préparer la liste des emails
    emails_destinataires = [abonne.email for abonne in abonnes]

    # Sujet de l'email
    sujet = f"📰 Nouvel article : {article.titre}"

    # Contexte pour le template
    contexte = {
        'article': article,
        'site_url': 'http://127.0.0.1:8000',  # À remplacer par votre domaine en production
    }

    # Contenu HTML de l'email
    try:
        html_content = render_to_string('nouvel_article.html', contexte)
        text_content = strip_tags(html_content)

        # Créer l'email
        email = EmailMultiAlternatives(
            subject=sujet,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            bcc=emails_destinataires,  # Utiliser BCC pour la confidentialité
        )
        email.attach_alternative(html_content, "text/html")

        # Envoyer l'email
        email.send()

        logger.info(f"Newsletter envoyée à {len(emails_destinataires)} abonnés pour l'article '{article.titre}'")
        return len(emails_destinataires)

    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de la newsletter : {str(e)}")
        return 0


def envoyer_email_bienvenue_newsletter(email_abonne):
    """
    Envoie un email de bienvenue à un nouvel abonné
    """
    sujet = "🎉 Bienvenue à la newsletter de Nimba24"

    contexte = {
        'email': email_abonne,
        'site_url': 'http://127.0.0.1:8000',
    }

    try:
        html_content = render_to_string('emails/bienvenue_newsletter.html', contexte)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=sujet,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email_abonne],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        logger.info(f"Email de bienvenue envoyé à {email_abonne}")
        return True

    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email de bienvenue : {str(e)}")
        return False