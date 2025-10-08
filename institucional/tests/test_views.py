import os
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from ..models import SobreNos, NossaHistoria, MembrosEquipe, NossosValores, topicos, EstatisticasBiblioteca


class BaseViewSetTest(APITestCase):
    """Classe base para configuração comum dos testes"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Criar dados de teste comuns
        self.historia = NossaHistoria.objects.create(
            descricao="Nossa história de teste"
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
        self.membro1 = MembrosEquipe.objects.create(
            nome="João Silva",
            cargo="Desenvolvedor"
        )
        self.membro2 = MembrosEquipe.objects.create(
            nome="Maria Santos",
            cargo="Designer"
        )
        
        # Criar valores
        self.valor1 = NossosValores.objects.create(
            valor="Qualidade",
            descricao="Buscamos sempre a melhor qualidade"
        )
        self.valor2 = NossosValores.objects.create(
            valor="Inovação",
            descricao="Valorizamos a inovação constante"
        )
        
        # Criar SobreNos
        self.sobre_nos = SobreNos.objects.create(
            descricao="Descrição sobre nós"
        )


class SobreNosViewSetTest(BaseViewSetTest):
    """Testes para o SobreNosViewSet"""
    
    def test_list_sobre_nos(self):
        """Testa listagem de SobreNos"""
        url = reverse('sobrenos-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Verificar apenas os campos existentes no modelo
        sobre_nos_data = response.data[0]
        self.assertEqual(sobre_nos_data['descricao'], "Descrição sobre nós")
        
        # Verificar que campos removidos não estão presentes
        self.assertNotIn('topicos', sobre_nos_data)
        self.assertNotIn('nossa_historia', sobre_nos_data)
        self.assertNotIn('membros_equipe', sobre_nos_data)
        self.assertNotIn('nossos_valores', sobre_nos_data)
        self.assertNotIn('estatisticas_biblioteca', sobre_nos_data)
    
    def test_retrieve_sobre_nos(self):
        """Testa recuperação de um SobreNos específico"""
        url = reverse('sobrenos-detail', kwargs={'pk': self.sobre_nos.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['descricao'], "Descrição sobre nós")
        
        # Verificar que campos removidos não estão presentes
        self.assertNotIn('topicos', response.data)
        self.assertNotIn('nossa_historia', response.data)
        self.assertNotIn('membros_equipe', response.data)
        self.assertNotIn('nossos_valores', response.data)
        self.assertNotIn('estatisticas_biblioteca', response.data)
    
    def test_create_sobre_nos(self):
        """Testa criação de SobreNos"""
        url = reverse('sobrenos-list')
        data = {
            'descricao': 'Nova descrição sobre nós'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SobreNos.objects.count(), 2)
        self.assertEqual(response.data['descricao'], 'Nova descrição sobre nós')
        
        # Verificar que apenas os campos corretos estão na resposta
        self.assertIn('descricao', response.data)
        self.assertNotIn('topicos', response.data)
        self.assertNotIn('nossa_historia', response.data)
        self.assertNotIn('membros_equipe', response.data)
        self.assertNotIn('nossos_valores', response.data)
        self.assertNotIn('estatisticas_biblioteca', response.data)
    
    def test_create_sobre_nos_com_banner(self):
        """Testa criação de SobreNos com banner (campo opcional)"""
        url = reverse('sobrenos-list')
        data = {
            'descricao': 'Descrição com banner',
            'banner': ''  # Campo opcional pode ser vazio
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SobreNos.objects.count(), 2)
        self.assertEqual(response.data['descricao'], 'Descrição com banner')
    
    def test_update_sobre_nos(self):
        """Testa atualização de SobreNos"""
        url = reverse('sobrenos-detail', kwargs={'pk': self.sobre_nos.pk})
        data = {
            'descricao': 'Descrição atualizada'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.sobre_nos.refresh_from_db()
        self.assertEqual(self.sobre_nos.descricao, 'Descrição atualizada')
    
    def test_delete_sobre_nos(self):
        """Testa exclusão de SobreNos"""
        url = reverse('sobrenos-detail', kwargs={'pk': self.sobre_nos.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(SobreNos.objects.count(), 0)


class NossaHistoriaViewSetTest(BaseViewSetTest):
    """Testes para o NossaHistoriaViewSet"""
    
    def test_list_nossa_historia(self):
        """Testa listagem de NossaHistoria"""
        url = reverse('nossahistoria-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_retrieve_nossa_historia(self):
        """Testa recuperação de uma NossaHistoria específica"""
        url = reverse('nossahistoria-detail', kwargs={'pk': self.historia.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['descricao'], "Nossa história de teste")
    
    def test_create_nossa_historia(self):
        """Testa criação de NossaHistoria"""
        url = reverse('nossahistoria-list')
        data = {
            'descricao': 'Nova história da empresa'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(NossaHistoria.objects.count(), 2)
        self.assertEqual(response.data['descricao'], 'Nova história da empresa')
    
    def test_create_nossa_historia_com_imagem(self):
        """Testa criação de NossaHistoria com imagem (campo opcional)"""
        url = reverse('nossahistoria-list')
        data = {
            'descricao': 'História com imagem',
            'imagem': ''  # Campo opcional pode ser vazio
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(NossaHistoria.objects.count(), 2)
        self.assertEqual(response.data['descricao'], 'História com imagem')
    
    def test_update_nossa_historia(self):
        """Testa atualização de NossaHistoria"""
        url = reverse('nossahistoria-detail', kwargs={'pk': self.historia.pk})
        data = {
            'descricao': 'História atualizada'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.historia.refresh_from_db()
        self.assertEqual(self.historia.descricao, 'História atualizada')
    
    def test_delete_nossa_historia(self):
        """Testa exclusão de NossaHistoria"""
        url = reverse('nossahistoria-detail', kwargs={'pk': self.historia.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(NossaHistoria.objects.count(), 0)


class MembrosEquipeViewSetTest(BaseViewSetTest):
    """Testes para o MembrosEquipeViewSet"""
    
    def test_list_membros_equipe(self):
        """Testa listagem de MembrosEquipe"""
        url = reverse('membrosequipe-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_retrieve_membro_equipe(self):
        """Testa recuperação de um membro específico"""
        url = reverse('membrosequipe-detail', kwargs={'pk': self.membro1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], "João Silva")
        self.assertEqual(response.data['cargo'], "Desenvolvedor")
    
    def test_create_membro_equipe(self):
        """Testa criação de MembrosEquipe"""
        url = reverse('membrosequipe-list')
        data = {
            'nome': 'Novo Membro',
            'cargo': 'Novo Cargo'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MembrosEquipe.objects.count(), 3)
        self.assertEqual(response.data['nome'], 'Novo Membro')
        self.assertEqual(response.data['cargo'], 'Novo Cargo')
    
    def test_create_membro_equipe_com_foto(self):
        """Testa criação de MembrosEquipe com foto (campo opcional)"""
        url = reverse('membrosequipe-list')
        data = {
            'nome': 'Membro Com Foto',
            'cargo': 'Cargo Teste',
            'foto': ''  # Campo opcional pode ser vazio
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MembrosEquipe.objects.count(), 3)
        self.assertEqual(response.data['nome'], 'Membro Com Foto')
    
    def test_update_membro_equipe(self):
        """Testa atualização de MembrosEquipe"""
        url = reverse('membrosequipe-detail', kwargs={'pk': self.membro1.pk})
        data = {
            'cargo': 'Desenvolvedor Sênior'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.membro1.refresh_from_db()
        self.assertEqual(self.membro1.cargo, 'Desenvolvedor Sênior')
    
    def test_delete_membro_equipe(self):
        """Testa exclusão de MembrosEquipe"""
        url = reverse('membrosequipe-detail', kwargs={'pk': self.membro1.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(MembrosEquipe.objects.count(), 1)


class NossosValoresViewSetTest(BaseViewSetTest):
    """Testes para o NossosValoresViewSet"""
    
    def test_list_nossos_valores(self):
        """Testa listagem de NossosValores"""
        url = reverse('nossosvalores-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_retrieve_nosso_valor(self):
        """Testa recuperação de um valor específico"""
        url = reverse('nossosvalores-detail', kwargs={'pk': self.valor1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['valor'], "Qualidade")
        self.assertEqual(response.data['descricao'], "Buscamos sempre a melhor qualidade")
    
    def test_create_nosso_valor(self):
        """Testa criação de NossosValores"""
        url = reverse('nossosvalores-list')
        data = {
            'valor': 'Transparência',
            'descricao': 'Agimos com transparência em todas as ações'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(NossosValores.objects.count(), 3)
        self.assertEqual(response.data['valor'], 'Transparência')
    
    def test_create_nosso_valor_com_imagem(self):
        """Testa criação de NossosValores com imagem (campo opcional)"""
        url = reverse('nossosvalores-list')
        data = {
            'valor': 'Valor com Imagem',
            'descricao': 'Descrição do valor',
            'imagem': ''  # Campo opcional pode ser vazio
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(NossosValores.objects.count(), 3)
        self.assertEqual(response.data['valor'], 'Valor com Imagem')
    
    def test_create_nosso_valor_sem_descricao(self):
        """Testa criação de NossosValores sem descrição (campo opcional)"""
        url = reverse('nossosvalores-list')
        data = {
            'valor': 'Valor Sem Descrição'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(NossosValores.objects.count(), 3)
        self.assertEqual(response.data['valor'], 'Valor Sem Descrição')
        self.assertIsNone(response.data['descricao'])
    
    def test_update_nosso_valor(self):
        """Testa atualização de NossosValores"""
        url = reverse('nossosvalores-detail', kwargs={'pk': self.valor1.pk})
        data = {
            'descricao': 'Descrição atualizada da qualidade'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.valor1.refresh_from_db()
        self.assertEqual(self.valor1.descricao, 'Descrição atualizada da qualidade')
    
    def test_delete_nosso_valor(self):
        """Testa exclusão de NossosValores"""
        url = reverse('nossosvalores-detail', kwargs={'pk': self.valor1.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(NossosValores.objects.count(), 1)


class TopicosViewSetTest(BaseViewSetTest):
    """Testes para o TopicosViewSet"""
    
    def test_list_topicos(self):
        """Testa listagem de tópicos"""
        url = reverse('topicos-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_retrieve_topico(self):
        """Testa recuperação de um tópico específico"""
        url = reverse('topicos-detail', kwargs={'pk': self.topico1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], "Missão")
    
    def test_create_topico(self):
        """Testa criação de tópico"""
        url = reverse('topicos-list')
        data = {
            'nome': 'Novo Tópico'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(topicos.objects.count(), 3)
        self.assertEqual(response.data['nome'], 'Novo Tópico')
    
    def test_create_topico_duplicado(self):
        """Testa que não é possível criar tópico com nome duplicado"""
        url = reverse('topicos-list')
        data = {
            'nome': 'Missão'  # Já existe
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('nome', response.data)
    
    def test_update_topico(self):
        """Testa atualização de tópico"""
        url = reverse('topicos-detail', kwargs={'pk': self.topico1.pk})
        data = {
            'nome': 'Missão Atualizada'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.topico1.refresh_from_db()
        self.assertEqual(self.topico1.nome, 'Missão Atualizada')
    
    def test_delete_topico(self):
        """Testa exclusão de tópico"""
        url = reverse('topicos-detail', kwargs={'pk': self.topico1.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(topicos.objects.count(), 1)