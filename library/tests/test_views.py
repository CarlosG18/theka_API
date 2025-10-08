# tests/test_views.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from library.models import Livro, Genero, Editora
from library.serializers import LivroSerializer, GeneroSerializer, EditoraSerializer
import json

class LivroViewSetTest(APITestCase):
    """Testes para LivroViewSet"""
    
    def setUp(self):
        # APITestCase já configura self.client automaticamente
        # Cria dados de teste
        self.genero = Genero.objects.create(nome="Ficção Científica")
        self.editora = Editora.objects.create(
            nome="Editora Teste",
            email="contato@editora.com"
        )
        
        self.livro_data = {
            'titulo': 'Dom Quixote',
            'numero_paginas': 863,
            'isbn': '9788525426334',
            'autor': 'Miguel de Cervantes',
            'ano_publicacao': 1605,
            'editora': self.editora.id,
            'resumo': 'As aventuras de um fidalgo que enlouquece após ler muitos romances de cavalaria.',
            'genero': self.genero.id
        }
        
        # Cria alguns livros para testes de listagem
        self.livro1 = Livro.objects.create(
            titulo="Livro 1",
            numero_paginas=100,
            isbn="9780123456781",
            autor="Autor 1",
            ano_publicacao=2020,
            editora=self.editora,
            resumo="Resumo do livro 1",
            genero=self.genero
        )
        
        self.livro2 = Livro.objects.create(
            titulo="Livro 2",
            numero_paginas=200,
            isbn="9780123456782",
            autor="Autor 2",
            ano_publicacao=2021,
            editora=self.editora,
            resumo="Resumo do livro 2",
            genero=self.genero
        )
    
    def test_list_livros(self):
        """Testa listagem de livros"""
        url = reverse('livro-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['titulo'], 'Livro 2')  # Ordenação por -criado_em
    
    def test_retrieve_livro(self):
        """Testa recuperação de um livro específico"""
        url = reverse('livro-detail', kwargs={'pk': self.livro1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['titulo'], 'Livro 1')
        self.assertEqual(response.data['autor'], 'Autor 1')
    
    def test_create_livro(self):
        """Testa criação de livro"""
        url = reverse('livro-list')
        response = self.client.post(url, self.livro_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Livro.objects.count(), 3)
        self.assertEqual(response.data['titulo'], 'Dom Quixote')
    
    def test_create_livro_invalido(self):
        """Testa criação de livro com dados inválidos"""
        data_invalido = self.livro_data.copy()
        data_invalido['titulo'] = ''  # Título vazio
        
        url = reverse('livro-list')
        response = self.client.post(url, data_invalido, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('titulo', response.data)
    
    def test_update_livro(self):
        """Testa atualização de livro"""
        url = reverse('livro-detail', kwargs={'pk': self.livro1.id})
        data_atualizado = self.livro_data.copy()
        data_atualizado['titulo'] = 'Livro Atualizado'
        
        response = self.client.put(url, data_atualizado, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.livro1.refresh_from_db()
        self.assertEqual(self.livro1.titulo, 'Livro Atualizado')
    
    def test_partial_update_livro(self):
        """Testa atualização parcial de livro"""
        url = reverse('livro-detail', kwargs={'pk': self.livro1.id})
        data_parcial = {'titulo': 'Título Atualizado'}
        
        response = self.client.patch(url, data_parcial, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.livro1.refresh_from_db()
        self.assertEqual(self.livro1.titulo, 'Título Atualizado')
    
    def test_delete_livro(self):
        """Testa exclusão de livro"""
        url = reverse('livro-detail', kwargs={'pk': self.livro1.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Livro.objects.count(), 1)
    
    def test_filtrar_por_genero(self):
        """Testa filtro por gênero"""
        url = reverse('livro-list')
        response = self.client.get(url, {'genero': self.genero.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_filtrar_por_ano_publicacao(self):
        """Testa filtro por ano de publicação"""
        url = reverse('livro-list')
        response = self.client.get(url, {'ano_publicacao': 2020})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['titulo'], 'Livro 1')
    
    def test_buscar_por_titulo(self):
        """Testa busca por título"""
        url = reverse('livro-list')
        response = self.client.get(url, {'search': 'Livro 1'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        titulos = [item['titulo'] for item in response.data['results']]
        self.assertIn('Livro 1', titulos)
    
    def test_buscar_por_autor(self):
        """Testa busca por autor"""
        url = reverse('livro-list')
        response = self.client.get(url, {'autor': 'Autor 2'})  # Use 'autor' em vez de 'search'

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        autores = [item['autor'] for item in response.data['results']]
        self.assertIn('Autor 2', autores)
        
    def test_buscar_por_isbn(self):
        """Testa busca por ISBN"""
        url = reverse('livro-list')
        response = self.client.get(url, {'search': '9780123456781'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['isbn'], '9780123456781')
    
    def test_ordenar_por_titulo(self):
        """Testa ordenação por título"""
        url = reverse('livro-list')
        response = self.client.get(url, {'ordering': 'titulo'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titulos = [item['titulo'] for item in response.data['results']]
        self.assertEqual(titulos, ['Livro 1', 'Livro 2'])
    
    def test_ordenar_por_ano_publicacao_desc(self):
        """Testa ordenação por ano de publicação decrescente"""
        url = reverse('livro-list')
        response = self.client.get(url, {'ordering': '-ano_publicacao'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        anos = [item['ano_publicacao'] for item in response.data['results']]
        self.assertEqual(anos, [2021, 2020])
    
    def test_action_novidades(self):
        """Testa action novidades"""
        # Cria mais livros para testar a limitação
        for i in range(3, 8):
            Livro.objects.create(
                titulo=f"Livro {i}",
                numero_paginas=100 + i,
                isbn=f"978012345678{i}",
                autor=f"Autor {i}",
                ano_publicacao=2020 + i,
                editora=self.editora,
                resumo=f"Resumo do livro {i}",
                genero=self.genero
            )
        
        url = reverse('livro-novidades')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)  # Deve retornar apenas 5
    
    def test_action_destaque_mes(self):
        """Testa action destaque do mês"""
        url = reverse('livro-destaque-mes')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['titulo'], 'Livro 2')  # Último criado
    
    def test_metodos_http_permitidos(self):
        """Testa que apenas métodos HTTP permitidos funcionam"""
        url = reverse('livro-list')
        
        # Métodos permitidos
        response_get = self.client.get(url)
        response_post = self.client.post(url, self.livro_data, format='json')
        
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        self.assertEqual(response_post.status_code, status.HTTP_201_CREATED)

class GeneroViewSetTest(APITestCase):
    """Testes para GeneroViewSet"""
    
    def setUp(self):
        # APITestCase já configura self.client automaticamente
        self.genero1 = Genero.objects.create(nome="Ficção")
        self.genero2 = Genero.objects.create(nome="Romance")
        
        self.genero_data = {
            'nome': 'Aventura'
        }
    
    def test_list_generos(self):
        """Testa listagem de gêneros"""
        url = reverse('genero-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_retrieve_genero(self):
        """Testa recuperação de um gênero específico"""
        url = reverse('genero-detail', kwargs={'pk': self.genero1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], 'Ficção')
    
    def test_create_genero(self):
        """Testa criação de gênero"""
        url = reverse('genero-list')
        response = self.client.post(url, self.genero_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Genero.objects.count(), 3)
        self.assertEqual(response.data['nome'], 'Aventura')
    
    def test_create_genero_invalido(self):
        """Testa criação de gênero com dados inválidos"""
        data_invalido = {'nome': 'A'}  # Nome muito curto
        
        url = reverse('genero-list')
        response = self.client.post(url, data_invalido, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_genero(self):
        """Testa atualização de gênero"""
        url = reverse('genero-detail', kwargs={'pk': self.genero1.id})
        data_atualizado = {'nome': 'Ficção Científica'}
        
        response = self.client.put(url, data_atualizado, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.genero1.refresh_from_db()
        self.assertEqual(self.genero1.nome, 'Ficção Científica')
    
    def test_delete_genero(self):
        """Testa exclusão de gênero"""
        url = reverse('genero-detail', kwargs={'pk': self.genero1.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Genero.objects.count(), 1)

class EditoraViewSetTest(APITestCase):
    """Testes para EditoraViewSet"""
    
    def setUp(self):
        # APITestCase já configura self.client automaticamente
        self.editora1 = Editora.objects.create(
            nome="Editora A",
            email="contato@editora-a.com"
        )
        self.editora2 = Editora.objects.create(
            nome="Editora B", 
            email="contato@editora-b.com"
        )
        
        self.editora_data = {
            'nome': 'Editora C',
            'email': 'contato@editora-c.com',
            'telefone': '(11) 99999-9999'
        }
    
    def test_list_editoras(self):
        """Testa listagem de editoras"""
        url = reverse('editora-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_retrieve_editora(self):
        """Testa recuperação de uma editora específica"""
        url = reverse('editora-detail', kwargs={'pk': self.editora1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], 'Editora A')
    
    def test_create_editora(self):
        """Testa criação de editora"""
        url = reverse('editora-list')
        response = self.client.post(url, self.editora_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Editora.objects.count(), 3)
        self.assertEqual(response.data['nome'], 'Editora C')
    
    def test_create_editora_invalida(self):
        """Testa criação de editora com dados inválidos"""
        data_invalido = {'nome': 'A'}  # Nome muito curto
        
        url = reverse('editora-list')
        response = self.client.post(url, data_invalido, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_editora(self):
        """Testa atualização de editora"""
        url = reverse('editora-detail', kwargs={'pk': self.editora1.id})
        data_atualizado = {
            'nome': 'Editora A Atualizada',
            'email': 'novo@editora-a.com'
        }
        
        response = self.client.put(url, data_atualizado, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.editora1.refresh_from_db()
        self.assertEqual(self.editora1.nome, 'Editora A Atualizada')
        self.assertEqual(self.editora1.email, 'novo@editora-a.com')
    
    def test_delete_editora(self):
        """Testa exclusão de editora"""
        url = reverse('editora-detail', kwargs={'pk': self.editora1.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Editora.objects.count(), 1)

class PaginationTest(APITestCase):
    """Testes específicos para paginação"""
    
    def setUp(self):
        # APITestCase já configura self.client automaticamente
        self.genero = Genero.objects.create(nome="Teste")
        self.editora = Editora.objects.create(nome="Editora Teste")
        
        # Cria múltiplos livros para testar paginação
        for i in range(15):
            Livro.objects.create(
                titulo=f"Livro {i}",
                numero_paginas=100 + i,
                isbn=f"97801234567{i:02d}",
                autor=f"Autor {i}",
                ano_publicacao=2020 + i,
                editora=self.editora,
                resumo=f"Resumo do livro {i}",
                genero=self.genero
            )
    
    def test_paginacao_padrao(self):
        """Testa que a paginação está funcionando"""
        url = reverse('livro-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 10)  # Page size padrão
    
    def test_paginacao_segunda_pagina(self):
        """Testa acesso à segunda página"""
        url = reverse('livro-list')
        response = self.client.get(url, {'page': 2})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)  # 15 total - 10 primeira página

class FilterTest(APITestCase):
    """Testes específicos para filtros"""
    
    def setUp(self):
        # APITestCase já configura self.client automaticamente
        self.genero1 = Genero.objects.create(nome="Ficção")
        self.genero2 = Genero.objects.create(nome="Romance")
        self.editora1 = Editora.objects.create(nome="Editora A")
        self.editora2 = Editora.objects.create(nome="Editora B")
        
        # Livros com diferentes características para testes de filtro
        self.livro1 = Livro.objects.create(
            titulo="Python para Iniciantes",
            numero_paginas=300,
            isbn="9780123456701",
            autor="João Silva",
            ano_publicacao=2020,
            editora=self.editora1,
            resumo="Aprenda Python do zero",
            genero=self.genero1
        )
        
        self.livro2 = Livro.objects.create(
            titulo="Django Avançado",
            numero_paginas=400,
            isbn="9780123456702", 
            autor="Maria Santos",
            ano_publicacao=2021,
            editora=self.editora2,
            resumo="Técnicas avançadas de Django",
            genero=self.genero2
        )
    
    def test_filtro_multiplos_campos(self):
        """Testa filtro combinando múltiplos campos"""
        url = reverse('livro-list')
        response = self.client.get(url, {
            'genero': self.genero1.id,
            'ano_publicacao': 2020
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['titulo'], 'Python para Iniciantes')