import django_filters
from review.models import Titles


class TitlesFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='contains')
    category = django_filters.CharFilter(
        field_name='category__slug', lookup_expr='contains'
    )
    genre = django_filters.CharFilter(
        field_name='genre__slug', lookup_expr='contains'
    )
    year = django_filters.NumberFilter(
        field_name='year',
    )

    class Meta:
        model = Titles
        fields = [
            'name',
            'genre',
            'category',
            'year',
        ]
