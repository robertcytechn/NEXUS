from rest_framework import serializers
from .models import WikiTecnica

class WikiTecnicaSerializer(serializers.ModelSerializer):
    # Campos para el reconocimiento público en el frontend de Sakai
    autor_nombre = serializers.CharField(
        source='autor.username', 
        read_only=True
    )
    
    modelo_nombre = serializers.CharField(
        source='modelo_relacionado.nombre_modelo', 
        read_only=True
    )
    
    casino_nombre = serializers.CharField(
        source='casino_origen.nombre', 
        read_only=True
    )

    class Meta:
        model = WikiTecnica
        fields = '__all__'
        
        # Blindaje de auditoría inalterable
        read_only_fields = [
            'puntos_reconocimiento',
            'creado_en',
            'modificado_en',
            'creado_por',
            'modificado_por'
        ]