# =============================================================================
# CUSTOM MANAGER — Version recommandée (BONNE PRATIQUE)
# =============================================================================
#
# La clé : définir les méthodes sur le QuerySet, PAS sur le Manager.
# Django garantit que .filter() retourne toujours une instance de la MÊME
# sous-classe que self. Donc si self est un BlogPostQuerySet, .filter()
# retourne un BlogPostQuerySet — et le chaînage est possible à l'infini.

from django.db import models
from django.contrib.auth.models import User


# --- PostCategory : les catégories disponibles pour un article ---

class PostCategory(models.TextChoices):
    TECH = 'TECH', 'Technologie'
    LIFESTYLE = 'LIFESTYLE', 'Lifestyle'
    TUTORIAL = 'TUTORIAL', 'Tutoriel'
    NEWS = 'NEWS', 'Actualité'


# =============================================================================
# LA BONNE PRATIQUE : hériter de models.QuerySet
# =============================================================================

class BlogPostQuerySet(models.QuerySet):

    def published(self):
        """Retourne uniquement les articles publiés."""
        return self.filter(published=True)
        # ^^^ self est une instance de BlogPostQuerySet.
        #     .filter() sur un QuerySet retourne TOUJOURS une instance
        #     de la même sous-classe que self.
        #     Donc ici : .filter() retourne un BlogPostQuerySet.
        #     by_category() EXISTE sur BlogPostQuerySet → chaînage possible ✅

    def by_category(self, category):
        """Filtre par catégorie — chaînable avec published()."""
        return self.filter(category=category)


# as_manager() crée un Manager à partir du QuerySet.
# Toutes les méthodes du QuerySet sont automatiquement exposées sur objects.
BlogPostManager = BlogPostQuerySet.as_manager()


# =============================================================================
# LE CHAÎNAGE — ce qui se passe à l'exécution
# =============================================================================
#
#   BlogPost.objects                  # → instance de BlogPostQuerySet ✅
#                                     #   (as_manager() + Django's default QS)
#
#   BlogPost.objects
#           .published()              # → instance de BlogPostQuerySet ✅
#                                     #   filter() préserve la sous-classe
#
#   BlogPost.objects
#           .published()
#           .by_category('TECH')      # → instance de BlogPostQuerySet ✅
#                                     #   chaînage infini possible !


# =============================================================================
# Le modèle
# =============================================================================

class BlogPost(models.Model):
    title = models.CharField(max_length=200, verbose_name="Titre")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug")
    content = models.TextField(verbose_name="Contenu")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Auteur")
    published = models.BooleanField(default=False, verbose_name="Publié")
    category = models.CharField(max_length=10, choices=PostCategory, verbose_name="Catégorie")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")

    objects = BlogPostManager  # ← Le manager issu du QuerySet

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# =============================================================================
# Exemples d'utilisation (à coller dans le shell Django) :
# =============================================================================
#
#   BlogPost.objects.published()                     # tous les publiés
#   BlogPost.objects.by_category('TECH')             # tous les articles TECH
#   BlogPost.objects.published().by_category('TECH') # ✅ chaînage — publiés ET TECH
#   BlogPost.objects.by_category('NEWS').published() # ✅ chaînage — dans l'autre sens
