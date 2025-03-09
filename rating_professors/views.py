from django.shortcuts import get_object_or_404, render, redirect, HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.db.models.functions import Cast
from django.db.models import IntegerField
from django.db.models.functions import Round
from django.views.generic import View
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.db.models import Avg
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from .models import Professor, Module, ModuleInstance, Rating
from .serializers import (
    UserSerializer, ProfessorSerializer, ModuleSerializer,
    ModuleInstanceSerializer, RatingSerializer, CreateRatingSerializer, ProfessorModuleRatingSerializer
)

# Registration View
class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "token": token.key
        }, status=status.HTTP_201_CREATED)


# API-based Login View
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

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
        if request.user.is_authenticated:
            request.user.auth_token.delete()
            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)



# Module Instance List View
class ModuleInstanceListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        module_instances = ModuleInstance.objects.all()
        data = []
        for instance in module_instances:
            data.append({
                "code": instance.module.code,
                "name": instance.module.title,
                "year": instance.year,
                "semester": instance.get_semester_display(),
                "taught_by": [{"id": professor.id, "name": professor.name} for professor in instance.professors.all()]
            })
        return Response(data, status=status.HTTP_200_OK)


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
    







# web base:

# def register(request):
#     if request.method == "POST":
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect("student_dashboard")
#     else:
#         form = UserCreationForm()
#     return render(request, "register.html", {"form": form})


# Web-based Login View
# class WebLoginView(LoginView):
#     template_name = 'registration/login.html'
#     redirect_authenticated_user = True

#     def get_success_url(self):
#         return reverse_lazy('student_dashboard')

#     def form_invalid(self, form):
#         form.add_error(None, "Invalid username or password")
#         return super().form_invalid(form)


# Web-based Logout View
# class WebLogoutView(LogoutView):
#     def get(self, request):
#         logout(request)
#         return redirect('login')


# @login_required
# def student_dashboard(request):
#     module_instances = ModuleInstance.objects.filter(students=request.user)
#     return render(request, 'student_dashboard.html', {
#         'module_instances': module_instances
#     })


# Student Home View
# @login_required
# def student_home(request):
#     module_instances = ModuleInstance.objects.all()
#     data = []

#     for instance in module_instances:
#         professors = instance.professors.all()
#         data.append({
#             'module': instance.module.title,
#             'semester': instance.get_semester_display(),
#             'year': instance.year,
#             'professors': [prof.name for prof in professors],
#             'module_instance_id': instance.id
#         })

#     return render(request, 'student_home.html', {'module_instances': data})


# def rate_professor(request, professor_id):
#     professor = get_object_or_404(Professor, id=professor_id)

#     if request.method == 'POST':
#         module_instance_id = request.POST.get('module_instance')
#         rating_value = request.POST.get('rating')
#         comment = request.POST.get('comment', '')

#         # Fetch the selected module instance
#         module_instance = get_object_or_404(ModuleInstance, id=module_instance_id)

#         # Validate the rating value
#         try:
#             rating_value = int(rating_value)
#             if rating_value < 1 or rating_value > 5:
#                 raise ValueError("Rating must be between 1 and 5.")
#         except (ValueError, TypeError):
#             messages.error(request, "Invalid rating. Please enter a number between 1 and 5.")
#             return redirect('rate_professor', professor_id=professor.id)

#         # Save the rating
#         Rating.objects.create(
#             user=request.user,
#             professor=professor,
#             module_instance=module_instance,  # Include the module_instance
#             rating=rating_value,
#             comment=comment
#         )
#         messages.success(request, f"Rating submitted for {professor.name}.")
#         return redirect('all_professors')

#     return render(request, 'rate_professor.html', {'professor': professor})


# Professor List View
# @login_required
# def professor_list(request, module_instance_id):
#     module_instance = get_object_or_404(ModuleInstance, id=module_instance_id)
#     professors = module_instance.professors.all()
#     return render(request, 'professor_list.html', {'module_instance': module_instance, 'professors': professors})

# def all_professors(request):
#     # Fetch all professors with their rounded average ratings
#     professors = Professor.objects.annotate(
#         average_rating=Round(Avg('rating__rating'))
#     ).all()
#     return render(request, 'all_professors.html', {'professors': professors})


# def module_instance_list_web(request):
#     module_instances = ModuleInstance.objects.all()
#     return render(request, 'module_instance_list.html', {'module_instances': module_instances})