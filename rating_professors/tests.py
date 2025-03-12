from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from .models import Professor, Module, ModuleInstance, Rating
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.db.models import Avg
from .models import Professor, Module, ModuleInstance, Rating

class UserRegistrationTests(APITestCase):
    def test_valid_registration(self):
        url = reverse('register')
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('token' in response.data)

    def test_invalid_registration(self):
        url = reverse('register')
        data = {
            'username': 'testuser',
            'email': 'invalid-email', 
            'password': 'testpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_valid_login(self):
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)

    def test_invalid_login(self):
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'  
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserLogoutTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.create(user = self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_valid_logout(self):
        url = reverse('logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'message': 'Successfully logged out'})

    def test_invalid_logout(self):
        self.client.logout()  
        url = reverse('logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ModuleInstanceTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.module = Module.objects.create(code='CD1', title='Computing for Dummies')
        self.professor = Professor.objects.create(name='Professor J. Excellent', email='je1@example.com', department='CS')
        self.module_instance = ModuleInstance.objects.create(module=self.module, year=2023, semester=1)
        self.module_instance.professors.add(self.professor)

    def test_list_module_instances(self):
        url = reverse('module-instance-list') 
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  


class ProfessorRatingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.professor = Professor.objects.create(name='Professor J. Excellent', email='je1@example.com', department='CS')
        self.module = Module.objects.create(code='CD1', title='Computing for Dummies')
        self.module_instance = ModuleInstance.objects.create(
            module=self.module,
            year=2023,  
            semester=1   
        )
        Rating.objects.create(user=self.user, professor=self.professor, module_instance=self.module_instance, rating=5)

    def test_view_professor_ratings(self):
        url = reverse('professor-ratings')  
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['average_rating'], 5) 

class ProfessorModuleRatingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.professor = Professor.objects.create(name='Professor J. Excellent', email='je1@example.com', department='CS')
        self.module = Module.objects.create(code='CD1', title='Computing for Dummies')
        self.module_instance = ModuleInstance.objects.create(module=self.module, year=2023, semester=1)
        self.module_instance.professors.add(self.professor)
        Rating.objects.create(user=self.user, professor=self.professor, module_instance=self.module_instance, rating=4)

    def test_view_professor_module_rating(self):
        url = reverse('professor-module-rating', args=[self.professor.id, self.module.code])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['average_rating'], 4)  


class RateProfessorTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.professor = Professor.objects.create(name='Professor J. Excellent', email='je1@example.com', department='CS')
        self.module = Module.objects.create(code='CD1', title='Computing for Dummies')
        self.module_instance = ModuleInstance.objects.create(module=self.module, year=2023, semester=1)
        self.module_instance.professors.add(self.professor)

    def test_rate_professor(self):
        url = reverse('rate-professor')
        data = {
            'professor': self.professor.id,
            'module_instance': self.module_instance.id,
            'rating': 5
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Rating.objects.count(), 1)  