from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Professor, Module, ModuleInstance, Rating
from django.db.models import Avg


class UserRegistrationTests(APITestCase):
    def test_register_user(self):
        """
        Ensure we can register a new user.
        """
        url = reverse('register')
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword123"
        }
        response = self.client.post(url, data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, "testuser")


class UserLoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username = "testuser", password="testpassword123")

    def test_login_user(self):
        url = reverse('login')
        data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        response = self.client.post(url, data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)      

        self.assertIn("token", response.data)
        self.assertIn("user_id", response.data)
        self.assertIn("username", response.data)
        self.assertIn("email", response.data)


class RatingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username = "testuser", password = "testpassword123")
        self.professor = Professor.objects.create(name = "Prof. Test", email = "prof@example.com", department = "CS")
        self.module = Module.objects.create(code = "CS101", title = "Introduction to Computer Science")
        self.module_instance = ModuleInstance.objects.create(module = self.module, year = 2023, semester = 1)
        self.module_instance.professors.add(self.professor)
        self.client.force_authenticate(user = self.user) 

    def test_create_rating(self):
        url = reverse('rating-list')
        data = {
            "professor": self.professor.id,
            "module_instance": self.module_instance.id,
            "rating": 5,
            "comment": "Great professor!"
        }
        response = self.client.post(url, data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Rating.objects.count(), 1)
        self.assertEqual(Rating.objects.get().rating, 5)

    def test_duplicate_rating(self):
        Rating.objects.create(
            user = self.user,
            professor = self.professor,
            module_instance = self.module_instance,
            rating = 4,
            comment = "Good professor!"
        )

        url = reverse('rating-list')
        data = {
            "professor": self.professor.id,
            "module_instance": self.module_instance.id,
            "rating": 5,
            "comment": "Great professor!"
        }
        response = self.client.post(url, data, format = 'json')

        print("Response Status Code:", response.status_code)
        print("Response Data:", response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)  
        self.assertEqual(Rating.objects.count(), 1)
        self.assertEqual(Rating.objects.get().rating, 5) 


class ProfessorModuleRatingTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username = "testuser1", password = "testpassword123")
        self.user2 = User.objects.create_user(username = "testuser2", password = "testpassword123")
        self.user3 = User.objects.create_user(username = "testuser3", password="testpassword123")

        self.professor = Professor.objects.create(name = "Prof. Test", email = "prof@example.com", department="CS")
        self.module = Module.objects.create(code="CS101", title = "Introduction to Computer Science")
        self.module_instance = ModuleInstance.objects.create(module = self.module, year = 2023, semester=1)
        self.module_instance.professors.add(self.professor)
        self.client.force_authenticate(user = self.user1)

        Rating.objects.create(user = self.user1, professor = self.professor, module_instance = self.module_instance, rating = 4, comment = "Good!")
        Rating.objects.create(user = self.user2, professor = self.professor, module_instance = self.module_instance, rating = 5, comment = "Great!")
        Rating.objects.create(user = self.user3, professor = self.professor, module_instance = self.module_instance, rating = 3, comment = "Okay!")

    def test_average_rating(self):
        url = reverse('professor-module-rating', args=[self.professor.id, self.module.code])
        response = self.client.get(url)

        print("Response Status Code:", response.status_code)
        print("Response Data:", response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_average = 4.0
        self.assertEqual(response.data["average_rating"], expected_average)
 