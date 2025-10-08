from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from django.contrib.auth.models import User
from .serializers import UserSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiExample

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=PasswordResetSerializer,
        responses={
            200: {
                'type': 'object', 
                'properties': {
                    'message': {'type': 'string'}
                }
            },
            400: {'description': 'Dados inválidos'}
        },
        examples=[
            OpenApiExample(
                'Exemplo de requisição',
                value={'email': 'usuario@example.com'},
                request_only=True
            ),
            OpenApiExample(
                'Exemplo de resposta',
                value={'message': 'Email de recuperação enviado com sucesso'},
                response_only=True
            )
        ]
    )
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Email de recuperação enviado com sucesso'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=PasswordResetConfirmSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'}
                }
            },
            400: {'description': 'Dados inválidos'}
        },
        examples=[
            OpenApiExample(
                'Exemplo de requisição',
                value={
                    'uid': 'MQ',
                    'token': 'abc123...',
                    'new_password': 'novasenha123',
                    'new_password_confirm': 'novasenha123'
                },
                request_only=True
            ),
            OpenApiExample(
                'Exemplo de resposta',
                value={'message': 'Senha redefinida com sucesso'},
                response_only=True
            )
        ]
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Senha redefinida com sucesso'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)