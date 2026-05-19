from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.test import override_settings
from html import unescape
from urllib.parse import parse_qs, urlparse


class EmailTokenObtainPairTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Password123!',
        )
        self.url = reverse('token_obtain_pair')

    def test_login_with_email_success(self):
        """Test JWT login using email instead of username."""
        response = self.client.post(
            self.url,
            {'email': 'test@example.com', 'password': 'Password123!'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_email_case_insensitive(self):
        """Test JWT login accepts email regardless of casing."""
        response = self.client.post(
            self.url,
            {'email': 'TEST@example.com', 'password': 'Password123!'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_with_username_is_not_accepted(self):
        """Test JWT login no longer accepts username as the credential field."""
        response = self.client.post(
            self.url,
            {'username': 'testuser', 'password': 'Password123!'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)


class UserTests(APITestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Password123!',
            'password_confirm': 'Password123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.url = reverse('user-list')

    def test_create_user_success(self):
        """Test creating a user with valid data."""
        response = self.client.post(self.url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')

    def test_create_user_invalid_password(self):
        """Test creating a user with a weak password."""
        data = self.user_data.copy()
        data['password'] = 'weak'
        data['password_confirm'] = 'weak'
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_create_user_mismatch_passwords(self):
        """Test creating a user with mismatched passwords."""
        data = self.user_data.copy()
        data['password_confirm'] = 'Different123!'
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data)

    def test_create_user_invalid_email(self):
        """Test creating a user with an invalid email."""
        data = self.user_data.copy()
        data['email'] = 'invalid-email'
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_duplicate_email(self):
        """Test that duplicate emails are not allowed."""
        User.objects.create_user(username='other', email='test@example.com', password='Password123!')
        response = self.client.post(self.url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_list_users(self):
        """Test listing users."""
        User.objects.create_user(username='user1', email='u1@ex.com', password='Pass123!')
        User.objects.create_user(username='user2', email='u2@ex.com', password='Pass123!')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 2)
        else:
            self.assertEqual(len(response.data), 2)

    def test_retrieve_user(self):
        """Test retrieving a specific user."""
        user = User.objects.create_user(username='testuser', email='test@ex.com', password='Pass123!')
        url = reverse('user-detail', args=[user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_update_user(self):
        """Test updating a user."""
        user = User.objects.create_user(username='testuser', email='test@ex.com', password='Pass123!')
        url = reverse('user-detail', args=[user.id])
        data = {'first_name': 'Updated'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.first_name, 'Updated')

    def test_delete_user(self):
        """Test deleting a user."""
        user = User.objects.create_user(username='testuser', email='test@ex.com', password='Pass123!')
        url = reverse('user-detail', args=[user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 0)

class PasswordResetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='OldPassword123!'
        )
        self.reset_url = reverse('password_reset')
        self.confirm_url = reverse('password_reset_confirm')

    @override_settings(FRONTEND_URL='http://localhost:3000/')
    def test_password_reset_request_success(self):
        """Test requesting a password reset email."""
        response = self.client.post(self.reset_url, {'email': 'test@example.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('test@example.com', mail.outbox[0].to)
        email_body = unescape(mail.outbox[0].body)
        self.assertIn('http://localhost:3000/auth/password/reset/confirm/?', email_body)

        reset_link = email_body.split('http://localhost:3000/auth/password/reset/confirm/?', 1)[1].split()[0]
        query_params = parse_qs(urlparse(f'http://localhost:3000/auth/password/reset/confirm/?{reset_link}').query)
        self.assertEqual(query_params['uid'], [urlsafe_base64_encode(force_bytes(self.user.pk))])
        self.assertIn('token', query_params)

    def test_password_reset_request_invalid_email(self):
        """Test requesting a reset for a non-existent email."""
        response = self.client.post(self.reset_url, {'email': 'wrong@example.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_success(self):
        """Test confirming a password reset."""
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        
        data = {
            'uid': uid,
            'token': token,
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'NewPassword123!'
        }
        response = self.client.post(self.confirm_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword123!'))

    def test_password_reset_confirm_invalid_token(self):
        """Test confirming reset with an invalid token."""
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = 'invalid-token'
        
        data = {
            'uid': uid,
            'token': token,
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'NewPassword123!'
        }
        response = self.client.post(self.confirm_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
