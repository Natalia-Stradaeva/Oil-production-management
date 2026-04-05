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
    extraction_capacity = db.Column(db.Float, default=250.0) # Capacità di estrazione in litri per giorno kg al ora

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    olives_own = db.Column(db.Float, default=0.0)   # proprie (per olio vergine)
    olives_bought = db.Column(db.Float, default=0.0) # acquistate (per olio extra)
    
    # Olio sfuso (in litri)
    oil_extra = db.Column(db.Float, default=0.0)
    oil_virgin = db.Column(db.Float, default=0.0)
    sansa = db.Column(db.Float, default=0.0) 

    # Materiali di imballaggio
    bottles = db.Column(db.Integer, default=0) # bottiglie da 1 litro
    corks = db.Column(db.Integer, default=0)   # Tappi di bottiglia
    empty_bags = db.Column(db.Integer, default=0) # sacchi vuoti da 10 kg per sansa
    

    # Prodotti finiti (bottiglie da 1 litro, sansa confezionata)
    bottled_extra = db.Column(db.Integer, default=0) # bottiglie di olio EVO imbottigliato
    bottled_virgin = db.Column(db.Integer, default=0) # bottiglie di olio Virgin imbottigliato
    sansa_bags = db.Column(db.Integer, default=0) # sansa confezionata in sacchi da 10 kg

    # Finanze
    money = db.Column(db.Float, default=1000.0)
    
    # Statistica
    last_production = db.Column(db.String(100), default="Nessuna")
    total_time = db.Column(db.Integer, default=0)

class ProductionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50))
    operation = db.Column(db.String(100)) # "Spremitura", "Filtrazione", "Imbottigliamento"
    oil_type = db.Column(db.String(50))
    quantity = db.Column(db.Float)
    time_spent = db.Column(db.Integer) #  Tempo in minuti
    temperature = db.Column(db.Float, default=25.0) # Temperatura durante la produzione
    waste_loss = db.Column(db.Float, default=0.0) # Perdita di olio durante la produzione (in litri)
    def __repr__(self):
        return f'<Log {self.date}: {self.operation} - {self.quantity}L>'    

# Tabella per la memorizzazione della storia del raccolto
class HarvestHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)     # Data della produzione
    olive_type = db.Column(db.String(50), nullable=False)  # Tipo di oliva (Premium, EVO)
    quantity = db.Column(db.Float, nullable=False)      # Quantità olive (kg)
    oil_produced = db.Column(db.Float, nullable=False)  # Olio prodotto (L)
    sansa_produced = db.Column(db.Float, default=0.0) # Sansa prodotta (kg)
    weather = db.Column(db.String(50), default="Soleggiato")
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