from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework import permissions, viewsets, status, filters
from rest_framework.decorators import action
from .models import Livro, Genero, Editora
from rest_framework.response import Response
from .serializers import LivroSerializer, GeneroSerializer, EditoraSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .pagination import StandardResultsSetPagination, LargeResultsSetPagination, SmallResultsSetPagination

# Create your views here.
from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Livro
from .serializers import LivroSerializer
from .pagination import StandardResultsSetPagination
from .filters import LivroFilter

class LivroViewSet(viewsets.ModelViewSet):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer
    # permission_classes = [permissions.IsAuthenticated]
    
    # CORREÇÃO: Configuração segura de filtros
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    
    # CORREÇÃO: Remover 'editora' do search_fields pois é ForeignKey
    search_fields = ['titulo', 'autor', 'isbn']  # Apenas campos CharField
    filterset_class = LivroFilter
    
    # CORREÇÃO: Para ForeignKeys, usar apenas IDs no filterset_fields
    filterset_fields = ['genero', 'ano_publicacao', 'editora']
    
    ordering_fields = ['titulo', 'ano_publicacao', 'autor', 'criado_em']
    ordering = ['-criado_em']
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_queryset(self):
        """Custom queryset para garantir que a ordenação funcione corretamente"""
        queryset = super().get_queryset()
        
        # Se há parâmetro de ordenação na URL, usa apenas ele
        # Se não há parâmetro, usa a ordenação padrão
        ordering = self.request.GET.get('ordering')
        if ordering:
            # Quando há ordering na URL, ignora a ordenação padrão
            return queryset.order_by(ordering)
        
        return queryset

        return super().get_queryset()

    # CORREÇÃO: Métodos opcionais - você pode remover se não precisar de customização
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'], url_path='novidades', url_name='novidades')
    def novidades(self, request):
        """
            Retorna os livros mais recentes.
        """
        ultimos_livros = Livro.objects.all().order_by('-criado_em')[:5]
        serializer = self.get_serializer(ultimos_livros, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='destaque-mes', url_name='destaque-mes')
    def destaque_mes(self, request):
        """
            Retorna um livro em destaque do mês.
        """
        livro_destaque = Livro.objects.all().order_by('-criado_em').first()
        serializer = self.get_serializer(livro_destaque)
        return Response(serializer.data)
    
class GeneroViewSet(viewsets.ModelViewSet):
    queryset = Genero.objects.all()
    serializer_class = GeneroSerializer
    #permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

class EditoraViewSet(viewsets.ModelViewSet):
    queryset = Editora.objects.all()
    serializer_class = EditoraSerializer
    #permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)