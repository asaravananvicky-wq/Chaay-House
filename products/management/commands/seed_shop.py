from django.core.management.base import BaseCommand

from products.models import Category, Product


CATEGORIES = [
    ('Tea', 'coffee', 1),
    ('Coffee', 'coffee', 2),
    ('Milkshakes', 'glass-water', 3),
    ('Snacks', 'cookie', 4),
    ('Biscuits', 'cookie-bite', 5),
    ('Cool Drinks', 'cup-soda', 6),
    ('Combos', 'box', 7),
]

PRODUCTS = [
    ('Tea', 'Masala Chai', 'Classic spiced Indian tea brewed with fresh milk and aromatic spices.', 25, True),
    ('Tea', 'Ginger Tea', 'Strong tea infused with fresh ginger for a warming kick.', 25, False),
    ('Tea', 'Cutting Chai', 'Small, strong, sweet — the neighborhood favorite.', 15, True),
    ('Tea', 'Green Tea', 'Light and refreshing antioxidant-rich green tea.', 30, False),
    ('Tea', 'Elaichi Chai', 'Cardamom-infused milk tea with a fragrant finish.', 28, True),
    ('Coffee', 'Filter Coffee', 'South Indian style filter coffee, strong and frothy.', 35, True),
    ('Coffee', 'Cold Coffee', 'Chilled blended coffee topped with ice cream.', 60, True),
    ('Coffee', 'Cappuccino', 'Espresso topped with steamed milk foam.', 70, False),
    ('Milkshakes', 'Chocolate Shake', 'Thick chocolate milkshake with whipped cream.', 90, True),
    ('Milkshakes', 'Mango Shake', 'Seasonal mango blended with milk and ice.', 85, False),
    ('Snacks', 'Samosa', 'Crispy pastry filled with spiced potato.', 20, True),
    ('Snacks', 'Vada Pav', 'Mumbai-style spiced potato fritter in a bun.', 30, False),
    ('Biscuits', 'Marie Gold', 'Classic tea-time biscuits, pack of 4.', 10, False),
    ('Biscuits', 'Osmania Biscuit', 'Sweet and salty Hyderabadi tea biscuit.', 15, True),
    ('Cool Drinks', 'Lemon Soda', 'Fizzy fresh lime soda, sweet or salted.', 30, False),
    ('Cool Drinks', 'Buttermilk', 'Spiced chilled buttermilk (chaas).', 25, False),
    ('Combos', 'Chai + Samosa Combo', 'Our famous cutting chai paired with a hot samosa.', 40, True),
    ('Combos', 'Coffee + Biscuit Combo', 'Filter coffee with two Osmania biscuits.', 45, False),
]


class Command(BaseCommand):
    help = "Seed the database with sample tea shop categories and products."

    def handle(self, *args, **options):
        cat_map = {}
        for name, icon, order in CATEGORIES:
            cat, _ = Category.objects.get_or_create(name=name, defaults={'icon': icon, 'display_order': order})
            cat_map[name] = cat
        self.stdout.write(self.style.SUCCESS(f"Categories ready: {len(cat_map)}"))

        created = 0
        for cat_name, name, description, price, bestseller in PRODUCTS:
            _, was_created = Product.objects.get_or_create(
                name=name,
                defaults={
                    'category': cat_map[cat_name],
                    'description': description,
                    'price': price,
                    'is_bestseller': bestseller,
                    'is_available': True,
                    'stock': 100,
                },
            )
            created += 1 if was_created else 0

        self.stdout.write(self.style.SUCCESS(f"Products created: {created} (existing ones left untouched)"))
