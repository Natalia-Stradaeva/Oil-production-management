from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
# Definizione della tabella per il magazzino 
class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    olives = db.Column(db.Float, default=500.0)
    oil_extra = db.Column(db.Float, default=0.0)
    oil_virgin = db.Column(db.Float, default=0.0)
    sansa = db.Column(db.Float, default=0.0)
    money = db.Column(db.Float, default=1000.0)
    last_production = db.Column(db.String(100), default="Nessuna")
    total_time = db.Column(db.Integer, default=0)
