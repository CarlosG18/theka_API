from django.contrib.auth.models import User
from rest_framework import serializers
from django.core.validators import validate_email
import re
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.html import strip_tags

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
        read_only_fields = ('id',)

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

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Não existe usuário com este email.")
        return value

    def save(self):
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        
        # Gerar token e uid
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Construir URL de reset
        reset_url = f"{settings.FRONTEND_URL}/password-reset-confirm/{uid}/{token}/"
        
        # Contexto para o template de email
        context = {
            'user': user,
            'reset_url': reset_url,
            'site_name': 'Sua Aplicação',  # Nome da sua aplicação
        }
        
        # Renderizar template HTML
        html_message = render_to_string('emails/password_reset.html', context)
        plain_message = strip_tags(html_message)
        
        # Enviar email
        send_mail(
            subject='Redefinição de Senha - Sua Aplicação',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )

class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "As senhas não coincidem."})
        return data

    def validate_uid(self, value):
        try:
            from django.utils.encoding import force_str
            from django.utils.http import urlsafe_base64_decode
            uid = force_str(urlsafe_base64_decode(value))
            self.user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            raise serializers.ValidationError("Link inválido.")
        return value

    def validate_token(self, value):
        if not hasattr(self, 'user'):
            return value
            
        if not default_token_generator.check_token(self.user, value):
            raise serializers.ValidationError("Token inválido ou expirado.")
        return value

    def save(self):
        user = self.user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user