# Custom Manager Django — Démonstration pédagogique

Projet Django illustrant la différence entre une **mauvaise pratique** et une **bonne pratique** lors de la création d'un custom manager.

## Le problème

Hériter de `models.Manager` casse le chaînage des méthodes custom :

```python
BlogPost.objects.published().by_category('TECH')  # ❌ AttributeError
```

`published()` retourne un `models.QuerySet` ordinaire, qui ne connaît pas `by_category()`.

## La solution

Hériter de `models.QuerySet` et utiliser `as_manager()` :

```python
BlogPost.objects.published().by_category('TECH')  # ✅ BlogPostQuerySet
```

`filter()` préserve toujours la sous-classe du QuerySet, donc le chaînage est possible à l'infini.

## Fichiers

| Fichier | Rôle |
|---|---|
| `blog/models_naive.py` | Mauvaise pratique — `BlogPostManager(models.Manager)` |
| `blog/models.py` | Bonne pratique — `BlogPostQuerySet(models.QuerySet)` + `as_manager()` |

## Installation

```bash
python -m venv venv && source venv/bin/activate
pip install django
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
# custom-manager-django
