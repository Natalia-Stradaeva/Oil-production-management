"""
Oleificio Simulation - Configuration & Validation Module

Modulo dedicato alla definizione delle costanti di sistema (finanziarie, produttive 
e tecniche) e alla gestione delle funzioni di validazione per le operazioni di magazzino.

Tutti i parametri sono configurabili per adattarsi ai diversi scenari produttivi
previsti dal progetto.
"""

# =============================================================================
# PARAMETRI ECONOMICI: Prezzi e Costi
# =============================================================================
COST_BUY_OLIVES = 105.0 # Costo di acquisto per un lotto di olive (mercato)
COST_PRODUCTION_BATCH = 16.5 # Costo operativo per ciclo di produzione (frangitura)
COST_BOTTLE = 0.80  # Costo unitario per bottiglia da 1 litro
COST_CORK = 0.20    # Costo unitario per tappo
COST_BAG = 0.50     # Costo unitario per sacco vuoto da 10 kg per sansa

MARKUP_BOTTLED_OIL = 1.2  # Coefficiente di ricarico per olio imbottigliato (+20%)
GOVERNMENT_SUBSIDY = 5000.0  # Sussidio statale una tantum per il supporto alla produzione

PRICE_VIRGIN = 25.0 # Prezzo vendita al litro (olio Vergine sfuso)
PRICE_EVO = 15.0 # Prezzo vendita al litro (olio EVO sfuso)
PRICE_SANSA = 0.20 # Prezzo di vendita per kg di sansa
PRICE_VIRGIN_BOTTLED = 30.0 # Prezzo di vendita per bottiglia (Vergine)
PRICE_EVO_BOTTLED = 20.0 # Prezzo di vendita per bottiglia (EVO)

# =============================================================================
# PARAMETRI PRODUTTIVI E TECNICI: Capacità e Rese
# =============================================================================
PRODUCTION_CAPACITY = 200.0  # Capacità massima di frangitura (kg/ora)
BATCH_SIZE = 100.0  # Dimensione standard del lotto di produzione (kg)
PACKAGING_BATCH_SIZE = 50 # Numero di bottiglie prodotte per kit imballaggio
BAGS_PER_PACKAGE = 500   # Quantità di sacchi in una confezione standard
SANSA_BAG_CAPACITY = 10   # Capacità in kg per un singolo sacco di sansa

# Coefficienti di resa e scarto
WASTE_COEFFICIENT = 0.02    # Coefficiente di perdita fisiologica durante la produzione (2%)
ESTIMATED_HARVEST_Q = 15.0  # Raccolto stimato per ettaro (in quintali)
DEFAULT_YIELD_LITERS = 18.0  # Resa media olio (litri per lotto)
SANSA_KG_PER_BATCH = 80.0  # Produzione media di sansa per lotto (kg)

OIL_YIELD_PREMIUM = 0.18  # Resa olio per kg di olive (Vergine)
OIL_YIELD_EVO = 0.15  # Resa olio per kg di olive (EVO)
SANSA_YIELD_PREMIUM = 0.40 # Coefficiente di conversione sansa (Vergine)
SANSA_YIELD_EVO = 0.45 # Coefficiente di conversione sansa (EVO)

# =============================================================================
# PARAMETRI TEMPORALI: Tempistiche di processo (in minuti)
# =============================================================================
TIME_SPREMITURA = 120 # Tempo necessario per la spremitura
TIME_IMBOTTIGLIAMENTO_UNIT = 2 # Tempo necessario per imbottigliare 1 unità
TIME_COOLING = 30  # Tempo di raffreddamento dell'olio
TIME_FILTRATION = 60 # Tempo supplementare per il processo di filtrazione

# =============================================================================
# VINCOLI OPERATIVI
# =============================================================================
MAX_TEMP_COLD_PRESS = 27.0  # Temperatura massima per la spremitura a freddo


# =============================================================================
# LOGICHE DI VALIDAZIONE
# =============================================================================
def can_afford(current_money, cost):
    """Controlla se ci sono abbastanza soldi per l'operazione"""
    return current_money >= cost

def has_resources(current_stock, required_amount):
    """Controlla se ci sono abbastanza risorse per l'operazione"""
    return current_stock >= required_amount