from rest_framework import serializers
from .models import SobreNos, NossaHistoria, MembrosEquipe, NossosValores, topicos, Contato

class SobreNosSerializer(serializers.ModelSerializer):
    class Meta:
        model = SobreNos
        fields = ['banner', 'descricao']

        read_only_fields = ['topicos', 'nossa_historia', 'membros_equipe', 'nossos_valores', 'estatisticas_biblioteca']

class NossaHistoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = NossaHistoria
        fields = '__all__'

class MembrosEquipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembrosEquipe
        fields = '__all__'

class NossosValoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = NossosValores
        fields = '__all__'

class TopicosSerializer(serializers.ModelSerializer):
    class Meta:
        model = topicos
        fields = '__all__'

class ContatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contato
        fields = '__all__'


