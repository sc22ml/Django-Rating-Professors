from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, LoginView, LogoutView,
    ModuleInstanceListView, ProfessorRatingsView,
    ProfessorModuleRatingView, RateProfessorView,
    ProfessorViewSet, ModuleInstanceViewSet, RatingViewSet
)

router = DefaultRouter()
router.register(r'professors', ProfessorViewSet)
router.register(r'module-instances', ModuleInstanceViewSet)
router.register(r'ratings', RatingViewSet)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('module-instances/', ModuleInstanceListView.as_view(), name='module-instance-list'),
    path('professor-ratings/', ProfessorRatingsView.as_view(), name='professor-ratings'),  # Add this line
    path('professor-module-rating/<int:professor_id>/<str:module_code>/', ProfessorModuleRatingView.as_view(), name='professor-module-rating'),
    path('rate-professor/', RateProfessorView.as_view(), name='rate-professor'),
    path('', include(router.urls)),
]