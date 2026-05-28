# =============================================================================
# CUSTOM MANAGER — Version naïve (MAUVAISE PRATIQUE)
# =============================================================================
#
# Ce fichier est une démonstration pédagogique.
# Il n'est PAS importé par Django et ne génère PAS de migration.
# Son unique rôle est de montrer le problème de chaînage.

from django.db import models
from django.contrib.auth.models import User


# --- PostCategory : les catégories disponibles pour un article ---

class PostCategory(models.TextChoices):
    TECH = 'TECH', 'Technologie'
    LIFESTYLE = 'LIFESTYLE', 'Lifestyle'
    TUTORIAL = 'TUTORIAL', 'Tutoriel'
    NEWS = 'NEWS', 'Actualité'


# =============================================================================
# LA MAUVAISE PRATIQUE : hériter directement de models.Manager
# =============================================================================

class BlogPostManager(models.Manager):
    def published(self):
        return self.get_queryset().filter(published=True)
        # ^^^ self est une instance de BlogPostManager.
        #     self.get_queryset() retourne une instance de models.QuerySet
        #     (la classe de base Django — PAS notre BlogPostManager).
        #     .filter() sur un models.QuerySet retourne aussi un models.QuerySet.
        #     by_category() n'existe PAS sur models.QuerySet.

    def by_category(self, category):
        return self.get_queryset().filter(category=category)


# =============================================================================
# LE PROBLÈME DE CHAÎNAGE — ce qui se passe à l'exécution
# =============================================================================
#
#   BlogPost.objects               # → instance de BlogPostManager
#                                  #   ✅ a .published() et .by_category()
#
#   BlogPost.objects
#           .published()           # → instance de models.QuerySet
#                                  #   ✅ a .filter(), .exclude(), .order_by()...
#                                  #   ❌ N'A PAS .by_category()
#
#   BlogPost.objects
#           .published()
#           .by_category('TECH')   # → AttributeError ❌
#                                  #   On a "quitté" BlogPostManager dès le
#                                  #   premier appel. published() a retourné
#                                  #   un models.QuerySet ordinaire, qui ne
#                                  #   connaît pas nos méthodes custom.
#
# CAUSE RACINE :
#   BlogPostManager et models.QuerySet sont deux classes DIFFÉRENTES et
#   INDÉPENDANTES. Une fois qu'une méthode du Manager retourne un QuerySet
#   de base, le chaînage vers les méthodes du Manager est impossible.

# =============================================================================
# Le modèle (identique à la bonne pratique pour la comparaison)
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

    objects = BlogPostManager()  # ← Le manager naïf

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
#   BlogPost.objects.published()                    # ✅ fonctionne
#   BlogPost.objects.by_category('TECH')            # ✅ fonctionne
#   BlogPost.objects.published().by_category('TECH')# ❌ AttributeError !
