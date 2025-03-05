from django.shortcuts import get_object_or_404, render, redirect, HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.contrib.auth.decorators import login_required  
import math
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.db.models import Avg
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Professor, Module, ModuleInstance, Rating
from .serializers import (
    UserSerializer, ProfessorSerializer, ModuleSerializer,
    ModuleInstanceSerializer, RatingSerializer, CreateRatingSerializer, ProfessorModuleRatingSerializer
)

def home(request):
    return HttpResponse("Welcome to the Professor Rating API!")


def dashboard(request):  
    return render(request, "dashboard.html")


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})
    

class WebLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def form_invalid(self, form):
        form.add_error(None, "Invalid username or password")
        return super().form_invalid(form)


class WebLogoutView(LogoutView):
    next_page = 'login'


class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user = user)

        return Response({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "token": token.key
        }, status = status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username = username, password = password)
        if user and user.is_active:
            token, _ = Token.objects.get_or_create(user = user)
            return Response({
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "token": token.key
            }, status = status.HTTP_200_OK)

        return Response({"error": "Invalid credentials"}, status = status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.is_authenticated:
            request.user.auth_token.delete()
            return Response({"message": "Successfully logged out"}, status = status.HTTP_200_OK)
        return Response({"error": "User not authenticated"}, status = status.HTTP_401_UNAUTHORIZED)


class ProfessorModuleRatingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, professor_id, module_code):
        professor = get_object_or_404(Professor, id = professor_id)
        module = get_object_or_404(Module, code = module_code)

        module_instances = ModuleInstance.objects.filter(
            module = module,
            professors = professor
        )

        if not module_instances.exists():
            return Response({"error": "This professor does not teach this module"},
                            status = status.HTTP_404_NOT_FOUND)

        ratings = Rating.objects.filter(
            module_instance__in = module_instances,
            professor = professor
        )

        if not ratings.exists():
            return Response({"average_rating": 0, "message": "No ratings yet"},
                            status = status.HTTP_200_OK)

        avg_rating_raw = ratings.aggregate(Avg('rating'))['rating__avg']
        avg_rating = int(avg_rating_raw + 0.5) if avg_rating_raw is not None else 0

        return Response({
            "professor_id": professor_id,
            "professor_name": professor.name,
            "module_code": module_code,
            "module_name": module.title,
            "average_rating": avg_rating,
            "total_ratings": ratings.count()
        }, status = status.HTTP_200_OK)


class RatingViewSet(viewsets.ModelViewSet):
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Rating.objects.filter(user = self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = CreateRatingSerializer(data = request.data, context = {'request': request})
        if serializer.is_valid():
            user = request.user
            professor = serializer.validated_data['professor']
            module_instance = serializer.validated_data['module_instance']

            existing_rating = Rating.objects.filter(
                user = user,
                professor = professor,
                module_instance = module_instance
            ).first()

            if existing_rating:
                existing_rating.rating = serializer.validated_data['rating']
                existing_rating.comment = serializer.validated_data.get('comment', '')
                existing_rating.save()
                return Response({"message": "Rating updated successfully"}, status=status.HTTP_200_OK)

            serializer.save(user=user)
            return Response({"message": "Rating submitted successfully"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ModuleInstanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ModuleInstance.objects.all()
    serializer_class = ModuleInstanceSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProfessorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Professor.objects.all()
    serializer_class = ProfessorSerializer
    permission_classes = [permissions.IsAuthenticated]
