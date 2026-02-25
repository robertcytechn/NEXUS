# Denominacion — Catálogo de Valores Monetarios

**Archivo fuente:** `BackEnd/Denominaciones/models.py`  
**Hereda de:** `models.Model` (directamente, sin `ModeloBase`)  
**Tabla BD:** `cat_denominaciones`  
**Propósito:** Catálogo maestro de los valores monetarios aceptados por las máquinas. Cada `Maquina` puede aceptar múltiples denominaciones mediante relación N:N.

---

## Campos

| Campo | Tipo Django | Nulo | Único | Descripción |
|---|---|---|---|---|
| `valor` | `DecimalField(5,2)` | No | ✅ | Valor numérico (ej. `1.00`, `0.25`) |
| `etiqueta` | `CharField(20)` | No | No | Texto para mostrar (ej. `"$1.00"`, `"$0.25 ctv"`) |

---

## ¿Por qué no hereda ModeloBase?

Es un catálogo simple y estático. No necesita auditoría de creación/modificación, ni borrado lógico. Agregar esos campos añadiría ruido sin valor.

---

## class Meta

```python
class Meta:
    db_table = 'cat_denominaciones'
    verbose_name = "Denominación"
    verbose_name_plural = "Denominaciones"
```
