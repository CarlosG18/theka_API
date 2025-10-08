# filters.py (crie este arquivo)
import django_filters
from .models import Livro

class LivroFilter(django_filters.FilterSet):
    editora_nome = django_filters.CharFilter(
        field_name='editora__nome', 
        lookup_expr='icontains',
        label='Editora (nome)'
    )
    genero_nome = django_filters.CharFilter(
        field_name='genero__nome',
        lookup_expr='icontains',
        label='Gênero (nome)'
    )
    
    class Meta:
        model = Livro
        fields = {
            'genero': ['exact'],
            'editora': ['exact'],
            'ano_publicacao': ['exact', 'gte', 'lte'],
            'titulo': ['icontains'],
            'autor': ['icontains'],
        }