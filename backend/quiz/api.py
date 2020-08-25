from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import *

# router = DefaultRouter()
# router.register(r'routes', RouteViewSet, basename='routes')
# router.register(r'route-plans', RoutePlanViewSet, basename='route-plans')


urlpatterns = [
    # path('', include(router.urls)),
    path('quiz/', QuizView.as_view()),
    path('answer/', VisitorAnswerView.as_view())
]
