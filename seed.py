from app import create_app, db
from app.models import User, Ticket, Comment

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    admin = User(name="Alan Martínez", email="admin@helpdesk.local", role="admin")
    admin.set_password("Admin123!")
    tech = User(name="Sofía Torres", email="tecnico@helpdesk.local", role="technician")
    tech.set_password("Tecnico123!")
    user = User(name="Carlos Mendoza", email="usuario@helpdesk.local", role="user")
    user.set_password("Usuario123!")
    db.session.add_all([admin, tech, user])
    db.session.flush()

    t1 = Ticket(title="Sin acceso al correo corporativo", description="Al iniciar sesión aparece un mensaje de credenciales no válidas. Ya reinicié el equipo.", category="Acceso", priority="Alta", status="En proceso", creator=user, technician=tech)
    t2 = Ticket(title="Equipo con bajo rendimiento", description="La computadora tarda demasiado en iniciar y abrir aplicaciones de oficina.", category="Hardware", priority="Media", status="Nuevo", creator=user)
    t3 = Ticket(title="Intermitencia en red Wi-Fi", description="La conexión se pierde durante varios minutos en la sala de juntas.", category="Red", priority="Alta", status="Resuelto", creator=user, technician=admin)
    db.session.add_all([t1, t2, t3])
    db.session.flush()
    db.session.add(Comment(body="Se validó la cuenta y se solicitó restablecimiento de contraseña.", ticket=t1, author=tech))
    db.session.add(Comment(body="Se revisó el punto de acceso y se ajustó el canal inalámbrico.", ticket=t3, author=admin))
    db.session.commit()
    print("Base de datos de demostración creada.")
