# Manejador de Excepciones — custom_exception_handler

**Archivo fuente:** `BackEnd/BackEnd/exceptions.py`  
**Registrado en:** `settings.py → REST_FRAMEWORK['EXCEPTION_HANDLER']`

---

## Propósito

Garantizar que **toda respuesta de error** de la API siga el mismo formato predecible:

```json
{"error": "Descripción del error"}
```

Esto simplifica enormemente el manejo de errores en el frontend Vue: siempre se lee `response.data.error` sin importar el tipo de excepción.

---

## Implementación

```python
def custom_exception_handler(exc, context):
    # 1. Primero llama al handler por defecto de DRF
    response = exception_handler(exc, context)
    
    # 2. Si DRF no puede manejarlo → 500
    if response is None:
        return Response({
            'error': 'Ha ocurrido un error inesperado en el servidor.',
            'detail': str(exc)
        }, status=500)
    
    # 3. Si la respuesta ya tiene 'error', 'detail', 'mensaje' o 'message' → preservar
    if isinstance(response.data, dict):
        if 'error' in response.data or 'detail' in response.data or 'mensaje' in response.data:
            return response
        
        # 4. Errores de campos de serializer → aplanar
        error_messages = []
        for field, errors in response.data.items():
            if isinstance(errors, list):
                error_msg = ' '.join([str(e) for e in errors])
                error_messages.append(f"{field.capitalize()}: {error_msg}")
            else:
                error_messages.append(f"{field.capitalize()}: {str(errors)}")
        
        if error_messages:
            response.data = {'error': ' | '.join(error_messages)}
    
    # 5. Lista de errores → aplanar en string
    elif isinstance(response.data, list):
        response.data = {'error': ' '.join([str(e) for e in response.data])}
    
    return response
```

---

## Casos manejados

### Caso 1: Error 500 no manejado por DRF

```python
# Excepción: ZeroDivisionError, KeyError, etc.
response = None
# → Se devuelve:
{"error": "Ha ocurrido un error inesperado en el servidor.", "detail": "division by zero"}
```

### Caso 2: Excepciones propias de DRF con `detail`

```python
# raise PermissionDenied("No tienes acceso")
# → DRF genera: {"detail": "No tienes acceso"}
# → Ya tiene 'detail' → se preserva tal cual
{"detail": "No tienes acceso"}
```

### Caso 3: Errores de validación de serializer (diccionario de campos)

```python
# serializer.errors = {
#   'uid_sala': ['Este campo es obligatorio.'],
#   'numero_serie': ['Ensure this value has at most 100 characters.']
# }
# → Se aplana:
{"error": "Uid_sala: Este campo es obligatorio. | Numero_serie: Ensure this value..."}
```

### Caso 4: Respuestas con `error` ya formateado (vistas que devuelven manualmente)

```python
# return Response({'error': 'Casino no encontrado'}, status=404)
# → Ya tiene 'error' → se preserva sin modificar
{"error": "Casino no encontrado"}
```

---

## Tabla de transformaciones

| Tipo de respuesta DRF original | Resultado final |
|---|---|
| `None` (excepción no DRF) | `{"error": "...", "detail": "..."}` con 500 |
| `{"detail": "..."}` | Sin cambios |
| `{"error": "..."}` | Sin cambios |
| `{"campo": ["error1", "error2"]}` | `{"error": "Campo: error1 error2"}` |
| `["error1", "error2"]` | `{"error": "error1 error2"}` |

---

## Impacto en el frontend

```javascript
// En cualquier servicio Vue, el manejo es uniforme:
try {
  const response = await api.post('/maquinas/', data)
} catch (error) {
  // Siempre existe error.response.data.error — no hay que inspeccionar la estructura
  toast.error(error.response.data.error)
}
```
