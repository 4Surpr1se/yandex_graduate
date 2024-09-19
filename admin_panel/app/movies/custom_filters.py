from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class RatingFilter(admin.SimpleListFilter):
    title = _('rating')
    parameter_name = 'rating'

    def lookups(self, request, model_admin):
        return [
            ('0-2', '0-2'),
            ('2-4', '2-4'),
            ('4-6', '4-6'),
            ('6-8', '6-8'),
            ('8-10', '8-10'),
        ]

    def queryset(self, request, queryset):
        if self.value() == '0-2':
            return queryset.filter(rating__gte=0, rating__lte=2)
        elif self.value() == '2-4':
            return queryset.filter(rating__gte=2, rating__lte=4)
        elif self.value() == '4-6':
            return queryset.filter(rating__gte=4, rating__lte=6)
        elif self.value() == '6-8':
            return queryset.filter(rating__gte=6, rating__lte=8)
        elif self.value() == '8-10':
            return queryset.filter(rating__gte=8, rating__lte=10)
        return queryset
