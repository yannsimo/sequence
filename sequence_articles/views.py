from django.shortcuts import render , get_object_or_404
# views.py

from django.views.generic import ListView
from django.db.models import Q
from .models import Article, Category

class HomePageView(ListView):
    model = Article
    template_name = 'sequence/home.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Récupérer l'article en vedette
        context['featured_article'] = Article.objects.filter(
            status='published',
            is_featured=True
        ).first()
        # Récupérer les catégories pour le menu
        context['categories'] = Category.objects.all()
        return context

    def get_queryset(self):
        # Récupérer tous les articles publiés sauf celui en vedette
        return Article.objects.filter(
            status='published'
        ).exclude(
            is_featured=True
        ).order_by('-published_at')


def search_articles(request):
    query = request.GET.get('query', '')

    if query:
        results = Article.objects.filter(
            Q(title__icontains=query) |
            Q(summary__icontains=query) |
            Q(content__icontains=query),
            status='published'
        ).distinct()
    else:
        results = Article.objects.none()

    context = {
        'query': query,
        'results': results,
        'count': results.count(),
        'categories': Category.objects.all()  # Pour le menu
    }

    return render(request, 'sequence/search_results.html', context)

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    articles = category.articles.all()
    return render(request, "sequence/category_detail.html", {"category": category, "articles": articles})

# ✅ Vue pour afficher un article en détail
def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    return render(request, "sequence/article_detail.html", {"article": article})