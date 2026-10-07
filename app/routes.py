import csv
import io
from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, Response, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_
from . import db
from .models import User, Ticket, Comment, TicketEvent

bp = Blueprint("main", __name__)

VALID_STATUS = {"Nuevo", "En proceso", "Resuelto"}
VALID_PRIORITY = {"Baja", "Media", "Alta"}
VALID_CATEGORY = {"Software", "Hardware", "Red", "Acceso", "Otro"}


def staff_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_staff:
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if current_user.role != "admin":
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def visible_tickets():
    if current_user.is_staff:
        return Ticket.query
    return Ticket.query.filter_by(created_by_id=current_user.id)


def filtered_tickets(query):
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    priority = request.args.get("priority", "").strip()
    if q:
        query = query.filter(or_(Ticket.title.ilike(f"%{q}%"), Ticket.description.ilike(f"%{q}%")))
    if status in VALID_STATUS:
        query = query.filter_by(status=status)
    if priority in VALID_PRIORITY:
        query = query.filter_by(priority=priority)
    return query


@bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("index.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("main.dashboard"))
        flash("Correo o contraseña incorrectos.", "danger")
    return render_template("login.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@bp.route("/dashboard")
@login_required
def dashboard():
    query = visible_tickets()
    items = query.all()
    resolved_times = [t.resolution_hours for t in items if t.resolution_hours is not None]
    resolved_count = sum(1 for t in items if t.status == "Resuelto")
    stats = {
        "total": len(items),
        "nuevo": sum(1 for t in items if t.status == "Nuevo"),
        "proceso": sum(1 for t in items if t.status == "En proceso"),
        "resuelto": resolved_count,
        "alta": sum(1 for t in items if t.priority == "Alta"),
        "vencidos": sum(1 for t in items if t.is_overdue),
        "tasa_resolucion": round((resolved_count / len(items)) * 100) if items else 0,
        "promedio_resolucion": round(sum(resolved_times) / len(resolved_times), 1) if resolved_times else 0,
    }
    recent = query.order_by(Ticket.updated_at.desc()).limit(6).all()
    return render_template("dashboard.html", stats=stats, recent=recent)


@bp.route("/tickets")
@login_required
def tickets():
    items = filtered_tickets(visible_tickets()).order_by(Ticket.updated_at.desc()).all()
    return render_template("tickets.html", tickets=items)


@bp.route("/tickets/new", methods=["GET", "POST"])
@login_required
def new_ticket():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "Software")
        priority = request.form.get("priority", "Media")
        if not title or not description:
            flash("Título y descripción son obligatorios.", "danger")
            return render_template("ticket_form.html")
        if category not in VALID_CATEGORY or priority not in VALID_PRIORITY:
            flash("Revisa la categoría y prioridad seleccionadas.", "danger")
            return render_template("ticket_form.html")
        ticket = Ticket(
            title=title,
            description=description,
            category=category,
            priority=priority,
            created_by_id=current_user.id,
        )
        ticket.set_sla_deadline()
        db.session.add(ticket)
        db.session.flush()
        db.session.add(TicketEvent(event_type="Creación", detail="Ticket registrado", ticket=ticket, actor=current_user))
        db.session.commit()
        flash("Ticket creado correctamente.", "success")
        return redirect(url_for("main.ticket_detail", ticket_id=ticket.id))
    return render_template("ticket_form.html")


@bp.route("/tickets/<int:ticket_id>", methods=["GET", "POST"])
@login_required
def ticket_detail(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)
    if not current_user.is_staff and ticket.created_by_id != current_user.id:
        abort(403)

    if request.method == "POST":
        body = request.form.get("comment", "").strip()
        if body:
            db.session.add(Comment(body=body, ticket=ticket, author=current_user))
            ticket.updated_at = datetime.utcnow()
            db.session.commit()
            flash("Comentario agregado.", "success")
            return redirect(url_for("main.ticket_detail", ticket_id=ticket.id))

    technicians = User.query.filter(User.role.in_(["technician", "admin"])).order_by(User.name).all()
    return render_template("ticket_detail.html", ticket=ticket, technicians=technicians)


@bp.route("/tickets/<int:ticket_id>/manage", methods=["POST"])
@staff_required
def manage_ticket(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)
    new_status = request.form.get("status", ticket.status)
    new_priority = request.form.get("priority", ticket.priority)
    assigned = request.form.get("assigned_to_id", "")

    if new_status not in VALID_STATUS or new_priority not in VALID_PRIORITY:
        abort(400)

    new_assigned_id = int(assigned) if assigned.isdigit() else None
    if new_assigned_id:
        technician = db.session.get(User, new_assigned_id)
        if not technician or not technician.is_staff:
            abort(400)

    changes = []
    if ticket.status != new_status:
        changes.append(f"Estado: {ticket.status} → {new_status}")
        if new_status == "Resuelto":
            ticket.resolved_at = datetime.utcnow()
        elif ticket.status == "Resuelto":
            ticket.resolved_at = None

    if ticket.priority != new_priority:
        changes.append(f"Prioridad: {ticket.priority} → {new_priority}")
        ticket.priority = new_priority
        if new_status != "Resuelto":
            ticket.set_sla_deadline(datetime.utcnow())

    old_technician = ticket.technician.name if ticket.technician else "Sin asignar"
    if ticket.assigned_to_id != new_assigned_id:
        new_technician = db.session.get(User, new_assigned_id).name if new_assigned_id else "Sin asignar"
        changes.append(f"Responsable: {old_technician} → {new_technician}")

    ticket.status = new_status
    ticket.priority = new_priority
    ticket.assigned_to_id = new_assigned_id
    ticket.updated_at = datetime.utcnow()

    if changes:
        db.session.add(TicketEvent(event_type="Actualización", detail=" · ".join(changes), ticket=ticket, actor=current_user))

    db.session.commit()
    flash("Ticket actualizado.", "success")
    return redirect(url_for("main.ticket_detail", ticket_id=ticket.id))


@bp.route("/tickets/export.csv")
@login_required
def export_tickets():
    items = filtered_tickets(visible_tickets()).order_by(Ticket.id).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Asunto", "Categoría", "Prioridad", "Estado", "Responsable", "Creado", "Límite SLA", "Resuelto"])
    for ticket in items:
        writer.writerow([
            ticket.id,
            ticket.title,
            ticket.category,
            ticket.priority,
            ticket.status,
            ticket.technician.name if ticket.technician else "Sin asignar",
            ticket.created_at.strftime("%Y-%m-%d %H:%M"),
            ticket.sla_due_at.strftime("%Y-%m-%d %H:%M") if ticket.sla_due_at else "",
            ticket.resolved_at.strftime("%Y-%m-%d %H:%M") if ticket.resolved_at else "",
        ])
    return Response(
        output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=tickets_helpdesk.csv"},
    )


@bp.route("/api/tickets")
@login_required
def api_tickets():
    items = filtered_tickets(visible_tickets()).order_by(Ticket.updated_at.desc()).all()
    return jsonify([
        {
            "id": t.id,
            "title": t.title,
            "category": t.category,
            "priority": t.priority,
            "status": t.status,
            "assigned_to": t.technician.name if t.technician else None,
            "created_at": t.created_at.isoformat(),
            "sla_due_at": t.sla_due_at.isoformat() if t.sla_due_at else None,
            "overdue": t.is_overdue,
            "resolved_at": t.resolved_at.isoformat() if t.resolved_at else None,
        }
        for t in items
    ])


@bp.route("/admin/users")
@admin_required
def users():
    return render_template("users.html", users=User.query.order_by(User.name).all())
