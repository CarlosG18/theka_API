from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from library.models import Livro
from django.contrib.auth.models import User

class topicos(models.Model):
    """
        modelo para representar tópicos institucionais.
    """
    nome = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['nome']
        verbose_name = "Tópico"
        verbose_name_plural = "Tópicos"

    def __str__(self):
        return self.nome

# Create your models here.
class SobreNos(models.Model):
    """
        modelo para representar informações sobre a empresa.
    """
    banner = models.ImageField(upload_to='banners/', blank=True, null=True)
    descricao = models.TextField()
    
    class Meta:
        verbose_name = "Sobre Nós"
        verbose_name_plural = "Sobre Nós"

    def __str__(self):
        return "Informações Sobre Nós"
    
class NossaHistoria(models.Model):
    """
        modelo para representar a história da empresa.
    """
    descricao = models.TextField()
    imagem = models.ImageField(upload_to='historia/', blank=True, null=True)

    class Meta:
        verbose_name = "Nossa História"
        verbose_name_plural = "Nossa História"
    
class MembrosEquipe(models.Model):
    """
        modelo para representar membros da equipe.
    """
    nome = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='equipe/', blank=True, null=True)

    class Meta:
        ordering = ['nome']
        verbose_name = "Membro da Equipe"
        verbose_name_plural = "Membros da Equipe"

    def __str__(self):
        return self.nome
    
class NossosValores(models.Model):
    """
        modelo para representar os valores da empresa.
    """
    valor = models.CharField(max_length=255)
    imagem = models.ImageField(upload_to='valores/', blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['valor']
        verbose_name = "Nosso Valor"
        verbose_name_plural = "Nossos Valores"

    def __str__(self):
        return self.valor
    
class Contato(models.Model):
    """
        modelo para representar informações de contato.
    """
    telefone = models.CharField(max_length=20)
    site = models.URLField(blank=True, null=True)
    localizacao = models.CharField(max_length=255, blank=True, null=True)
    link_instagram = models.URLField(blank=True, null=True)
    link_tiktok = models.URLField(blank=True, null=True)
    link_x = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = "Contato"
        verbose_name_plural = "Contatos"

    def __str__(self):
        return f"Contato: {self.email}"
    
class EstatisticasBiblioteca(models.Model):
    """
        modelo para representar estatísticas da biblioteca.
    """
    total_livros = models.PositiveIntegerField(default=0)
    total_autores = models.PositiveIntegerField(default=0)
    total_categorias = models.PositiveIntegerField(default=0)
    total_usuarios = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Estatística da Biblioteca"
        verbose_name_plural = "Estatísticas da Biblioteca"

    def __str__(self):
        return "Estatísticas da Biblioteca"
    
    def atualizar_estatisticas(self, livros, autores, categorias, usuarios):
        """
            método para atualizar as estatísticas da biblioteca.
        """
        self.total_livros = livros
        self.total_autores = autores
        self.total_categorias = categorias
        self.total_usuarios = usuarios
        self.save()

@receiver(post_save, sender=Livro)
def atualizar_estatisticas_livros(sender, instance, **kwargs):
    estatisticas, created = EstatisticasBiblioteca.objects.get_or_create(id=1)
    total_livros = Livro.objects.count()
    estatisticas.atualizar_estatisticas(
        livros=total_livros,
        autores=estatisticas.total_autores,
        categorias=estatisticas.total_categorias,
        usuarios=estatisticas.total_usuarios
    )

@receiver(post_save, sender=User)
def atualizar_estatisticas_usuarios(sender, instance, **kwargs):
    estatisticas, created = EstatisticasBiblioteca.objects.get_or_create(id=1)
    total_usuarios = User.objects.count()
    estatisticas.atualizar_estatisticas(
        livros=estatisticas.total_livros,
        autores=estatisticas.total_autores,
        categorias=estatisticas.total_categorias,
        usuarios=total_usuarios
    )

@receiver(post_save, sender=topicos)
def atualizar_estatisticas_categorias(sender, instance, **kwargs):
    estatisticas, created = EstatisticasBiblioteca.objects.get_or_create(id=1)
    total_categorias = topicos.objects.count()
    estatisticas.atualizar_estatisticas(
        livros=estatisticas.total_livros,
        autores=estatisticas.total_autores,
        categorias=total_categorias,
        usuarios=estatisticas.total_usuarios
    )