# HelpDesk TI

Sistema web de **mesa de ayuda y soporte técnico** para registrar, asignar y dar seguimiento a incidencias de TI.

Lo desarrollé como proyecto de portafolio para practicar desarrollo web, bases de datos y procesos que se utilizan en un área de soporte. El objetivo fue ir más allá de un CRUD básico e incluir elementos propios de una mesa de ayuda: responsables, prioridades, SLA, historial, evidencias, métricas, seguridad y exportación de información.

## Demo pública

**Probar aplicación:** https://helpdesk-ti-alan.onrender.com

> La demo utiliza el plan gratuito de Render, por lo que puede tardar unos segundos en iniciar si estuvo inactiva. La base SQLite y los archivos adjuntos son temporales y pueden reiniciarse cuando la instancia se recrea.

### Usuarios de demostración

| Rol | Correo | Contraseña |
|---|---|---|
| Administrador | `admin@helpdesk.local` | `Admin123!` |
| Técnico | `tecnico@helpdesk.local` | `Tecnico123!` |
| Usuario | `usuario@helpdesk.local` | `Usuario123!` |

## Funcionalidades principales

### Gestión de tickets
- Registro de incidencias por categoría y prioridad.
- Estados: **Nuevo**, **En proceso** y **Resuelto**.
- Asignación de responsables.
- Comentarios para documentar el seguimiento.
- Historial de cambios por ticket.
- Búsqueda y filtros.

### SLA y métricas
- SLA por prioridad: Alta 4 h, Media 12 h y Baja 24 h.
- Identificación de tickets vencidos.
- Tiempo promedio de resolución.
- Tasa de resolución.
- Dashboard con indicadores.
- Panel administrativo con gráficas de estados, categorías y carga de trabajo.
- Actividad reciente para el administrador.

### Evidencias y exportación
- Archivos adjuntos PNG, JPG, JPEG, PDF o TXT.
- Límite de 5 MB por archivo.
- Descarga de evidencias con control de acceso.
- Exportación de tickets a CSV.
- API REST de consulta en `/api/tickets`.

### Seguridad y calidad
- Inicio de sesión con roles de usuario, técnico y administrador.
- Contraseñas almacenadas con hash.
- Protección CSRF.
- Pruebas automáticas con Pytest.
- Ejecución de pruebas mediante GitHub Actions.

## Tecnologías

- **Backend:** Python, Flask, SQLAlchemy
- **Base de datos:** SQLite para demo; MySQL / PyMySQL para entorno local con Docker
- **Frontend:** HTML, CSS
- **Autenticación y formularios:** Flask-Login, Flask-WTF
- **Infraestructura:** Docker Compose, Gunicorn, Render
- **Calidad:** Pytest, GitHub Actions

## Estructura del proyecto

```text
helpdesk-ti/
├── app/
│   ├── static/
│   ├── templates/
│   ├── __init__.py
│   ├── demo_data.py
│   ├── models.py
│   └── routes.py
├── tests/
├── bootstrap.py
├── docker-compose.yml
├── render.yaml
├── requirements.txt
├── run.py
├── seed.py
└── wsgi.py
```

## Ejecución local con SQLite

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Crear un archivo `.env`:

```env
SECRET_KEY=una-clave-local
DATABASE_URL=sqlite:///helpdesk.db
```

Cargar los datos de demostración y ejecutar:

```bash
python seed.py
python run.py
```

Abrir `http://127.0.0.1:5000`.

## MySQL con Docker

```bash
docker compose up -d
```

Configurar `.env`:

```env
SECRET_KEY=cambia-esta-clave
DATABASE_URL=mysql+pymysql://helpdesk:helpdesk@localhost:3306/helpdesk
```

Después:

```bash
python seed.py
python run.py
```

> `seed.py` recrea la base de datos de demostración y elimina los datos anteriores.

## Manejo de evidencias

Los archivos se guardan en `instance/uploads`, carpeta que no se versiona en GitHub. El sistema genera un nombre interno para cada archivo y solo permite descargar una evidencia cuando el usuario tiene acceso al ticket correspondiente.

## Despliegue

El repositorio incluye `render.yaml`, Gunicorn y una ruta `/health` para la demo pública en Render. Para un entorno real usaría una base de datos administrada y almacenamiento persistente de archivos; para este proyecto de portafolio mantuve una arquitectura sencilla y sin costos.

## Pruebas

```bash
python -m pytest -q
```

También existe un workflow de GitHub Actions para ejecutar las pruebas cuando se suben cambios a `main`.

## Mejoras futuras

- Notificaciones por correo.
- Reportes por periodo.
- Almacenamiento de archivos en un servicio externo.

## Autor

**Alan Daniel Martínez Martínez**  
Estudiante de Ingeniería en Sistemas Computacionales — UNITEC  
[GitHub](https://github.com/adm-land) · [LinkedIn](https://www.linkedin.com/in/alan-daniel-martinez-mart%C3%ADnez-5215a8218)
