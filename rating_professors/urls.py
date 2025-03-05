from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, LoginView, LogoutView,
    ModuleInstanceViewSet, ProfessorViewSet,
    ProfessorModuleRatingView, RatingViewSet
)
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to the Professor Rating API!")

router = DefaultRouter()
router.register(r'module-instances', ModuleInstanceViewSet, basename = 'moduleinstance')
router.register(r'professors', ProfessorViewSet, basename = 'professor')
router.register(r'ratings', RatingViewSet, basename = 'rating')

# Define URL patterns
urlpatterns = [
    path('', home, name = 'home'),
    path('register/', RegisterView.as_view(), name = 'register'),
    path('login/', LoginView.as_view(), name = 'login'),
    path('logout/', LogoutView.as_view(), name = 'logout'),
    path('professors/<int:professor_id>/modules/<str:module_code>/average/',
         ProfessorModuleRatingView.as_view(), name = 'professor-module-rating'),
    path('', include(router.urls)),  
]


