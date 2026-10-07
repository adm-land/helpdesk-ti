# HelpDesk TI

Sistema web para registrar y dar seguimiento a incidencias de soporte técnico. Lo hice como proyecto de portafolio para practicar desarrollo web, bases de datos y procesos que se usan en un área de TI.

La idea fue ir más allá de un CRUD básico y agregar funciones que sí tienen sentido en una mesa de ayuda: responsables, prioridades, tiempos de atención, historial de cambios, métricas, evidencias y exportación de información.

## Funciones principales

- Inicio de sesión con roles de usuario, técnico y administrador.
- Registro de tickets por categoría y prioridad.
- Estados: Nuevo, En proceso y Resuelto.
- Asignación de responsables.
- Comentarios para documentar el seguimiento.
- Historial de cambios por ticket.
- Evidencias adjuntas en PNG, JPG, PDF o TXT.
- Descarga de archivos con control de acceso.
- Límite de 5 MB por archivo.
- SLA por prioridad: Alta 4 h, Media 12 h y Baja 24 h.
- Identificación de tickets vencidos.
- Tiempo promedio de resolución y tasa de resolución.
- Dashboard con indicadores.
- Panel de administración con gráficas de estados, categorías y carga de trabajo.
- Actividad reciente para el administrador.
- Búsqueda y filtros.
- Exportación de tickets a CSV.
- API REST de consulta en `/api/tickets`.
- Contraseñas con hash y protección CSRF.
- Pruebas automáticas con Pytest y GitHub Actions.

## Tecnologías

- Python
- Flask
- SQLAlchemy
- MySQL / PyMySQL
- HTML y CSS
- Flask-Login
- Flask-WTF
- Docker Compose
- Pytest
- GitHub Actions
- Gunicorn

## Estructura

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

## Ejecutarlo con SQLite

```bash
python -m venv .venv
```

En Windows:

```bash
.venv\Scripts\activate
```

En macOS o Linux:

```bash
source .venv/bin/activate
```

Instala las dependencias:

```bash
pip install -r requirements.txt
```

Crea un archivo `.env`:

```env
SECRET_KEY=una-clave-local
DATABASE_URL=sqlite:///helpdesk.db
```

Carga los datos de demostración y ejecuta la aplicación:

```bash
python seed.py
python run.py
```

Abre `http://127.0.0.1:5000`.

### Usuarios de demostración

| Rol | Correo | Contraseña |
|---|---|---|
| Administrador | `admin@helpdesk.local` | `Admin123!` |
| Técnico | `tecnico@helpdesk.local` | `Tecnico123!` |
| Usuario | `usuario@helpdesk.local` | `Usuario123!` |

Son cuentas de prueba y no deben usarse fuera de la base de datos de demostración.

## Evidencias adjuntas

Los archivos se guardan dentro de `instance/uploads`, una carpeta que no se versiona en GitHub. El sistema genera un nombre interno distinto al archivo original para evitar choques entre nombres y solo permite descargar una evidencia si el usuario tiene acceso al ticket.

Formatos permitidos: PNG, JPG, JPEG, PDF y TXT.

## MySQL con Docker

```bash
docker compose up -d
```

En `.env`:

```env
SECRET_KEY=cambia-esta-clave
DATABASE_URL=mysql+pymysql://helpdesk:helpdesk@localhost:3306/helpdesk
```

Después:

```bash
python seed.py
python run.py
```

`seed.py` recrea la base de datos de demostración, por lo que elimina los datos anteriores.

## Demo pública

El repositorio ya incluye `render.yaml`, Gunicorn y una ruta `/health` para publicarlo en Render. La demo gratuita usa SQLite y almacenamiento temporal para las evidencias. Si Render recrea la instancia, `bootstrap.py` vuelve a cargar los usuarios y tickets de ejemplo automáticamente.

Para un sistema real usaría una base de datos administrada y almacenamiento persistente para los archivos. Para el portafolio prefiero mantener la demo sencilla y sin costos.

## Pruebas

```bash
python -m pytest -q
```

También dejé un workflow de GitHub Actions para ejecutar las pruebas cuando se suben cambios a `main`.

## Mejoras futuras

El proyecto ya cubre el flujo principal de una mesa de ayuda. Como mejoras futuras dejaría notificaciones por correo, reportes por periodo y almacenamiento de archivos en un servicio externo.

## Autor

**Alan Daniel Martínez Martínez**  
Estudiante de Ingeniería en Sistemas Computacionales — UNITEC  
[LinkedIn](https://www.linkedin.com/in/alan-daniel-martinez-mart%C3%ADnez-5215a8218)
