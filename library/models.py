from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import datetime
import re
from .utils import validar_isbn10, validar_isbn13
from django.core.validators import MinValueValidator

class Genero(models.Model):
    """
        modelo para representar gêneros literários.
    """
    nome = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['nome']
        verbose_name = "Gênero"
        verbose_name_plural = "Gêneros"

    def __str__(self):
        return self.nome
    
    def clean(self):
        """Validações customizadas para Genero"""
        if self.nome:
            # Remove espaços extras e valida
            self.nome = self.nome.strip()
            if len(self.nome) < 2:
                raise ValidationError({'nome': 'O nome do gênero deve ter pelo menos 2 caracteres.'})
            
            # Verifica se contém apenas letras e espaços
            if not re.match(r'^[A-Za-zÀ-ÿ\s]+$', self.nome):
                raise ValidationError({'nome': 'O nome do gênero deve conter apenas letras e espaços.'})

class Editora(models.Model):
    """
        modelo para representar editoras.
    """
    nome = models.CharField(max_length=255, unique=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        ordering = ['nome']
        verbose_name = "Editora"
        verbose_name_plural = "Editoras"

    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        # Faz o strip antes de salvar
        if self.nome:
            self.nome = self.nome.strip()
        if self.telefone:
            self.telefone = self.telefone.strip()
        if self.email:
            self.email = self.email.strip()
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validações customizadas para Editora"""
        if self.nome:
            self.nome = self.nome.strip()
            if len(self.nome) < 2:
                raise ValidationError({'nome': 'O nome da editora deve ter pelo menos 2 caracteres.'})
        
        if self.telefone and self.telefone.strip():
            # Valida formato básico de telefone
            telefone_limpo = re.sub(r'\D', '', self.telefone)
            if len(telefone_limpo) < 10:
                raise ValidationError({'telefone': 'Telefone inválido. Deve conter pelo menos 10 dígitos.'})

class Livro(models.Model):
    """
        modelo para representar livros.
    """
    titulo = models.CharField(max_length=255)
    numero_paginas = models.PositiveIntegerField(validators=[MinValueValidator(1)], blank=True, null=True)
    capa = models.ImageField(upload_to='capas_livros/', blank=True, null=True)
    isbn = models.CharField("ISBN", max_length=17, unique=True)  # Aumentado para 17 para permitir formatação
    autor = models.CharField(max_length=255)
    ano_publicacao = models.PositiveIntegerField(blank=True, null=True)
    editora = models.ForeignKey(Editora, on_delete=models.CASCADE, related_name='livros')
    resumo = models.TextField()
    genero = models.ForeignKey(Genero, on_delete=models.CASCADE, related_name='livros')

    # Campos automáticos
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = "Livro"
        verbose_name_plural = "Livros"

    def __str__(self):
        return f"{self.titulo} ({self.autor})"
    
    def clean(self):
        """Validações customizadas para Livro"""
        errors = {}
        
        # Validação do título
        if self.titulo:
            self.titulo = self.titulo.strip()
            if len(self.titulo) < 2:
                errors['titulo'] = 'O título deve ter pelo menos 2 caracteres.'
        
        # Validação do número de páginas
        if self.numero_paginas:
            if int(self.numero_paginas) < 1:
                print(self.numero_paginas)
                errors['numero_paginas'] = 'O número de páginas deve ser pelo menos 1.'
            elif int(self.numero_paginas) > 10000:
                errors['numero_paginas'] = 'O número de páginas não pode exceder 10.000.'

        # Validação do autor
        if self.autor:
            self.autor = self.autor.strip()
            if len(self.autor) < 2:
                errors['autor'] = 'O nome do autor deve ter pelo menos 2 caracteres.'
        
        # Validação do ano de publicação
        ano_atual = datetime.now().year
        if self.ano_publicacao:
            if int(self.ano_publicacao) < 1000:
                errors['ano_publicacao'] = 'Ano de publicação inválido.'
            elif int(self.ano_publicacao) > ano_atual:
                errors['ano_publicacao'] = f'Ano de publicação não pode ser no futuro. Ano atual: {ano_atual}'
            
        # Validação do resumo
        if self.resumo:
            self.resumo = self.resumo.strip()
            if len(self.resumo) < 10:
                errors['resumo'] = 'O resumo deve ter pelo menos 10 caracteres.'
            elif len(self.resumo) > 2000:
                errors['resumo'] = 'O resumo não pode exceder 2000 caracteres.'

        if errors:
            raise ValidationError(errors)