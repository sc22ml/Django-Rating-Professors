# from django.urls import path, include
# from .views import dashboard
# from django.contrib.auth import views as auth_views
# from rest_framework.routers import DefaultRouter
# from .views import WebLoginView
# from .views import (
#     RegisterView, LoginView, LogoutView,
#     ModuleInstanceViewSet, ProfessorViewSet,
#     ProfessorModuleRatingView, RatingViewSet
# )
# from django.http import HttpResponse

# def home(request):
#     return HttpResponse("Welcome to the Professor Rating API!")

# router = DefaultRouter()
# router.register(r'module-instances', ModuleInstanceViewSet, basename = 'moduleinstance')
# router.register(r'professors', ProfessorViewSet, basename = 'professor')
# router.register(r'ratings', RatingViewSet, basename = 'rating')

# urlpatterns = [
#     path('', home, name = 'home'),
#     path('dashboard/', dashboard, name='dashboard'),
#     path('register/', RegisterView.as_view(), name = 'register'),
#     path('login/', WebLoginView.as_view(), name='login'),
#     path('logout/', auth_views.LogoutView.as_view(next_page = 'login'), name = 'logout'),
#     path('api/professors/<int:professor_id>/modules/<str:module_code>/average/',
#          ProfessorModuleRatingView.as_view(), name = 'professor-module-rating'),
#     path('api/', include(router.urls)),  
# ]


from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from .views import (
    home, dashboard, WebLoginView, RegisterView, LoginView, LogoutView,
    ModuleInstanceViewSet, ProfessorViewSet, ProfessorModuleRatingView, RatingViewSet
)


router = DefaultRouter()
router.register(r'module-instances', ModuleInstanceViewSet, basename='moduleinstance')
router.register(r'professors', ProfessorViewSet, basename='professor')
router.register(r'ratings', RatingViewSet, basename='rating')

urlpatterns = [
    path('', home, name = 'home'),
    path('dashboard/', dashboard, name='dashboard'),

    path('register/', RegisterView.as_view(), name = 'register'),
    path('login/', WebLoginView.as_view(template_name = 'registration/login.html'), name = 'login'),
    path('logout/', auth_views.LogoutView.as_view(next_page = 'login'), name = 'logout'),

    path('api/professors/<int:professor_id>/modules/<str:module_code>/average/',
         ProfessorModuleRatingView.as_view(), name = 'professor-module-rating'),
    path('api/', include(router.urls)),
]