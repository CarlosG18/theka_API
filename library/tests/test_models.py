# tests/test_models.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from library.models import Genero, Editora, Livro
from datetime import datetime
import re

class GeneroModelTest(TestCase):
    """Testes para o modelo Genero"""
    
    def setUp(self):
        self.genero_valido = Genero(nome="Ficção Científica")
    
    def test_criacao_genero_valido(self):
        """Testa a criação de um gênero válido"""
        self.genero_valido.full_clean()
        self.genero_valido.save()
        self.assertEqual(Genero.objects.count(), 1)
        self.assertEqual(str(self.genero_valido), "Ficção Científica")
    
    def test_nome_obrigatorio(self):
        """Testa que nome é obrigatório"""
        genero = Genero(nome="")
        with self.assertRaises(ValidationError):
            genero.full_clean()
    
    def test_nome_minimo_caracteres(self):
        """Testa validação de nome com menos de 2 caracteres"""
        genero = Genero(nome="A")
        with self.assertRaises(ValidationError) as context:
            genero.full_clean()
        self.assertIn('nome', context.exception.error_dict)
    
    def test_nome_apenas_letras_e_espacos(self):
        """Testa validação de caracteres especiais no nome"""
        casos_invalidos = ["Ficção123", "Romance!", "Ação@"]
        for nome in casos_invalidos:
            with self.subTest(nome=nome):
                genero = Genero(nome=nome)
                with self.assertRaises(ValidationError) as context:
                    genero.full_clean()
                self.assertIn('nome', context.exception.error_dict)
    
    def test_nomes_validos_com_acentos(self):
        """Testa que nomes com acentos são válidos"""
        nomes_validos = ["Ação", "Romântico", "Ficção Científica", "Literatura Infantil"]
        for nome in nomes_validos:
            with self.subTest(nome=nome):
                genero = Genero(nome=nome)
                try:
                    genero.full_clean()
                    genero.save()
                except ValidationError:
                    self.fail(f"Nome válido '{nome}' não deveria falhar na validação")
    
    def test_nome_unico(self):
        """Testa que nome deve ser único"""
        Genero.objects.create(nome="Romance")
        genero_duplicado = Genero(nome="Romance")
        with self.assertRaises(IntegrityError):
            genero_duplicado.save()
    
    def test_trim_espacos(self):
        """Testa que espaços extras são removidos"""
        genero = Genero(nome="  Fantasia  ")
        genero.full_clean()
        genero.save()
        genero_salvo = Genero.objects.get(pk=genero.pk)
        self.assertEqual(genero_salvo.nome, "Fantasia")
    
    def test_meta_ordering(self):
        """Testa ordenação padrão"""
        Genero.objects.create(nome="Zebra")
        Genero.objects.create(nome="Abacate")
        generos = Genero.objects.all()
        self.assertEqual(generos[0].nome, "Abacate")
        self.assertEqual(generos[1].nome, "Zebra")
    
    def test_verbose_names(self):
        """Testa nomes amigáveis"""
        self.assertEqual(Genero._meta.verbose_name, "Gênero")
        self.assertEqual(Genero._meta.verbose_name_plural, "Gêneros")

class EditoraModelTest(TestCase):
    """Testes para o modelo Editora"""
    
    def setUp(self):
        self.editora_valida = Editora(
            nome="Editora Teste",
            endereco="Rua Teste, 123",
            telefone="(11) 99999-9999",
            email="contato@editora.com"
        )
    
    def test_criacao_editora_valida(self):
        """Testa criação de editora válida"""
        self.editora_valida.full_clean()
        self.editora_valida.save()
        self.assertEqual(Editora.objects.count(), 1)
        self.assertEqual(str(self.editora_valida), "Editora Teste")
    
    def test_nome_obrigatorio(self):
        """Testa que nome é obrigatório"""
        editora = Editora(nome="")
        with self.assertRaises(ValidationError):
            editora.full_clean()
    
    def test_nome_minimo_caracteres(self):
        """Testa validação de nome com menos de 2 caracteres"""
        editora = Editora(nome="A")
        with self.assertRaises(ValidationError) as context:
            editora.full_clean()
        self.assertIn('nome', context.exception.error_dict)
    
    def test_nome_unico(self):
        """Testa que nome deve ser único"""
        Editora.objects.create(nome="Editora A")
        editora_duplicada = Editora(nome="Editora A")
        with self.assertRaises(IntegrityError):
            editora_duplicada.save()
    
    def test_telefone_valido(self):
        """Testa validação de telefone válido"""
        telefones_validos = [
            "(11) 99999-9999",
            "11999999999",
            "11 99999 9999",
            "(11) 9999-9999"
        ]
        for telefone in telefones_validos:
            with self.subTest(telefone=telefone):
                editora = Editora(nome=f"Editora {telefone}", telefone=telefone)
                try:
                    editora.full_clean()
                except ValidationError:
                    self.fail(f"Telefone válido '{telefone}' não deveria falhar")
    
    def test_telefone_invalido(self):
        """Testa validação de telefone inválido"""
        telefones_invalidos = [
            "123",
            "abc",
            "(11) 999-999",
            "119999999"  # apenas 9 dígitos
        ]
        for telefone in telefones_invalidos:
            with self.subTest(telefone=telefone):
                editora = Editora(nome=f"Editora {telefone}", telefone=telefone)
                with self.assertRaises(ValidationError) as context:
                    editora.full_clean()
                self.assertIn('telefone', context.exception.error_dict)
    
    def test_email_valido(self):
        """Testa validação de email válido"""
        emails_validos = [
            "test@example.com",
            "test.name@example.com",
            "test+name@example.com.br"
        ]
        for email in emails_validos:
            with self.subTest(email=email):
                editora = Editora(nome=f"Editora {email}", email=email)
                try:
                    editora.full_clean()
                except ValidationError:
                    self.fail(f"Email válido '{email}' não deveria falhar")
    
    def test_email_invalido(self):
        """Testa validação de email inválido"""
        emails_invalidos = [
            "invalid",
            "invalid@",
            "@invalid.com",
            "invalid@com"
        ]
        for email in emails_invalidos:
            with self.subTest(email=email):
                editora = Editora(nome=f"Editora {email}", email=email)
                with self.assertRaises(ValidationError) as context:
                    editora.full_clean()
                self.assertIn('email', context.exception.error_dict)
    
    def test_campos_opcionais(self):
        """Testa que endereço, telefone e email são opcionais"""
        editora = Editora(nome="Editora Simples")
        try:
            editora.full_clean()
            editora.save()
        except ValidationError:
            self.fail("Editora com apenas nome obrigatório não deveria falhar")
    
    def test_trim_espacos(self):
        """Testa que espaços extras são removidos"""
        editora = Editora(nome="  Editora Teste  ", email="    test@test.com  ")
        editora.clean()
        editora.save()
        editora_salva = Editora.objects.get(pk=editora.pk)
        self.assertEqual(editora_salva.nome, "Editora Teste")
        self.assertEqual(editora_salva.email, "test@test.com")
    
    def test_meta_ordering(self):
        """Testa ordenação padrão"""
        Editora.objects.create(nome="Z Editora")
        Editora.objects.create(nome="A Editora")
        editoras = Editora.objects.all()
        self.assertEqual(editoras[0].nome, "A Editora")
        self.assertEqual(editoras[1].nome, "Z Editora")

class LivroModelTest(TestCase):
    """Testes para o modelo Livro"""
    
    def setUp(self):
        self.genero = Genero.objects.create(nome="Ficção Científica")
        self.editora = Editora.objects.create(nome="Editora Teste")
        
        self.livro_valido = Livro(
            titulo="Dom Quixote",
            numero_paginas=863,
            isbn="9788525426334",
            autor="Miguel de Cervantes",
            ano_publicacao=1605,
            editora=self.editora,
            resumo="As aventuras de um fidalgo que enlouquece após ler muitos romances de cavalaria.",
            genero=self.genero
        )
    
    def test_criacao_livro_valido(self):
        """Testa criação de livro válido"""
        self.livro_valido.full_clean()
        self.livro_valido.save()
        self.assertEqual(Livro.objects.count(), 1)
        self.assertEqual(str(self.livro_valido), "Dom Quixote (Miguel de Cervantes)")
    
    def test_campos_obrigatorios(self):
        """Testa que todos os campos obrigatórios são validados"""
        campos_obrigatorios = ['titulo', 'numero_paginas', 'isbn', 'autor', 
                              'ano_publicacao', 'editora', 'resumo', 'genero']
        
        for campo in campos_obrigatorios:
            with self.subTest(campo=campo):
                livro_invalido = Livro(
                    titulo="Teste",
                    numero_paginas=100,
                    isbn="9780123456789",
                    autor="Autor Teste",
                    ano_publicacao=2020,
                    editora=self.editora,
                    resumo="Resumo teste com mais de 10 caracteres",
                    genero=self.genero
                )
                
                # Remove um campo por vez
                if campo == 'editora':
                    livro_invalido.editora = None
                elif campo == 'genero':
                    livro_invalido.genero = None
                else:
                    setattr(livro_invalido, campo, "")
                
                with self.assertRaises(ValidationError):
                    livro_invalido.full_clean()
    
    def test_titulo_minimo_caracteres(self):
        """Testa validação de título com menos de 2 caracteres"""
        livro = Livro(
            titulo="A",
            numero_paginas=100,
            isbn="9780123456789",
            autor="Autor Teste",
            ano_publicacao=2020,
            editora=self.editora,
            resumo="Resumo válido com mais de 10 caracteres",
            genero=self.genero
        )
        with self.assertRaises(ValidationError) as context:
            livro.full_clean()
        self.assertIn('titulo', context.exception.error_dict)
    
    def test_numero_paginas_minimo(self):
        """Testa validação de número de páginas mínimo"""
        livro = Livro(
            titulo="Livro Teste",
            numero_paginas=0,
            isbn="9780123456789",
            autor="Autor Teste",
            ano_publicacao=2020,
            editora=self.editora,
            resumo="Resumo válido com mais de 10 caracteres",
            genero=self.genero
        )
        with self.assertRaises(ValidationError) as context:
            livro.full_clean()
        self.assertIn('numero_paginas', context.exception.error_dict)
    
    def test_numero_paginas_maximo(self):
        """Testa validação de número de páginas máximo"""
        livro = Livro(
            titulo="Livro Teste",
            numero_paginas=10001,
            isbn="9780123456789",
            autor="Autor Teste",
            ano_publicacao=2020,
            editora=self.editora,
            resumo="Resumo válido com mais de 10 caracteres",
            genero=self.genero
        )
        with self.assertRaises(ValidationError) as context:
            livro.full_clean()
        self.assertIn('numero_paginas', context.exception.error_dict)
    
    def test_isbn_unico(self):
        """Testa que ISBN deve ser único"""
        self.livro_valido.save()
        
        livro_duplicado = Livro(
            titulo="Outro Livro",
            numero_paginas=200,
            isbn=self.livro_valido.isbn,
            autor="Outro Autor",
            ano_publicacao=2021,
            editora=self.editora,
            resumo="Outro resumo válido com mais de 10 caracteres",
            genero=self.genero
        )
        
        with self.assertRaises(IntegrityError):
            livro_duplicado.save()
    
    def test_autor_minimo_caracteres(self):
        """Testa validação de autor com menos de 2 caracteres"""
        livro = Livro(
            titulo="Livro Teste",
            numero_paginas=100,
            isbn="9780123456789",
            autor="A",
            ano_publicacao=2020,
            editora=self.editora,
            resumo="Resumo válido com mais de 10 caracteres",
            genero=self.genero
        )
        with self.assertRaises(ValidationError) as context:
            livro.full_clean()
        self.assertIn('autor', context.exception.error_dict)
    
    def test_ano_publicacao_minimo(self):
        """Testa validação de ano de publicação mínimo"""
        livro = Livro(
            titulo="Livro Teste",
            numero_paginas=100,
            isbn="9780123456789",
            autor="Autor Teste",
            ano_publicacao=999,
            editora=self.editora,
            resumo="Resumo válido com mais de 10 caracteres",
            genero=self.genero
        )
        with self.assertRaises(ValidationError) as context:
            livro.full_clean()
        self.assertIn('ano_publicacao', context.exception.error_dict)
    
    def test_ano_publicacao_futuro(self):
        """Testa que ano de publicação não pode ser no futuro"""
        ano_futuro = datetime.now().year + 1
        livro = Livro(
            titulo="Livro Teste",
            numero_paginas=100,
            isbn="9780123456789",
            autor="Autor Teste",
            ano_publicacao=ano_futuro,
            editora=self.editora,
            resumo="Resumo válido com mais de 10 caracteres",
            genero=self.genero
        )
        with self.assertRaises(ValidationError) as context:
            livro.full_clean()
        self.assertIn('ano_publicacao', context.exception.error_dict)
    
    def test_resumo_minimo_caracteres(self):
        """Testa validação de resumo com menos de 10 caracteres"""
        livro = Livro(
            titulo="Livro Teste",
            numero_paginas=100,
            isbn="9780123456789",
            autor="Autor Teste",
            ano_publicacao=2020,
            editora=self.editora,
            resumo="Pouco",
            genero=self.genero
        )
        with self.assertRaises(ValidationError) as context:
            livro.full_clean()
        self.assertIn('resumo', context.exception.error_dict)
    
    def test_resumo_maximo_caracteres(self):
        """Testa validação de resumo com mais de 2000 caracteres"""
        resumo_longo = "X" * 2001
        livro = Livro(
            titulo="Livro Teste",
            numero_paginas=100,
            isbn="9780123456789",
            autor="Autor Teste",
            ano_publicacao=2020,
            editora=self.editora,
            resumo=resumo_longo,
            genero=self.genero
        )
        with self.assertRaises(ValidationError) as context:
            livro.full_clean()
        self.assertIn('resumo', context.exception.error_dict)
    
    def test_meta_ordering(self):
        """Testa ordenação padrão (mais recente primeiro)"""
        livro1 = Livro.objects.create(
            titulo="Livro Antigo",
            numero_paginas=100,
            isbn="9780123456781",
            autor="Autor 1",
            ano_publicacao=2020,
            editora=self.editora,
            resumo="Resumo válido com mais de 10 caracteres",
            genero=self.genero
        )
        
        livro2 = Livro.objects.create(
            titulo="Livro Recente",
            numero_paginas=200,
            isbn="9780123456782",
            autor="Autor 2",
            ano_publicacao=2021,
            editora=self.editora,
            resumo="Outro resumo válido com mais de 10 caracteres",
            genero=self.genero
        )
        
        livros = Livro.objects.all()
        self.assertEqual(livros[0].titulo, "Livro Recente")
        self.assertEqual(livros[1].titulo, "Livro Antigo")
    
    def test_relacionamentos(self):
        """Testa relacionamentos com Editora e Genero"""
        self.livro_valido.save()
        
        # Testa relacionamento com Editora
        self.assertEqual(self.livro_valido.editora, self.editora)
        self.assertEqual(self.editora.livros.count(), 1)
        self.assertEqual(self.editora.livros.first(), self.livro_valido)
        
        # Testa relacionamento com Genero
        self.assertEqual(self.livro_valido.genero, self.genero)
        self.assertEqual(self.genero.livros.count(), 1)
        self.assertEqual(self.genero.livros.first(), self.livro_valido)

class ModelIntegrationTest(TestCase):
    """Testes de integração entre os modelos"""
    
    def test_cascata_delete_editora(self):
        """Testa que livros são deletados quando editora é deletada"""
        genero = Genero.objects.create(nome="Teste")
        editora = Editora.objects.create(nome="Editora Teste")
        
        Livro.objects.create(
            titulo="Livro 1",
            numero_paginas=100,
            isbn="9780123456781",
            autor="Autor 1",
            ano_publicacao=2020,
            editora=editora,
            resumo="Resumo válido com mais de 10 caracteres",
            genero=genero
        )
        
        Livro.objects.create(
            titulo="Livro 2",
            numero_paginas=200,
            isbn="9780123456782",
            autor="Autor 2",
            ano_publicacao=2021,
            editora=editora,
            resumo="Outro resumo válido com mais de 10 caracteres",
            genero=genero
        )
        
        self.assertEqual(Livro.objects.count(), 2)
        editora.delete()
        self.assertEqual(Livro.objects.count(), 0)
    
    def test_cascata_delete_genero(self):
        """Testa que livros são deletados quando gênero é deletado"""
        genero = Genero.objects.create(nome="Teste")
        editora = Editora.objects.create(nome="Editora Teste")
        
        Livro.objects.create(
            titulo="Livro 1",
            numero_paginas=100,
            isbn="9780123456781",
            autor="Autor 1",
            ano_publicacao=2020,
            editora=editora,
            resumo="Resumo válido com mais de 10 caracteres",
            genero=genero
        )
        
        self.assertEqual(Livro.objects.count(), 1)
        genero.delete()
        self.assertEqual(Livro.objects.count(), 0)