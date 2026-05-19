from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LegacyPasswordResetConfirmRedirectView,
    UserViewSet,
    PasswordResetConfirmView,
    PasswordResetView,
)

router = DefaultRouter()

router.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'password-reset-confirm/<str:uid>/<str:token>/',
        LegacyPasswordResetConfirmRedirectView.as_view(),
        name='legacy_password_reset_confirm',
    ),
    path('auth/password/reset/', PasswordResetView.as_view(), name='password_reset'),
    path('auth/password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
