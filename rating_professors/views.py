from django.shortcuts import get_object_or_404, render, redirect, HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Avg, IntegerField
from django.db.models.functions import Cast, Round
from django.views.generic import View, ListView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User

from rest_framework import viewsets, permissions, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view

from .models import Professor, Module, ModuleInstance, Rating
from .serializers import (
    UserSerializer, ProfessorSerializer, ModuleSerializer,
    ModuleInstanceSerializer, RatingSerializer, CreateRatingSerializer, ProfessorModuleRatingSerializer
)


class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        print("Recieved Data: ", request.data)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "token": token.key
            }, status=status.HTTP_201_CREATED)
        else:
            print("Validation Errors: ", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# API-based Login View
class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user and user.is_active:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "token": token.key
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


# API-based Logout View
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
        except Token.DoesNotExist:
            pass 
        return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)


class ModuleInstanceListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        module_instances = ModuleInstance.objects.all()
        serializer = ModuleInstanceSerializer(module_instances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Professor Ratings View
class ProfessorRatingsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        professors = Professor.objects.annotate(
            average_rating=Avg('ratings__rating')
        ).values('id', 'name', 'average_rating')
        
        for professor in professors:
            professor['average_rating'] = int(professor['average_rating']) if professor['average_rating'] else 0
        return Response(professors, status=status.HTTP_200_OK)


# Professor Module Rating View
class ProfessorModuleRatingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, professor_id, module_code):
        professor = get_object_or_404(Professor, id=professor_id)
        module = get_object_or_404(Module, code=module_code)

        ratings = Rating.objects.filter(professor=professor, module_instance__module=module)
        avg_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0

        return Response({
            "professor_id": professor.id,
            "professor_name": professor.name,
            "module_code": module.code,
            "module_name": module.title,
            "average_rating": round(avg_rating, 1)
        }, status=status.HTTP_200_OK)


# Rate Professor View
class RateProfessorView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CreateRatingSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message": "Rating submitted successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Professor ViewSet
class ProfessorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Professor.objects.all()
    serializer_class = ProfessorSerializer
    permission_classes = [permissions.IsAuthenticated]


# Module Instance ViewSet
class ModuleInstanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ModuleInstance.objects.all()
    serializer_class = ModuleInstanceSerializer
    permission_classes = [permissions.IsAuthenticated]


# Rating ViewSet
class RatingViewSet(viewsets.ModelViewSet):
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Rating.objects.all()

    def get_queryset(self):
        return Rating.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = CreateRatingSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            professor = serializer.validated_data['professor']
            module_instance = serializer.validated_data['module_instance']

            existing_rating = Rating.objects.filter(
                user=user,
                professor=professor,
                module_instance=module_instance
            ).first()

            if existing_rating:
                existing_rating.rating = serializer.validated_data['rating']
                existing_rating.save()
                return Response({"message": "Rating updated successfully"}, status=status.HTTP_200_OK)

            serializer.save(user=user)
            return Response({"message": "Rating submitted successfully"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)