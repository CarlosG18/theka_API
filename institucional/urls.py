from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NossaHistoriaViewSet, SobreNosViewSet, MembrosEquipeViewSet, NossosValoresViewSet, TopicosViewSet, ContatoViewSet, EstatisticasBibliotecaViewSet

router = DefaultRouter()

router.register(r'sobrenos', SobreNosViewSet, basename='sobrenos')
router.register(r'nossa-historia', NossaHistoriaViewSet, basename='nossahistoria')
router.register(r'membros-equipe', MembrosEquipeViewSet, basename='membrosequipe')
router.register(r'nossos-valores', NossosValoresViewSet, basename='nossosvalores')
router.register(r'topicos', TopicosViewSet, basename='topicos')
router.register(r'contato', ContatoViewSet, basename='contato')
router.register(r'estatisticas-biblioteca', EstatisticasBibliotecaViewSet, basename='estatisticasbiblioteca')

urlpatterns = [
    path('', include(router.urls)),
]