# library/serializers.py
from rest_framework import serializers
from .models import Genero, Editora, Livro
import re

class GeneroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genero
        fields = '__all__'

    def validate_nome(self, value):
        """Validação customizada para o campo nome"""
        if not value or not value.strip():
            raise serializers.ValidationError("O nome da editora é obrigatório.")
        
        value = value.strip()
        
        # Verifica tamanho mínimo
        if len(value) < 2:
            raise serializers.ValidationError("O nome da editora deve ter pelo menos 2 caracteres.")
        
        # Verifica se contém apenas letras, espaços e caracteres especiais comuns
        if not re.match(r'^[A-Za-zÀ-ÿ0-9\s\-\.,&]+$', value):
            raise serializers.ValidationError("O nome da editora contém caracteres inválidos.")
        
        return value

class EditoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Editora
        fields = '__all__'

    def validate_nome(self, value):
        """Validação customizada para o campo nome"""
        if not value or not value.strip():
            raise serializers.ValidationError("O nome da editora é obrigatório.")
        
        value = value.strip()
        
        # Verifica tamanho mínimo
        if len(value) < 2:
            raise serializers.ValidationError("O nome da editora deve ter pelo menos 2 caracteres.")
        
        # Verifica se contém apenas letras, espaços e caracteres especiais comuns
        if not re.match(r'^[A-Za-zÀ-ÿ0-9\s\-\.,&]+$', value):
            raise serializers.ValidationError("O nome da editora contém caracteres inválidos.")
        
        return value

class LivroSerializer(serializers.ModelSerializer):
    genero = serializers.PrimaryKeyRelatedField(queryset=Genero.objects.all())
    editora = serializers.PrimaryKeyRelatedField(queryset=Editora.objects.all())
    
    # Campos apenas para leitura que mostram os nomes
    genero_nome = serializers.CharField(source='genero.nome', read_only=True)
    editora_nome = serializers.CharField(source='editora.nome', read_only=True)
    
    class Meta:
        model = Livro
        fields = [
            'id', 'titulo', 'numero_paginas', 'capa', 'isbn', 'autor', 
            'ano_publicacao', 'editora', 'editora_nome', 'resumo', 
            'genero', 'genero_nome', 'criado_em', 'atualizado_em'
        ]
        read_only_fields = ('criado_em', 'atualizado_em')

    def to_representation(self, instance):
        """
        Customiza a representação para mostrar apenas strings nos campos
        genero e editora na resposta.
        """
        representation = super().to_representation(instance)
        
        # Remove os campos write_only da resposta
        representation.pop('genero', None)
        representation.pop('editora', None)
        
        # Renomeia os campos de leitura para os nomes principais
        representation['genero'] = representation.pop('genero_nome')
        representation['editora'] = representation.pop('editora_nome')
        
        return representation
