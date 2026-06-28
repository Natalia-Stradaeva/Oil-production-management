"""
Oleificio Simulation - Database Models Module

Definizione dello schema del database tramite SQLAlchemy.
Modulo responsabile della persistenza dei dati relativi all'autenticazione, 
alla gestione delle risorse aziendali (piantagioni, magazzino), al controllo 
dei flussi finanziari e alla tracciabilità storica dei processi produttivi e delle vendite.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# =============================================================================
# MODULO UTENTI: Autenticazione e Profilazione
# =============================================================================
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False) 
    role = db.Column(db.String(20), default='operator') # Ruoli: 'admin', 'engineer', 'operator'

# =============================================================================
# MODULO RISORSE E PRODUZIONE
# =============================================================================
class Plantation(db.Model):
    """Gestione dei parametri colturali e operativi del terreno di proprietà."""
    id = db.Column(db.Integer, primary_key=True)
    size_hectares = db.Column(db.Float, default=10.0)  # Estensione in ettari (10 piantagione propria)
    current_month = db.Column(db.Integer, default=1) # Mese corrente (1-12)
    irrigation_cost = db.Column(db.Float, default=500.0) # Costo dell'irrigazione per stagione
    workers_salary = db.Column(db.Float, default=2000.0) # Costo del salario dei lavoratori in novembre
    harvest_amount = db.Column(db.Float, default=0.0)    # Quantità di olive raccolte (in novembre)
    extraction_capacity = db.Column(db.Float, default=250.0) # Capacità di estrazione in litri per giorno kg al ora

class Stock(db.Model):
    """Gestione inventario: stato attuale delle scorte, materie prime, prodotti e liquidità."""
    id = db.Column(db.Integer, primary_key=True)

    # Materie prime (Olive)
    olives_own = db.Column(db.Float, default=0.0)   # Scorta olive proprie (per olio Vergine)
    olives_bought = db.Column(db.Float, default=0.0) # Scorta olive acquistate (per olio EVO)
    
    # Prodotti intermedi e vendita diretta (Olio sfuso e Sansa)
    oil_extra = db.Column(db.Float, default=0.0) # Olio EVO sfuso (litri)
    oil_virgin = db.Column(db.Float, default=0.0) # Olio Vergine (proprio) sfuso (litri)
    sansa = db.Column(db.Float, default=0.0) # Sansa grezza (kg)

    # Materiali di imballaggio
    bottles = db.Column(db.Integer, default=0) # Bottiglie vuote (1L)
    corks = db.Column(db.Integer, default=0)   # Tappi di bottiglia
    empty_bags = db.Column(db.Integer, default=0) # Sacchi vuoti da 10 kg per sansa
    

    # Prodotti finiti (bottiglie da 1 litro, sansa confezionata)
    bottled_extra = db.Column(db.Integer, default=0) # Bottiglie EVO
    bottled_virgin = db.Column(db.Integer, default=0) # Bottiglie Vergine
    sansa_bags = db.Column(db.Integer, default=0) # Sacchi sansa confezionata

    # Stato finanziario e metriche
    money = db.Column(db.Float, default=1000.0) # Saldo di cassa
    last_production = db.Column(db.String(100), default="Nessuna")
    total_time = db.Column(db.Integer, default=0) # Tempo operativo totale (minuti)

 # =============================================================================
# MODULO STORICO E LOG: Tracciabilità delle operazioni
# =============================================================================   
class ProductionLog(db.Model):
    """Registro dettagliato di ogni operazione di trasformazione effettuata."""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50))
    operation = db.Column(db.String(100)) # "Spremitura", "Filtrazione", "Imbottigliamento"
    oil_type = db.Column(db.String(50))
    quantity = db.Column(db.Float) # Quantità lavorata
    time_spent = db.Column(db.Integer) # Tempo impiegato (minuti)
    temperature = db.Column(db.Float, default=25.0) # Temperatura durante la produzione
    waste_loss = db.Column(db.Float, default=0.0) # Perdita di olio durante la produzione (in litri)

    def __repr__(self):
        return f'<Log {self.date}: {self.operation} - {self.quantity}L>'    

class HarvestHistory(db.Model):
    """Tabella per la memorizzazione della storia del raccolto."""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)     # Data della produzione
    olive_type = db.Column(db.String(50), nullable=False)  # Tipo di oliva (Virgin, EVO)
    quantity = db.Column(db.Float, nullable=False)      # Quantità olive (kg)
    oil_produced = db.Column(db.Float, nullable=False)  # Olio prodotto (L)
    sansa_produced = db.Column(db.Float, default=0.0) # Sansa prodotta (kg)
    weather = db.Column(db.String(50), default="Soleggiato")

    def __repr__(self):
        return f'<Evento {self.date}: {self.olive_type} - {self.oil_produced}L>'   
     
class SalesHistory(db.Model):
    """Tabella per la memorizzazione della storia delle vendite."""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    product_type = db.Column(db.String(50), nullable=False) # Virgin, EVO, Sansa
    quantity = db.Column(db.Float, nullable=False)
    price_unit = db.Column(db.Float, nullable=False)
    total_revenue = db.Column(db.Float, nullable=False)   