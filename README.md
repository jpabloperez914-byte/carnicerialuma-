# Sistema de Administración Integral para Carnicería

Este es un sistema de escritorio completo para la administración de una carnicería, desarrollado en Python con una interfaz gráfica de Tkinter y una base de datos SQLite.

## Características Principales

El sistema está diseñado siguiendo una arquitectura Modelo-Vista-Controlador (MVC) para una fácil mantenibilidad y escalabilidad.

- **Gestión de Usuarios:** Soporta dos roles: `administrador` y `empleado`, con diferentes niveles de permisos.
- **Control de Stock y Desposte:** Permite registrar la llegada de materia prima (media res) y su posterior desposte en cortes individuales, actualizando el stock automáticamente.
- **Punto de Venta (POS):** Una interfaz rápida para registrar ventas, buscar productos por código, y aceptar múltiples formas de pago.
- **Módulos de Administración:**
  - **Gestión de Usuarios:** Permite a los administradores crear, editar y desactivar cuentas de usuario.
  - **Reportes y Estadísticas:** Un panel visual con gráficos (usando Matplotlib) para analizar ventas por producto, rendimiento de empleados y horas pico.
- **Seguridad y Mantenibilidad:**
  - **Logging de Actividades:** Las acciones críticas como ventas, inicios de turno y creación de usuarios quedan registradas.
  - **Copias de Seguridad:** Los administradores pueden crear backups de la base de datos con un solo clic.

## Instalación

Para poner en marcha el sistema, sigue estos pasos. Se recomienda usar un entorno virtual de Python.

1.  **Clona o descarga el proyecto.**

2.  **Crea y activa un entorno virtual (recomendado):**
    ```bash
    python -m venv venv
    # En Windows
    venv\\Scripts\\activate
    # En macOS/Linux
    source venv/bin/activate
    ```

3.  **Instala las dependencias:**
    El proyecto depende de `matplotlib`. Instálalo usando el archivo `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

## Cómo Ejecutar la Aplicación

Una vez instaladas las dependencias, el sistema se puede iniciar de dos maneras:

1.  **Inicializar la Base de Datos (solo la primera vez):**
    Antes de ejecutar la aplicación por primera vez, debes crear la base de datos y las tablas. Ejecuta el siguiente script desde la raíz del proyecto:
    ```bash
    python carniceria_system/database/database_setup.py
    ```
    Esto creará el archivo `carniceria.db` y lo llenará con datos de prueba, incluyendo el usuario administrador.

2.  **Iniciar la Aplicación Principal:**
    Para abrir la interfaz gráfica, ejecuta el script `run_app.py`:
    ```bash
    python run_app.py
    ```

## Credenciales de Acceso

El sistema se inicializa con un usuario administrador por defecto:

-   **Usuario:** `admin`
-   **Contraseña:** `admin`

Usa estas credenciales para iniciar sesión por primera vez y acceder a todas las funcionalidades de administración.

## Estructura del Proyecto

El código está organizado en la carpeta `carniceria_system/` de la siguiente manera:
-   `controllers/`: Contiene la lógica de negocio.
-   `models/`: Contiene las clases que representan los datos (ej. `Usuario`, `Producto`).
-   `views/`: Contiene las clases de la interfaz gráfica (ej. `LoginView`, `SalesView`).
-   `utils/`: Contiene módulos de ayuda, como el gestor de la base de datos.
-   `database/`: Contiene el script de setup y almacenará la base de datos y sus backups.
-   `assets/`: Para futuros recursos como iconos o imágenes.
