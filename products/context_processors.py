from .models import Category


def shop_categories(request):
    """Makes the category list available in every template (for navbar/footer menus)."""
    return {'nav_categories': Category.objects.all()}
