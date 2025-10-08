from django.shortcuts import render
from rest_framework import permissions, viewsets, status, filters
from .models import SobreNos, NossaHistoria, MembrosEquipe, NossosValores, topicos, Contato
from .serializers import SobreNosSerializer, NossaHistoriaSerializer, MembrosEquipeSerializer, NossosValoresSerializer, TopicosSerializer, ContatoSerializer
from rest_framework.response import Response

# Create your views here.
class SobreNosViewSet(viewsets.ModelViewSet):
    queryset = SobreNos.objects.all()
    serializer_class = SobreNosSerializer
    #permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

class NossaHistoriaViewSet(viewsets.ModelViewSet):
    queryset = NossaHistoria.objects.all()
    serializer_class = NossaHistoriaSerializer
    #permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

class MembrosEquipeViewSet(viewsets.ModelViewSet):
    queryset = MembrosEquipe.objects.all()
    serializer_class = MembrosEquipeSerializer
    #permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

class NossosValoresViewSet(viewsets.ModelViewSet):  
    queryset = NossosValores.objects.all()
    serializer_class = NossosValoresSerializer
    #permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

class TopicosViewSet(viewsets.ModelViewSet):
    queryset = topicos.objects.all()
    serializer_class = TopicosSerializer
    #permission_classes = [permissions.IsAuthenticated]
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
    
class ContatoViewSet(viewsets.ModelViewSet):
    queryset = Contato.objects.all()
    serializer_class = ContatoSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    #permission_classes = [permissions.IsAuthenticated]

    