import datetime

from django.core.exceptions import ValidationError


def validate_year(year):
    """Год не может быть больше текущего."""
    current_year = datetime.datetime.now()
    if year < 1700 or year > current_year.year:
        raise ValidationError(
            f'Год указан больше текущего года {current_year.year}'
            f'или меньше нашей эры'
        )
