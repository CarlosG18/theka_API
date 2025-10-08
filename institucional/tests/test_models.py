import os
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from ..models import (
    topicos, SobreNos, NossaHistoria, MembrosEquipe, 
    NossosValores, EstatisticasBiblioteca
)
from library.models import Livro, Genero, Editora


class TopicosModelTest(TestCase):
    """Testes para o modelo topicos"""
    
    def setUp(self):
        self.topico = topicos.objects.create(nome="Tecnologia")
    
    def test_criacao_topico(self):
        """Testa a criação de um tópico"""
        self.assertEqual(self.topico.nome, "Tecnologia")
        self.assertTrue(isinstance(self.topico, topicos))
    
    def test_string_representation(self):
        """Testa a representação em string do tópico"""
        self.assertEqual(str(self.topico), "Tecnologia")
    
    def test_nome_unico(self):
        """Testa que o nome do tópico deve ser único"""
        with self.assertRaises(IntegrityError):
            topicos.objects.create(nome="Tecnologia")
    
    def test_ordering(self):
        """Testa a ordenação dos tópicos"""
        topicos.objects.create(nome="Arte")
        topicos.objects.create(nome="Ciência")
        
        topicos_list = list(topicos.objects.all())
        self.assertEqual(topicos_list[0].nome, "Arte")
        self.assertEqual(topicos_list[1].nome, "Ciência")
        self.assertEqual(topicos_list[2].nome, "Tecnologia")
    
    def test_verbose_names(self):
        """Testa os nomes verbose do modelo"""
        self.assertEqual(topicos._meta.verbose_name, "Tópico")
        self.assertEqual(topicos._meta.verbose_name_plural, "Tópicos")


class NossaHistoriaModelTest(TestCase):
    """Testes para o modelo NossaHistoria"""
    
    def setUp(self):
        self.historia = NossaHistoria.objects.create(
            descricao="Nossa história começa em 2020...",
            imagem=SimpleUploadedFile("historia.jpg", b"file_content", content_type="image/jpeg")
        )
    
    def test_criacao_nossa_historia(self):
        """Testa a criação de uma instância de NossaHistoria"""
        self.assertEqual(self.historia.descricao, "Nossa história começa em 2020...")
        self.assertTrue(self.historia.imagem.name.startswith('historia/'))
    
    def test_verbose_names(self):
        """Testa os nomes verbose do modelo"""
        self.assertEqual(NossaHistoria._meta.verbose_name, "Nossa História")
        self.assertEqual(NossaHistoria._meta.verbose_name_plural, "Nossa História")


class MembrosEquipeModelTest(TestCase):
    """Testes para o modelo MembrosEquipe"""
    
    def setUp(self):
        self.membro = MembrosEquipe.objects.create(
            nome="João Silva",
            cargo="Desenvolvedor",
            foto=SimpleUploadedFile("foto.jpg", b"file_content", content_type="image/jpeg")
        )
    
    def test_criacao_membro_equipe(self):
        """Testa a criação de um membro da equipe"""
        self.assertEqual(self.membro.nome, "João Silva")
        self.assertEqual(self.membro.cargo, "Desenvolvedor")
        self.assertTrue(self.membro.foto.name.startswith('equipe/'))
    
    def test_criacao_membro_sem_foto(self):
        """Testa a criação de um membro da equipe sem foto"""
        membro_sem_foto = MembrosEquipe.objects.create(
            nome="Maria Santos",
            cargo="Designer"
        )
        self.assertFalse(membro_sem_foto.foto)
    
    def test_string_representation(self):
        """Testa a representação em string do membro"""
        self.assertEqual(str(self.membro), "João Silva")
    
    def test_ordering(self):
        """Testa a ordenação dos membros"""
        MembrosEquipe.objects.create(nome="Ana Costa", cargo="Gerente")
        MembrosEquipe.objects.create(nome="Carlos Lima", cargo="Analista")
        
        membros = list(MembrosEquipe.objects.all())
        self.assertEqual(membros[0].nome, "Ana Costa")
        self.assertEqual(membros[1].nome, "Carlos Lima")
        self.assertEqual(membros[2].nome, "João Silva")
    
    def test_verbose_names(self):
        """Testa os nomes verbose do modelo"""
        self.assertEqual(MembrosEquipe._meta.verbose_name, "Membro da Equipe")
        self.assertEqual(MembrosEquipe._meta.verbose_name_plural, "Membros da Equipe")


class NossosValoresModelTest(TestCase):
    """Testes para o modelo NossosValores"""
    
    def setUp(self):
        self.valor = NossosValores.objects.create(
            valor="Inovação",
            descricao="Valorizamos a inovação constante",
            imagem=SimpleUploadedFile("valor.jpg", b"file_content", content_type="image/jpeg")
        )
    
    def test_criacao_nossos_valores(self):
        """Testa a criação de um valor"""
        self.assertEqual(self.valor.valor, "Inovação")
        self.assertEqual(self.valor.descricao, "Valorizamos a inovação constante")
        self.assertTrue(self.valor.imagem.name.startswith('valores/'))
    
    def test_criacao_valor_sem_imagem_descricao(self):
        """Testa a criação de um valor sem imagem e descrição"""
        valor_simples = NossosValores.objects.create(valor="Qualidade")
        self.assertEqual(valor_simples.valor, "Qualidade")
        self.assertIsNone(valor_simples.descricao)
        self.assertFalse(valor_simples.imagem)
    
    def test_string_representation(self):
        """Testa a representação em string do valor"""
        self.assertEqual(str(self.valor), "Inovação")
    
    def test_verbose_names(self):
        """Testa os nomes verbose do modelo"""
        self.assertEqual(NossosValores._meta.verbose_name, "Nosso Valor")
        self.assertEqual(NossosValores._meta.verbose_name_plural, "Nossos Valores")


class EstatisticasBibliotecaModelTest(TestCase):
    """Testes para o modelo EstatisticasBiblioteca"""
    
    def setUp(self):
        self.estatisticas = EstatisticasBiblioteca.objects.create(
            total_livros=100,
            total_autores=50,
            total_categorias=10,
            total_usuarios=200
        )
    
    def test_criacao_estatisticas(self):
        """Testa a criação de estatísticas"""
        self.assertEqual(self.estatisticas.total_livros, 100)
        self.assertEqual(self.estatisticas.total_autores, 50)
        self.assertEqual(self.estatisticas.total_categorias, 10)
        self.assertEqual(self.estatisticas.total_usuarios, 200)
    
    def test_valores_padrao(self):
        """Testa os valores padrão das estatísticas"""
        estatisticas_padrao = EstatisticasBiblioteca.objects.create()
        self.assertEqual(estatisticas_padrao.total_livros, 0)
        self.assertEqual(estatisticas_padrao.total_autores, 0)
        self.assertEqual(estatisticas_padrao.total_categorias, 0)
        self.assertEqual(estatisticas_padrao.total_usuarios, 0)
    
    def test_string_representation(self):
        """Testa a representação em string das estatísticas"""
        self.assertEqual(str(self.estatisticas), "Estatísticas da Biblioteca")
    
    def test_metodo_atualizar_estatisticas(self):
        """Testa o método atualizar_estatisticas"""
        self.estatisticas.atualizar_estatisticas(
            livros=150,
            autores=75,
            categorias=15,
            usuarios=300
        )
        
        self.estatisticas.refresh_from_db()
        self.assertEqual(self.estatisticas.total_livros, 150)
        self.assertEqual(self.estatisticas.total_autores, 75)
        self.assertEqual(self.estatisticas.total_categorias, 15)
        self.assertEqual(self.estatisticas.total_usuarios, 300)
    
    def test_verbose_names(self):
        """Testa os nomes verbose do modelo"""
        self.assertEqual(EstatisticasBiblioteca._meta.verbose_name, "Estatística da Biblioteca")
        self.assertEqual(EstatisticasBiblioteca._meta.verbose_name_plural, "Estatísticas da Biblioteca")


class SobreNosModelTest(TestCase):
    """Testes para o modelo SobreNos"""
    
    def setUp(self):
        # Criar objetos relacionados
        self.historia = NossaHistoria.objects.create(
            descricao="Nossa história...",
            imagem=SimpleUploadedFile("historia.jpg", b"file_content", content_type="image/jpeg")
        )
        
        self.estatisticas = EstatisticasBiblioteca.objects.create(
            total_livros=100,
            total_autores=50,
            total_categorias=10,
            total_usuarios=200
        )
        
        # Criar tópicos
        self.topico1 = topicos.objects.create(nome="Missão")
        self.topico2 = topicos.objects.create(nome="Visão")
        
        # Criar membros da equipe
        self.membro1 = MembrosEquipe.objects.create(nome="João", cargo="Dev")
        self.membro2 = MembrosEquipe.objects.create(nome="Maria", cargo="Design")
        
        # Criar valores
        self.valor1 = NossosValores.objects.create(valor="Qualidade")
        self.valor2 = NossosValores.objects.create(valor="Inovação")
        
        # Criar SobreNos
        self.sobre_nos = SobreNos.objects.create(
            banner=SimpleUploadedFile("banner.jpg", b"file_content", content_type="image/jpeg"),
            descricao="Descrição sobre nós",
            nossa_historia=self.historia,
            estatisticas_biblioteca=self.estatisticas
        )
        
        # Adicionar relações ManyToMany
        self.sobre_nos.topicos.add(self.topico1, self.topico2)
        self.sobre_nos.membros_equipe.add(self.membro1, self.membro2)
        self.sobre_nos.nossos_valores.add(self.valor1, self.valor2)
    
    def test_criacao_sobre_nos(self):
        """Testa a criação de uma instância de SobreNos"""
        self.assertEqual(self.sobre_nos.descricao, "Descrição sobre nós")
        self.assertTrue(self.sobre_nos.banner.name.startswith('banners/'))
        self.assertEqual(self.sobre_nos.nossa_historia, self.historia)
        self.assertEqual(self.sobre_nos.estatisticas_biblioteca, self.estatisticas)
    
    def test_relacoes_many_to_many(self):
        """Testa as relações ManyToMany"""
        self.assertEqual(self.sobre_nos.topicos.count(), 2)
        self.assertEqual(self.sobre_nos.membros_equipe.count(), 2)
        self.assertEqual(self.sobre_nos.nossos_valores.count(), 2)
        
        self.assertIn(self.topico1, self.sobre_nos.topicos.all())
        self.assertIn(self.membro1, self.sobre_nos.membros_equipe.all())
        self.assertIn(self.valor1, self.sobre_nos.nossos_valores.all())
    
    def test_string_representation(self):
        """Testa a representação em string"""
        self.assertEqual(str(self.sobre_nos), "Informações Sobre Nós")
    
    def test_verbose_names(self):
        """Testa os nomes verbose do modelo"""
        self.assertEqual(SobreNos._meta.verbose_name, "Sobre Nós")
        self.assertEqual(SobreNos._meta.verbose_name_plural, "Sobre Nós")


class SignalsTest(TestCase):
    """Testes para os signals"""
    
    def setUp(self):
        self.editora = Editora.objects.create(nome="Editora Teste")
        self.genero = Genero.objects.create(nome="Ficção")
        
        # Criar estatísticas iniciais
        self.estatisticas = EstatisticasBiblioteca.objects.create(id=1)
    
    def test_signal_atualizar_estatisticas_livros(self):
        """Testa o signal para atualizar estatísticas de livros"""
        # Criar um livro
        livro = Livro.objects.create(
            titulo="Livro Teste",
            isbn="978-85-333-0227-3",
            autor="Autor Teste",
            editora=self.editora,
            resumo="Resumo do livro teste",
            genero=self.genero
        )
        
        # Verificar se as estatísticas foram atualizadas
        self.estatisticas.refresh_from_db()
        self.assertEqual(self.estatisticas.total_livros, 1)
    
    def test_signal_atualizar_estatisticas_usuarios(self):
        """Testa o signal para atualizar estatísticas de usuários"""
        # Criar um usuário
        User.objects.create_user(username="testuser", password="testpass")
        
        # Verificar se as estatísticas foram atualizadas
        self.estatisticas.refresh_from_db()
        self.assertEqual(self.estatisticas.total_usuarios, 1)  # +1 do usuário criado no setUp
    
    def test_signal_atualizar_estatisticas_categorias(self):
        """Testa o signal para atualizar estatísticas de categorias"""
        # Criar um tópico
        topicos.objects.create(nome="Nova Categoria")
        
        # Verificar se as estatísticas foram atualizadas
        self.estatisticas.refresh_from_db()
        self.assertEqual(self.estatisticas.total_categorias, 1)
    
    def test_signal_criacao_estatisticas_automatica(self):
        """Testa que as estatísticas são criadas automaticamente se não existirem"""
        # Deletar estatísticas existentes
        EstatisticasBiblioteca.objects.all().delete()
        
        # Criar um livro - deve disparar o signal e criar estatísticas
        livro = Livro.objects.create(
            titulo="Livro Teste",
            isbn="978-85-333-0227-3",
            autor="Autor Teste",
            editora=self.editora,
            resumo="Resumo do livro teste",
            genero=self.genero
        )
        
        # Verificar se as estatísticas foram criadas automaticamente
        estatisticas = EstatisticasBiblioteca.objects.get(id=1)
        self.assertEqual(estatisticas.total_livros, 1)
    
    def test_signal_multiplos_livros(self):
        """Testa que o signal atualiza corretamente com múltiplos livros"""
        # Criar vários livros
        Livro.objects.create(
            titulo="Livro 1",
            isbn="978-85-333-0227-1",
            autor="Autor 1",
            editora=self.editora,
            resumo="Resumo 1",
            genero=self.genero
        )
        Livro.objects.create(
            titulo="Livro 2",
            isbn="978-85-333-0227-2",
            autor="Autor 2",
            editora=self.editora,
            resumo="Resumo 2",
            genero=self.genero
        )
        
        # Verificar se as estatísticas foram atualizadas corretamente
        self.estatisticas.refresh_from_db()
        self.assertEqual(self.estatisticas.total_livros, 2)