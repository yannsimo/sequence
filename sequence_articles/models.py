from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


def resize_image(image_field):
    """
    Redimensionne une image pour conserver un bon rapport hauteur/largeur
    sans dépasser une largeur maximale.
    """
    if not image_field:
        return image_field

    img = Image.open(image_field)

    # Définir les dimensions cibles (tout en préservant le ratio)
    max_width = 1200
    if img.width > max_width:
        ratio = max_width / float(img.width)
        new_height = int(float(img.height) * float(ratio))
        img = img.resize((max_width, new_height), Image.LANCZOS)

    # Réenregistrer l'image
    output = BytesIO()

    # Conserver le format d'origine si possible
    if img.format:
        format_name = img.format
    else:
        format_name = 'JPEG'

    # Sauvegarde avec la bonne qualité
    if format_name == 'JPEG':
        img.save(output, format=format_name, quality=85)
    else:
        img.save(output, format=format_name)

    output.seek(0)

    # Déterminer le type de contenu
    content_type = f'image/{format_name.lower()}' if format_name != 'PNG' else 'image/png'

    # Créer un nouveau fichier pour Django
    return InMemoryUploadedFile(
        output,
        'ImageField',
        f"{image_field.name.split('/')[-1]}",
        content_type,
        sys.getsizeof(output),
        None
    )


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Article(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    summary = models.TextField(help_text="Bref résumé de l'article pour la page d'accueil")
    content = models.TextField()
    featured_image = models.ImageField(upload_to='articles/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='articles')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False, help_text="Article mis en avant sur la page d'accueil")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(default=timezone.now)
    views_count = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        # Création du slug si nécessaire
        if not self.slug:
            self.slug = slugify(self.title)

        # Redimensionner l'image si elle existe et a été modifiée
        if self.featured_image and hasattr(self.featured_image, 'file'):
            try:
                self.featured_image = resize_image(self.featured_image)
            except Exception as e:
                print(f"Erreur lors du redimensionnement de l'image: {e}")

        # Gestion de l'article en vedette
        if self.is_featured:
            # S'assurer qu'il n'y a qu'un seul article en vedette
            Article.objects.filter(is_featured=True).exclude(pk=self.pk).update(is_featured=False)

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Retourne l'URL canonique pour accéder à l'article"""
        from django.urls import reverse
        return reverse('article_detail', kwargs={'slug': self.slug})

    def increment_views(self):
        """Incrémente le compteur de vues de l'article"""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class ArticleImage(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='articles/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        # Redimensionner l'image si elle existe et a été modifiée
        if self.image and hasattr(self.image, 'file'):
            try:
                self.image = resize_image(self.image)
            except Exception as e:
                print(f"Erreur lors du redimensionnement de l'image: {e}")

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image pour {self.article.title}"


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Commentaire par {self.author_name} sur {self.article.title}'