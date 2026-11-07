from django.urls import path

from .views import QuoteComparisonView


urlpatterns = [
    path(
        'rfqs/<int:rfq_id>/comparison/',
        QuoteComparisonView.as_view(),
        name='quote-comparison'
    ),
]