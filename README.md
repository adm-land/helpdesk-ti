# HelpDesk TI

Sistema web de gestión de incidencias de soporte técnico orientado a un entorno empresarial. Permite registrar tickets, priorizarlos, asignar responsables y documentar su seguimiento hasta la resolución.

## ¿Por qué este proyecto?

Lo desarrollé como parte de mi portafolio de Ingeniería en Sistemas Computacionales para aplicar programación, bases de datos y procesos de soporte TI en un caso cercano a los que utilizan las empresas.

## Funcionalidades

- Inicio de sesión con roles de **usuario, técnico y administrador**.
- Registro de tickets con categoría y prioridad.
- Estados: **Nuevo, En proceso y Resuelto**.
- Asignación de tickets a personal técnico.
- Comentarios e historial básico de seguimiento.
- Dashboard con indicadores de incidencias.
- Búsqueda y filtros por estado y prioridad.
- Acceso restringido: cada usuario consulta sus tickets y el personal de TI puede administrar todos.
- Contraseñas almacenadas con hash, no en texto plano.
- Protección CSRF en formularios para reducir solicitudes no autorizadas.

## Tecnologías

- Python
- Flask
- SQLAlchemy
- MySQL / PyMySQL
- HTML y CSS
- Flask-Login
- Flask-WTF / CSRFProtect
- Docker Compose para levantar MySQL de forma sencilla
- Pytest para pruebas básicas
- GitHub Actions para integración continua (CI)

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

## Ejecución rápida con SQLite

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Crea un archivo `.env` con:

```env
SECRET_KEY=una-clave-local
DATABASE_URL=sqlite:///helpdesk.db
```

Después:

```bash
python seed.py
python run.py
```

Abre `http://127.0.0.1:5000`.

### Usuario de demostración

- Correo: `admin@helpdesk.local`
- Contraseña: `Admin123!`

> Estas credenciales son únicamente para la base de datos de demostración. No deben reutilizarse en un entorno real.

## Uso con MySQL

Levanta la base de datos:

```bash
docker compose up -d
```

Configura `.env`:

```env
SECRET_KEY=cambia-esta-clave
DATABASE_URL=mysql+pymysql://helpdesk:helpdesk@localhost:3306/helpdesk
```

Luego ejecuta:

```bash
python seed.py
python run.py
```

## Pruebas

```bash
pytest
```

## Próximas mejoras

- Adjuntar evidencias o capturas a los tickets.
- Notificaciones por correo.
- Métricas de tiempo de resolución y SLA.
- Exportación de reportes.
- API REST para integración con otros sistemas.

## Autor

**Alan Daniel Martínez Martínez**  
Estudiante de Ingeniería en Sistemas Computacionales — UNITEC  
[LinkedIn](https://www.linkedin.com/in/alan-daniel-martinez-mart%C3%ADnez-5215a8218)
