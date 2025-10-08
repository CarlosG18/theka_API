from django.contrib.auth.models import User
from rest_framework import serializers
from django.core.validators import validate_email
import re

class UserSerializer(serializers.ModelSerializer):
    # Campo de confirmação de senha (apenas para escrita)
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }
        read_only_fields = ('id', 'username')

    def validate_email(self, value):
        """
        Validação customizada para o campo email
        """
        if not value:
            raise serializers.ValidationError("O campo email é obrigatório.")
        
        # Valida formato do email
        try:
            validate_email(value)
        except:
            raise serializers.ValidationError("Por favor, insira um endereço de email válido.")
        
        # Verifica se o email já está em uso (apenas para criação)
        if self.instance is None:  # Se é uma criação (não atualização)
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("Este email já está em uso.")
        
        return value.lower()  # Normaliza para minúsculas

    def validate_password(self, value):
        """
        Validação de força da senha
        """
        if len(value) < 8:
            raise serializers.ValidationError("A senha deve ter pelo menos 8 caracteres.")
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("A senha deve conter pelo menos uma letra maiúscula.")
        
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("A senha deve conter pelo menos uma letra minúscula.")
        
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("A senha deve conter pelo menos um número.")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("A senha deve conter pelo menos um caractere especial.")
        
        return value

    def validate_first_name(self, value):
        """
        Validação para o primeiro nome
        """
        if value:
            if len(value.strip()) < 2:
                raise serializers.ValidationError("O primeiro nome deve ter pelo menos 2 caracteres.")
            
            if not value.replace(' ', '').isalpha():
                raise serializers.ValidationError("O primeiro nome deve conter apenas letras.")
        
        return value.strip() if value else value

    def validate_last_name(self, value):
        """
        Validação para o sobrenome
        """
        if value:
            if len(value.strip()) < 2:
                raise serializers.ValidationError("O sobrenome deve ter pelo menos 2 caracteres.")
            
            if not value.replace(' ', '').isalpha():
                raise serializers.ValidationError("O sobrenome deve conter apenas letras.")
        
        return value.strip() if value else value

    def validate(self, attrs):
        """
        Validação que envolve múltiplos campos
        """
        # Verifica se as senhas coincidem
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm', None)
        
        if password and password_confirm and password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': "As senhas não coincidem."
            })
        
        # Verifica se primeiro nome e último nome não são iguais
        first_name = attrs.get('first_name', '').lower().strip()
        last_name = attrs.get('last_name', '').lower().strip()
        
        if first_name and last_name and first_name == last_name:
            raise serializers.ValidationError({
                'first_name': "Primeiro nome e sobrenome não podem ser iguais.",
                'last_name': "Primeiro nome e sobrenome não podem ser iguais."
            })
        
        return attrs

    def create(self, validated_data):
        """
        Criação do usuário com senha criptografada
        """
        # Remove password_confirm do validated_data
        validated_data.pop('password_confirm', None)
        
        # Cria o usuário com a senha criptografada
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        """
        Atualização do usuário
        """
        # Remove password_confirm do validated_data
        validated_data.pop('password_confirm', None)
        
        # Atualiza a senha se for fornecida
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        # Atualiza os outros campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance