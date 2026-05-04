from datetime import datetime
from core.database import db


class Goal(db.Model):

    __tablename__ = "goals"

    id = db.Column(db.Integer, primary_key=True)
    calories_goal = db.Column(db.Integer, nullable=False)
    water_goal_ml = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, default=datetime.utcnow)
    end_date = db.Column(db.Date, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
