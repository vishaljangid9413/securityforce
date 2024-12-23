from django_filters import rest_framework as filters
from .models import DutyLog

class KilometerRangeFilter(filters.Filter):
    def filter(self, qs, value):
        if value:
            min_km, max_km = value
            return qs.filter(kilometers__gte=min_km, kilometers__lte=max_km)
        return qs

class DutyLogFilter(filters.FilterSet):
    kilometers_range = KilometerRangeFilter()

    class Meta:
        model = DutyLog
        fields = {
            'user': ['exact'],
            'date': ['gte', 'lte'],
        }
