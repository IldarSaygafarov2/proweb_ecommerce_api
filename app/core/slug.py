import re
import unicodedata


def slugify(text: str) -> str:
    '''генерирует slug относительно переданного значения'''
    text = unicodedata.normalize('NFKD', text)
    text = text.encode("utf-8", "ignore").decode("utf-8")
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', "", text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-') or "product"


def make_unique_slug(base: str, existing_slugs: list[str]) -> str:
    """создает уникальный слаг, если созданный нами слаг уже есть в БД"""
    slug = base
    counter = 1
    while slug in existing_slugs:
        slug = f'{base}-{counter}'
        counter += 1
    return slug



