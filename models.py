from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False) # parole 
    role = db.Column(db.String(20), default='operator')  # 'admin', 'engineer', 'operator'

# piantagione propria (per olio vergine esclusivo)
class Plantation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    size_hectares = db.Column(db.Float, default=10.0)    # 10 piantagione propria
    current_month = db.Column(db.Integer, default=1) # 1-12 per rappresentare i mesi
    irrigation_cost = db.Column(db.Float, default=500.0) # Costo dell'irrigazione per stagione
    workers_salary = db.Column(db.Float, default=2000.0) # Costo del salario dei lavoratori in novembre
    harvest_amount = db.Column(db.Float, default=0.0)    # Quantità di olive raccolte (in novembre)


class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    olives_own = db.Column(db.Float, default=0.0)   # proprie (per olio vergine)
    olives_bought = db.Column(db.Float, default=0.0) # acquistate (per olio extra)
    
    # olio prodotto
    oil_extra = db.Column(db.Float, default=0.0)
    oil_virgin = db.Column(db.Float, default=0.0)
    sansa = db.Column(db.Float, default=0.0)
    
    # Finanze
    money = db.Column(db.Float, default=1000.0)
    
    # Statistica
    last_production = db.Column(db.String(100), default="Nessuna")
    total_time = db.Column(db.Integer, default=0)

# Tabella per la memorizzazione della storia del raccolto
class HarvestHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)     # Data della produzione
    olive_type = db.Column(db.String(50), nullable=False)  # Tipo di oliva (Premium, EVO)
    quantity = db.Column(db.Float, nullable=False)      # Quantità olive (kg)
    oil_produced = db.Column(db.Float, nullable=False)  # Olio prodotto (L)
    sansa_produced = db.Column(db.Float, default=0.0) # Sansa prodotta (kg)
    def __repr__(self):
        return f'<Evento {self.date}: {self.olive_type} - {self.oil_produced}L>'   
     
# Tabella per la memorizzazione della storia delle vendite
class SalesHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    product_type = db.Column(db.String(50), nullable=False) # Virgin, EVO, Sansa
    quantity = db.Column(db.Float, nullable=False)
    price_unit = db.Column(db.Float, nullable=False)
    total_revenue = db.Column(db.Float, nullable=False)   