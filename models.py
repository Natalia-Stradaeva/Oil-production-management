from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# piantagione propria (per olio vergine esclusivo)
class Plantation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    size_hectares = db.Column(db.Float, default=10.0)    # 10 piantagione propria
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

# Tabella per la memorizzazione della storia del raccolto negli anni passati
class HarvestHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    amount_kg = db.Column(db.Float, nullable=False)  # Quanti chilogrammi di olive sono state raccolte
    profit_estimate = db.Column(db.Float)            # Stima della profit 

    def __repr__(self):
        return f'<Raccolto {self.year}: {self.amount_kg}kg>'    