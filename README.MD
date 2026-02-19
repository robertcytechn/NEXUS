# Sistema de Control de Dispositivos y Maquinaria (SCDM) - Red de Casinos

## 📌 Visión General
Este sistema ha sido diseñado para la gestión y control administrativo de máquinas y dispositivos en una red de **17 sucursales de casinos**. La plataforma permite supervisar el estado de los equipos, gestionar bajas, reparaciones y movimientos de inventario de forma manual por parte del personal autorizado.

**Nota importante:** Por seguridad, el sistema NO tiene conexión directa en tiempo real con las máquinas; los cambios de estado son responsabilidad de los usuarios finales.

---

## 🛠️ Stack Tecnológico
Para garantizar la estabilidad y el control que requiere la dirección de sistemas, se utilizan las siguientes tecnologías:

- **Backend:** Python 3.14 + Django & Django REST Framework (DRF).
- **Base de Datos:** MySQL (Conexión mediante `PyMySQL` debido a compatibilidad de entorno).
- **Frontend:** Vue.js 3 + PrimeVue (Basado en el tema **Sakai**).
- **Gestión de Estado:** Pinia.
- **Consumo de API:** Axios.

---

## 🏗️ Arquitectura y Reglas de Negocio

### 1. Jerarquía de Permisos (Roles)
El control de acceso se basa en un nivel jerárquico numérico:
- **Rango:** 0 a 200 (siendo 200 el nivel máximo de administración).
- Toda validación de API y visibilidad en el frontend debe contrastarse contra este valor numérico.

### 2. Gestión de Sucursales
El sistema opera sobre 17 ubicaciones físicas fijas. Cada sucursal cuenta con 3 usuarios operativos planeados. Se deben registrar horarios de apertura/cierre y correos de contacto para gerencia y soporte técnico en cada sede.

### 3. Seguridad y Sesión Única
- **Sesión Unitaria:** Se permite estrictamente una sola sesión activa por usuario.
- **Control de Tokens:** Al iniciar sesión en un nuevo dispositivo, cualquier sesión previa en otros navegadores o dispositivos debe ser invalidada automáticamente mediante la comparación del `session_token` en la base de datos.
- **Identidad:** No se utiliza el sistema de usuarios nativo de Django; se emplea una tabla personalizada `UsuarioPropio` vinculada a Roles y Sucursales.

### 4. Estándar de Auditoría (Modelo Base)
Todas las entidades de la base de datos deben heredar de un `ModeloBase` abstracto que incluya:
- **Borrado Lógico:** Uso del campo `esta_activo` (boolean) en lugar de eliminar registros físicos.
- **Trazabilidad:** Registro automático de `creado_en`, `modificado_en`, `creado_por` y `modificado_por`.

---

## 🗄️ Estructura de Base de Datos (Principales)



- **Roles:** ID, nombre, descripción, nivel (0-200).
- **Sucursales:** ID, nombre, código interno, dirección, teléfonos, correos (gerente/técnico), horarios.
- **Usuarios:** Username, password (hash), email, nombre completo, fecha de nacimiento, rol (FK), sucursal (FK), último token.
- **Logs:** Auditoría detallada de acciones por usuario y módulo.

---

## 🚀 Guía de Desarrollo para IA (Gemini/Copilot)
Cuando trabajes en este proyecto, sigue estas directrices estrictas:
1. **Frontend:** Usa exclusivamente componentes de **PrimeVue** siguiendo la estética de **Sakai**.
2. **Backend:** Prioriza la seguridad de los endpoints verificando siempre el nivel de jerarquía (0-200) del usuario que realiza la petición.
3. **Conectividad:** La API debe estar configurada para manejar CORS, ya que el Frontend y el Backend corren de forma desacoplada.