from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ModuleInstanceListView, ProfessorRatingsView, ProfessorModuleRatingView, RateProfessorView,
    RegisterView, LoginView, LogoutView, ProfessorViewSet, ModuleInstanceViewSet, RatingViewSet
)

# Create a router for viewsets
router = DefaultRouter()
router.register(r'professors', ProfessorViewSet)  # /api/professors/
router.register(r'module-instances', ModuleInstanceViewSet)  # /api/module-instances/
router.register(r'ratings', RatingViewSet)  # /api/ratings/

urlpatterns = [
    # API Endpoints
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/module-instances/', ModuleInstanceListView.as_view(), name='module_instance_list'),
    path('api/professors/ratings/', ProfessorRatingsView.as_view(), name='professor_ratings'),
    path('api/professors/<int:professor_id>/modules/<str:module_code>/rating/', ProfessorModuleRatingView.as_view(), name='professor_module_rating'),
    path('api/rate/', RateProfessorView.as_view(), name='rate_professor'),

    # Include router-generated URLs
    path('api/', include(router.urls)),
]