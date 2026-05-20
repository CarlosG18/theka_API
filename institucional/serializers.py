from rest_framework import serializers
from .models import SobreNos, NossaHistoria, MembrosEquipe, NossosValores, topicos, Contato, EstatisticasBiblioteca


class OptionalImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if data == '':
            return None
        return super().to_internal_value(data)


class SobreNosSerializer(serializers.ModelSerializer):
    banner = OptionalImageField(required=False, allow_null=True)

    class Meta:
        model = SobreNos
        fields = ['banner', 'descricao']

        read_only_fields = ['topicos', 'nossa_historia', 'membros_equipe', 'nossos_valores', 'estatisticas_biblioteca']

class NossaHistoriaSerializer(serializers.ModelSerializer):
    imagem = OptionalImageField(required=False, allow_null=True)

    class Meta:
        model = NossaHistoria
        fields = '__all__'

class MembrosEquipeSerializer(serializers.ModelSerializer):
    foto = OptionalImageField(required=False, allow_null=True)

    class Meta:
        model = MembrosEquipe
        fields = '__all__'

class NossosValoresSerializer(serializers.ModelSerializer):
    imagem = OptionalImageField(required=False, allow_null=True)

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

class EstatisticasBibliotecaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstatisticasBiblioteca
        fields = '__all__'
