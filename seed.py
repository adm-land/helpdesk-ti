from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Ticket, Comment, TicketEvent

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

    now = datetime.utcnow()
    tickets = [
        Ticket(title="Sin acceso al correo corporativo", description="Al iniciar sesión aparece un mensaje de credenciales no válidas. Ya reinicié el equipo.", category="Acceso", priority="Alta", status="En proceso", creator=user, technician=tech, created_at=now - timedelta(hours=2), updated_at=now - timedelta(minutes=35)),
        Ticket(title="Equipo con bajo rendimiento", description="La computadora tarda demasiado en iniciar y abrir aplicaciones de oficina.", category="Hardware", priority="Media", status="Nuevo", creator=user, created_at=now - timedelta(hours=3), updated_at=now - timedelta(hours=3)),
        Ticket(title="Intermitencia en red Wi-Fi", description="La conexión se pierde durante varios minutos en la sala de juntas.", category="Red", priority="Alta", status="Resuelto", creator=user, technician=admin, created_at=now - timedelta(hours=6), resolved_at=now - timedelta(hours=4), updated_at=now - timedelta(hours=4)),
        Ticket(title="Actualización de software contable", description="Se requiere actualizar la aplicación contable a la versión autorizada por el área.", category="Software", priority="Baja", status="Resuelto", creator=user, technician=tech, created_at=now - timedelta(hours=30), resolved_at=now - timedelta(hours=22), updated_at=now - timedelta(hours=22)),
        Ticket(title="Impresora de recepción sin conexión", description="La impresora aparece fuera de línea para todos los usuarios de recepción.", category="Red", priority="Alta", status="Nuevo", creator=user, created_at=now - timedelta(hours=8), updated_at=now - timedelta(hours=8)),
    ]
    for ticket in tickets:
        ticket.set_sla_deadline(ticket.created_at)
    db.session.add_all(tickets)
    db.session.flush()

    db.session.add_all([
        Comment(body="Se validó la cuenta y se solicitó restablecimiento de contraseña.", ticket=tickets[0], author=tech),
        Comment(body="Se revisó el punto de acceso y se ajustó el canal inalámbrico.", ticket=tickets[2], author=admin),
        TicketEvent(event_type="Creación", detail="Ticket registrado", ticket=tickets[0], actor=user, created_at=tickets[0].created_at),
        TicketEvent(event_type="Actualización", detail="Estado: Nuevo → En proceso · Responsable: Sin asignar → Sofía Torres", ticket=tickets[0], actor=tech, created_at=now - timedelta(hours=1, minutes=40)),
        TicketEvent(event_type="Creación", detail="Ticket registrado", ticket=tickets[1], actor=user, created_at=tickets[1].created_at),
        TicketEvent(event_type="Creación", detail="Ticket registrado", ticket=tickets[2], actor=user, created_at=tickets[2].created_at),
        TicketEvent(event_type="Actualización", detail="Estado: En proceso → Resuelto · Responsable: Sin asignar → Alan Martínez", ticket=tickets[2], actor=admin, created_at=tickets[2].resolved_at),
        TicketEvent(event_type="Creación", detail="Ticket registrado", ticket=tickets[3], actor=user, created_at=tickets[3].created_at),
        TicketEvent(event_type="Actualización", detail="Estado: En proceso → Resuelto · Responsable: Sin asignar → Sofía Torres", ticket=tickets[3], actor=tech, created_at=tickets[3].resolved_at),
        TicketEvent(event_type="Creación", detail="Ticket registrado", ticket=tickets[4], actor=user, created_at=tickets[4].created_at),
    ])
    db.session.commit()
    print("Base de datos de demostración creada.")
