from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager

SLA_HOURS = {"Alta": 4, "Media": 12, "Baja": 24}


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    created_tickets = db.relationship("Ticket", foreign_keys="Ticket.created_by_id", back_populates="creator")
    assigned_tickets = db.relationship("Ticket", foreign_keys="Ticket.assigned_to_id", back_populates="technician")
    comments = db.relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    events = db.relationship("TicketEvent", back_populates="actor")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_staff(self):
        return self.role in {"technician", "admin"}


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, default="Software")
    priority = db.Column(db.String(20), nullable=False, default="Media")
    status = db.Column(db.String(20), nullable=False, default="Nuevo")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    sla_due_at = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    creator = db.relationship("User", foreign_keys=[created_by_id], back_populates="created_tickets")
    technician = db.relationship("User", foreign_keys=[assigned_to_id], back_populates="assigned_tickets")
    comments = db.relationship("Comment", back_populates="ticket", cascade="all, delete-orphan", order_by="Comment.created_at")
    events = db.relationship("TicketEvent", back_populates="ticket", cascade="all, delete-orphan", order_by="TicketEvent.created_at")

    def set_sla_deadline(self, base_time=None):
        start = base_time or self.created_at or datetime.utcnow()
        self.sla_due_at = start + timedelta(hours=SLA_HOURS.get(self.priority, 12))

    @property
    def is_overdue(self):
        return bool(self.sla_due_at and self.status != "Resuelto" and datetime.utcnow() > self.sla_due_at)

    @property
    def resolution_hours(self):
        if not self.created_at or not self.resolved_at:
            return None
        return round((self.resolved_at - self.created_at).total_seconds() / 3600, 1)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey("ticket.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    ticket = db.relationship("Ticket", back_populates="comments")
    author = db.relationship("User", back_populates="comments")


class TicketEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(40), nullable=False)
    detail = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey("ticket.id"), nullable=False)
    actor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    ticket = db.relationship("Ticket", back_populates="events")
    actor = db.relationship("User", back_populates="events")
