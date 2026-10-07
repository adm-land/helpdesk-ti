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

## Estructura

```text
helpdesk-ti/
├── app/
│   ├── static/
│   ├── templates/
│   ├── __init__.py
│   ├── models.py
│   └── routes.py
├── tests/
├── docker-compose.yml
├── requirements.txt
├── run.py
└── seed.py
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

## Pruebas

```bash
python -m pytest -q
```

También dejé un workflow de GitHub Actions para ejecutar las pruebas cuando se suben cambios a `main`.

## Siguiente paso

Quiero agregar notificaciones por correo y una vista de reportes por periodo. También quiero seguir mejorando las pruebas para cubrir más casos de permisos y archivos.

## Autor

**Alan Daniel Martínez Martínez**  
Estudiante de Ingeniería en Sistemas Computacionales — UNITEC  
[LinkedIn](https://www.linkedin.com/in/alan-daniel-martinez-mart%C3%ADnez-5215a8218)
