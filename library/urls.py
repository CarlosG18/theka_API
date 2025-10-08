from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LivroViewSet, GeneroViewSet, EditoraViewSet

router = DefaultRouter()

router.register('livros',LivroViewSet, basename='livro')
router.register('generos', GeneroViewSet, basename='genero')
router.register('editoras', EditoraViewSet, basename='editora')

urlpatterns = [
    path('', include(router.urls)),
]