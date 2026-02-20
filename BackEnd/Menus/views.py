from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import MenuConfig

class MenuActivoView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        menu = MenuConfig.objects.first()
        if menu:
            return Response(menu.configuracion)
        return Response([])

class MenuConfigView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        menu = MenuConfig.objects.first()
        if not menu:
            menu = MenuConfig()
        
        # Guardamos directamente la lista recibida desde el frontend
        menu.configuracion = request.data
        menu.save()
        return Response({"success": True})
