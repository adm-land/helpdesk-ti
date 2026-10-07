from app import create_app
from app.demo_data import seed_demo_data

app = create_app()

with app.app_context():
    created = seed_demo_data(reset=False)
    if created:
        print("Datos de demostración cargados.")
    else:
        print("La base de datos ya tiene información.")
