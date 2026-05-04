# create_tables.py
from app import app
from core.database import db
import os

os.environ["DB_USER"] = "diet_user"
os.environ["DB_PASSWORD"] = "sua_senha"
os.environ["DB_HOST"] = "127.0.0.1"
os.environ["DB_PORT"] = "3306"
os.environ["DB_NAME"] = "daily_diet"

# Importa todos os models para que o SQLAlchemy saiba das tabelas
from meals.models import Meal
from goals.models import Goal
from water.models import WaterIntake

with app.app_context():
    db.create_all()
    print("✅ Todas as tabelas foram criadas com sucesso!")
