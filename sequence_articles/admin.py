from django.contrib import admin
from django.contrib import admin
from .models import Category, Article, ArticleImage, Comment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    ordering = ('-created_at',)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'is_featured', 'category', 'published_at', 'views_count')
    list_filter = ('status', 'category', 'is_featured', 'created_at')
    search_fields = ('title', 'author__username', 'category__name')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-published_at',)
    readonly_fields = ('views_count',)
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'slug', 'author', 'category', 'summary', 'content', 'featured_image')
        }),
        ('Publication', {
            'fields': ('status', 'is_featured', 'published_at')
        }),
        ('Statistiques', {
            'fields': ('views_count',)
        }),
    )

@admin.register(ArticleImage)
class ArticleImageAdmin(admin.ModelAdmin):
    list_display = ('article', 'image', 'caption', 'order')
    ordering = ('order',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('article', 'author_name', 'author_email', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('author_name', 'author_email', 'content')
    ordering = ('-created_at',)
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = "Approuver les commentaires sélectionnés"

# Register your models here.
