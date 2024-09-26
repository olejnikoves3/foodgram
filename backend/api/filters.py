from rest_framework.filters import BaseFilterBackend
from django.db.models import Case, When, Value, IntegerField


class IngredientSearch(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        name = request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)
            queryset = queryset.annotate(
                starts_with=Case(
                    When(name__istartswith=name, then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            ).order_by('starts_with', 'name')
        return queryset
