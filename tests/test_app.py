from app import create_app, db
from app.models import User


def test_home_and_login(tmp_path):
    db_path = tmp_path / "test.db"
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}", "SECRET_KEY": "test", "WTF_CSRF_ENABLED": False})
    with app.app_context():
        user = User(name="Admin", email="admin@test.local", role="admin")
        user.set_password("pass123")
        db.session.add(user)
        db.session.commit()
    client = app.test_client()
    assert client.get("/").status_code == 200
    response = client.post("/login", data={"email": "admin@test.local", "password": "pass123"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Dashboard" in response.data
