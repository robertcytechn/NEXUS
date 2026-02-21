from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    """
    Manejador global para todas las excepciones capturadas por Django Rest Framework.
    Garantiza que el frontend siempre reciba un formato estándar predecible
    (con una clave principal de mensaje de error).
    """

    # Llama al manejador por defecto de DRF primero para obtener la respuesta estándar.
    response = exception_handler(exc, context)

    # Si la respuesta es None, significa que ocurrió una excepción no manejada nativamente por DRF (ej. un error 500 estándar de Python)
    if response is None:
        return Response({
            'error': 'Ha ocurrido un error inesperado en el servidor.',
            'detail': str(exc)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Procesar errores de validación y de serializadores (normalmente diccionarios de listados de errores)
    if isinstance(response.data, dict):
        # Si la respuesta ya tiene 'error', 'detail' o 'mensaje', la preservamos pero la ajustamos si es necesario.
        if 'error' in response.data or 'detail' in response.data or 'mensaje' in response.data or 'message' in response.data:
            return response
            
        # Si son errores de campos específicos (Django forms/serializers) aplanamos los mensajes.
        error_messages = []
        for field, errors in response.data.items():
            if isinstance(errors, list):
                # Usar el primer error del campo o juntarlos
                error_msg = ' '.join([str(e) for e in errors])
                error_messages.append(f"{field.capitalize()}: {error_msg}")
            else:
                error_messages.append(f"{field.capitalize()}: {str(errors)}")
        
        # Juntamos los errores en un solo 'mensaje' de fácil lectura para el frontend (toast)
        if error_messages:
            custom_error = " | ".join(error_messages)
            response.data = {
                'error': custom_error
            }
    
    # Si la respuesta es una lista en crudo (raro, pero posible)
    elif isinstance(response.data, list):
         error_msg = ' '.join([str(e) for e in response.data])
         response.data = {
             'error': error_msg
         }

    return response
