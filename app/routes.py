from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_
from . import db
from .models import User, Ticket, Comment

bp = Blueprint("main", __name__)


def staff_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_staff:
            abort(403)
        return view(*args, **kwargs)
    return wrapped


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
    base = Ticket.query if current_user.is_staff else Ticket.query.filter_by(created_by_id=current_user.id)
    stats = {
        "total": base.count(),
        "nuevo": base.filter_by(status="Nuevo").count(),
        "proceso": base.filter_by(status="En proceso").count(),
        "resuelto": base.filter_by(status="Resuelto").count(),
        "alta": base.filter_by(priority="Alta").count(),
    }
    recent = base.order_by(Ticket.updated_at.desc()).limit(6).all()
    return render_template("dashboard.html", stats=stats, recent=recent)


@bp.route("/tickets")
@login_required
def tickets():
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    priority = request.args.get("priority", "").strip()
    query = Ticket.query if current_user.is_staff else Ticket.query.filter_by(created_by_id=current_user.id)
    if q:
        query = query.filter(or_(Ticket.title.ilike(f"%{q}%"), Ticket.description.ilike(f"%{q}%")))
    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=priority)
    items = query.order_by(Ticket.updated_at.desc()).all()
    return render_template("tickets.html", tickets=items)


@bp.route("/tickets/new", methods=["GET", "POST"])
@login_required
def new_ticket():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        if not title or not description:
            flash("Título y descripción son obligatorios.", "danger")
            return render_template("ticket_form.html")
        ticket = Ticket(
            title=title,
            description=description,
            category=request.form.get("category", "Software"),
            priority=request.form.get("priority", "Media"),
            created_by_id=current_user.id,
        )
        db.session.add(ticket)
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
            db.session.commit()
            flash("Comentario agregado.", "success")
            return redirect(url_for("main.ticket_detail", ticket_id=ticket.id))

    technicians = User.query.filter(User.role.in_(["technician", "admin"])).order_by(User.name).all()
    return render_template("ticket_detail.html", ticket=ticket, technicians=technicians)


@bp.route("/tickets/<int:ticket_id>/manage", methods=["POST"])
@staff_required
def manage_ticket(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)
    ticket.status = request.form.get("status", ticket.status)
    ticket.priority = request.form.get("priority", ticket.priority)
    assigned = request.form.get("assigned_to_id", "")
    ticket.assigned_to_id = int(assigned) if assigned.isdigit() else None
    db.session.commit()
    flash("Ticket actualizado.", "success")
    return redirect(url_for("main.ticket_detail", ticket_id=ticket.id))


@bp.route("/admin/users")
@staff_required
def users():
    return render_template("users.html", users=User.query.order_by(User.name).all())
