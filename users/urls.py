from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, PasswordResetConfirmView, PasswordResetView

router = DefaultRouter()

router.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/password/reset/', PasswordResetView.as_view(), name='password_reset'),
    path('auth/password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]