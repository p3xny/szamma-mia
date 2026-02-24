"""Seed the database with all 16 dishes from the frontend MenuSection."""

import asyncio
from decimal import Decimal

from sqlalchemy import select

from database import async_session, engine
from models import Base, Category, Dish, DishExtra, DishIngredient, Extra, Ingredient

# ---------------------------------------------------------------------------
# Raw data extracted from client/src/components/MenuSection.vue
# ---------------------------------------------------------------------------

CATEGORIES = [
    {"key": "pizza", "label": "Pizza", "display_order": 1},
    {"key": "pasta", "label": "Makarony", "display_order": 2},
    {"key": "main", "label": "Dania Główne", "display_order": 3},
    {"key": "dessert", "label": "Desery", "display_order": 4},
]

# Each dish: (name, category_key, base_price, original_price, image_url, is_daily_special, display_order,
#             [(ingredient_name, included, extra_price), ...],
#             [(extra_name, price), ...])

DISHES = [
    # ── Pizza ──
    (
        "Pizza Margherita", "pizza", 28, 35,
        "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=600",
        True, 1,
        [
            ("Sos pomidorowy", True, 0),
            ("Mozzarella", True, 0),
            ("Bazylia", True, 0),
            ("Oliwki", False, 3),
            ("Jalapeño", False, 4),
        ],
        [("Sos czosnkowy", 3), ("Dodatkowy ser", 5), ("Frytki", 8)],
    ),
    (
        "Pizza Pepperoni", "pizza", 38, None,
        "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=600",
        False, 2,
        [
            ("Sos pomidorowy", True, 0),
            ("Mozzarella", True, 0),
            ("Pepperoni", True, 0),
            ("Oliwki", False, 3),
            ("Papryka", False, 3),
        ],
        [("Sos czosnkowy", 3), ("Dodatkowy ser", 5), ("Frytki", 8)],
    ),
    (
        "Pizza Quattro Formaggi", "pizza", 42, None,
        "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600",
        False, 3,
        [
            ("Mozzarella", True, 0),
            ("Gorgonzola", True, 0),
            ("Parmezan", True, 0),
            ("Ricotta", True, 0),
            ("Rukola", False, 3),
        ],
        [("Miód", 3), ("Orzechy włoskie", 4), ("Frytki", 8)],
    ),
    (
        "Pizza Diavola", "pizza", 40, None,
        "https://images.unsplash.com/photo-1628840042765-356cda07504e?w=600",
        False, 4,
        [
            ("Sos pomidorowy", True, 0),
            ("Mozzarella", True, 0),
            ("Salami pikantne", True, 0),
            ("Oliwki", False, 3),
            ("Jalapeño", False, 4),
        ],
        [("Sos czosnkowy", 3), ("Dodatkowy ser", 5), ("Frytki", 8)],
    ),

    # ── Pasta ──
    (
        "Spaghetti Carbonara", "pasta", 32, 40,
        "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?w=600",
        True, 1,
        [
            ("Spaghetti", True, 0),
            ("Guanciale", True, 0),
            ("Jajko", True, 0),
            ("Pecorino", True, 0),
            ("Boczek", False, 5),
        ],
        [("Sos truflowy", 6), ("Chleb czosnkowy", 5), ("Dodatkowy parmezan", 4)],
    ),
    (
        "Penne Arrabbiata", "pasta", 34, None,
        "https://images.unsplash.com/photo-1563379926898-05f4575a45d8?w=600",
        False, 2,
        [
            ("Penne", True, 0),
            ("Sos pomidorowy", True, 0),
            ("Chili", True, 0),
            ("Czosnek", True, 0),
            ("Kurczak", False, 6),
        ],
        [("Parmezan", 4), ("Chleb czosnkowy", 5), ("Oliwa truflowa", 5)],
    ),
    (
        "Tagliatelle z Truflami", "pasta", 52, None,
        "https://images.unsplash.com/photo-1556761223-4c4282c73f77?w=600",
        False, 3,
        [
            ("Tagliatelle", True, 0),
            ("Masło truflowe", True, 0),
            ("Parmezan", True, 0),
            ("Trufle", True, 0),
            ("Grzyby leśne", False, 6),
        ],
        [("Dodatkowe trufle", 10), ("Chleb czosnkowy", 5), ("Kieliszek Prosecco", 12)],
    ),
    (
        "Fettuccine Alfredo", "pasta", 38, None,
        "https://images.unsplash.com/photo-1645112411341-6c4fd023714a?w=600",
        False, 4,
        [
            ("Fettuccine", True, 0),
            ("Sos śmietanowy", True, 0),
            ("Parmezan", True, 0),
            ("Masło", True, 0),
            ("Kurczak", False, 6),
        ],
        [("Krewetki", 8), ("Chleb czosnkowy", 5), ("Szpinak", 3)],
    ),

    # ── Main courses ──
    (
        "Lasagna Bolognese", "main", 42, None,
        "https://images.unsplash.com/photo-1551183053-bf91a1d81141?w=600",
        False, 1,
        [
            ("Makaron lasagna", True, 0),
            ("Ragù bolognese", True, 0),
            ("Beszamel", True, 0),
            ("Mozzarella", True, 0),
            ("Dodatkowe mięso", False, 6),
        ],
        [("Sałatka", 6), ("Chleb czosnkowy", 5), ("Frytki", 8)],
    ),
    (
        "Risotto Grzybowe", "main", 40, 50,
        "https://images.unsplash.com/photo-1608897013039-887f21d8c804?w=600",
        True, 2,
        [
            ("Ryż arborio", True, 0),
            ("Grzyby leśne", True, 0),
            ("Parmezan", True, 0),
            ("Masło", True, 0),
            ("Trufle", False, 8),
        ],
        [("Oliwa truflowa", 5), ("Sałatka", 6), ("Kieliszek wina", 14)],
    ),
    (
        "Osso Buco", "main", 58, None,
        "https://images.unsplash.com/photo-1544025162-d76694265947?w=600",
        False, 3,
        [
            ("Golonka cielęca", True, 0),
            ("Warzywa duszone", True, 0),
            ("Gremolata", True, 0),
            ("Risotto", True, 0),
            ("Dodatkowa porcja mięsa", False, 12),
        ],
        [("Purée ziemniaczane", 6), ("Sałatka", 6), ("Kieliszek wina", 14)],
    ),
    (
        "Saltimbocca alla Romana", "main", 54, None,
        "https://images.unsplash.com/photo-1432139555190-58524dae6a55?w=600",
        False, 4,
        [
            ("Cielęcina", True, 0),
            ("Prosciutto", True, 0),
            ("Szałwia", True, 0),
            ("Sos z białego wina", True, 0),
            ("Grzyby", False, 5),
        ],
        [("Ziemniaki pieczone", 6), ("Sałatka", 6), ("Szparagi", 7)],
    ),

    # ── Desserts ──
    (
        "Tiramisu", "dessert", 19, 24,
        "https://images.unsplash.com/photo-1579954115545-a95591f28bfc?w=600",
        True, 1,
        [
            ("Mascarpone", True, 0),
            ("Biszkopty", True, 0),
            ("Espresso", True, 0),
            ("Kakao", True, 0),
            ("Likiery", False, 4),
        ],
        [("Bita śmietana", 3), ("Lody waniliowe", 5), ("Sos czekoladowy", 3)],
    ),
    (
        "Panna Cotta", "dessert", 22, None,
        "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=600",
        False, 2,
        [
            ("Śmietanka", True, 0),
            ("Wanilia", True, 0),
            ("Sos malinowy", True, 0),
            ("Sos karmelowy", False, 3),
        ],
        [("Owoce świeże", 4), ("Bita śmietana", 3), ("Sos czekoladowy", 3)],
    ),
    (
        "Cannoli Sycylijskie", "dessert", 20, None,
        "https://images.unsplash.com/photo-1611293388250-580b08c4a145?w=600",
        False, 3,
        [
            ("Ricotta", True, 0),
            ("Skorupka cannoli", True, 0),
            ("Cukier puder", True, 0),
            ("Chipsy czekoladowe", False, 3),
        ],
        [("Pistacje", 4), ("Sos czekoladowy", 3), ("Lody", 5)],
    ),
    (
        "Gelato Misto", "dessert", 18, None,
        "https://images.unsplash.com/photo-1567206563064-6f60f40a2b57?w=600",
        False, 4,
        [
            ("Wanilia", True, 0),
            ("Czekolada", True, 0),
            ("Pistacja", True, 0),
            ("Mango", False, 3),
        ],
        [("Bita śmietana", 3), ("Sos karmelowy", 3), ("Wafelek", 2)],
    ),
]


async def seed():
    async with async_session() as session:
        # 1. Categories
        cat_map: dict[str, Category] = {}
        for c in CATEGORIES:
            cat = Category(**c)
            session.add(cat)
            cat_map[c["key"]] = cat
        await session.flush()

        # 2. Collect all unique ingredient and extra names
        all_ingredients: set[str] = set()
        all_extras: set[str] = set()
        for dish_tuple in DISHES:
            for ing_name, _, _ in dish_tuple[7]:
                all_ingredients.add(ing_name)
            for ext_name, _ in dish_tuple[8]:
                all_extras.add(ext_name)

        # 3. Create ingredients
        ing_map: dict[str, Ingredient] = {}
        for name in sorted(all_ingredients):
            ing = Ingredient(name=name)
            session.add(ing)
            ing_map[name] = ing
        await session.flush()

        # 4. Create extras
        ext_map: dict[str, Extra] = {}
        for name in sorted(all_extras):
            ext = Extra(name=name)
            session.add(ext)
            ext_map[name] = ext
        await session.flush()

        # 5. Create dishes with associations
        for (
            name, cat_key, base_price, original_price, image_url,
            is_daily_special, display_order, ingredients, extras
        ) in DISHES:
            dish = Dish(
                name=name,
                category_id=cat_map[cat_key].id,
                base_price=Decimal(str(base_price)),
                original_price=Decimal(str(original_price)) if original_price else None,
                image_url=image_url,
                is_daily_special=is_daily_special,
                display_order=display_order,
            )
            session.add(dish)
            await session.flush()

            for idx, (ing_name, included, price) in enumerate(ingredients):
                session.add(DishIngredient(
                    dish_id=dish.id,
                    ingredient_id=ing_map[ing_name].id,
                    is_included_by_default=included,
                    additional_price=Decimal(str(price)),
                    display_order=idx + 1,
                ))

            for idx, (ext_name, price) in enumerate(extras):
                session.add(DishExtra(
                    dish_id=dish.id,
                    extra_id=ext_map[ext_name].id,
                    price=Decimal(str(price)),
                    display_order=idx + 1,
                ))

        await session.commit()

    # Print summary
    async with async_session() as session:
        cat_count = len((await session.execute(select(Category))).scalars().all())
        dish_count = len((await session.execute(select(Dish))).scalars().all())
        ing_count = len((await session.execute(select(Ingredient))).scalars().all())
        ext_count = len((await session.execute(select(Extra))).scalars().all())
        di_count = len((await session.execute(select(DishIngredient))).scalars().all())
        de_count = len((await session.execute(select(DishExtra))).scalars().all())

    print(f"Seeded: {cat_count} categories, {dish_count} dishes, "
          f"{ing_count} ingredients, {ext_count} extras, "
          f"{di_count} dish-ingredients, {de_count} dish-extras")


if __name__ == "__main__":
    asyncio.run(seed())
