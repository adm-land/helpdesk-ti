import io
from app import create_app, db
from app.models import User, Ticket, Attachment


def make_app(tmp_path):
    db_path = tmp_path / "test.db"
    return create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "SECRET_KEY": "test",
        "WTF_CSRF_ENABLED": False,
        "UPLOAD_FOLDER": str(tmp_path / "uploads"),
    })


def login(client):
    return client.post("/login", data={"email": "admin@test.local", "password": "pass123"}, follow_redirects=True)


def create_admin(app):
    with app.app_context():
        user = User(name="Admin", email="admin@test.local", role="admin")
        user.set_password("pass123")
        db.session.add(user)
        db.session.commit()


def create_ticket(client):
    return client.post("/tickets/new", data={
        "title": "Falla de red",
        "category": "Red",
        "priority": "Alta",
        "description": "No hay conectividad en el equipo de pruebas.",
    }, follow_redirects=True)


def test_health(tmp_path):
    app = make_app(tmp_path)
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_home_and_login(tmp_path):
    app = make_app(tmp_path)
    create_admin(app)
    client = app.test_client()
    assert client.get("/").status_code == 200
    response = login(client)
    assert response.status_code == 200
    assert b"Hola, Admin" in response.data


def test_ticket_sla_api_and_export(tmp_path):
    app = make_app(tmp_path)
    create_admin(app)
    client = app.test_client()
    login(client)

    response = create_ticket(client)
    assert response.status_code == 200

    with app.app_context():
        ticket = Ticket.query.first()
        assert ticket is not None
        assert ticket.sla_due_at is not None
        assert round((ticket.sla_due_at - ticket.created_at).total_seconds() / 3600) == 4

    api_response = client.get("/api/tickets")
    assert api_response.status_code == 200
    assert api_response.get_json()[0]["priority"] == "Alta"

    export_response = client.get("/tickets/export.csv")
    assert export_response.status_code == 200
    assert "text/csv" in export_response.content_type
    assert b"Falla de red" in export_response.data


def test_attachment_and_admin_panel(tmp_path):
    app = make_app(tmp_path)
    create_admin(app)
    client = app.test_client()
    login(client)
    create_ticket(client)

    with app.app_context():
        ticket = Ticket.query.first()
        ticket_id = ticket.id

    upload = client.post(
        f"/tickets/{ticket_id}/attachments",
        data={"attachment": (io.BytesIO(b"evidencia de prueba"), "evidencia.txt")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert upload.status_code == 200
    assert b"evidencia.txt" in upload.data

    with app.app_context():
        attachment = Attachment.query.first()
        assert attachment is not None
        attachment_id = attachment.id

    download = client.get(f"/attachments/{attachment_id}")
    assert download.status_code == 200
    assert download.data == b"evidencia de prueba"

    admin = client.get("/admin")
    assert admin.status_code == 200
    assert b"Panel general" in admin.data
