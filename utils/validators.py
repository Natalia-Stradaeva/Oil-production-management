# Prezzi e limiti (costanti)
COST_BUY_OLIVES = 105.0
COST_PRODUCTION_BATCH = 16.5
PRICE_VIRGIN = 25.0
PRICE_EVO = 15.0
PRICE_SANSA = 0.20
COST_BOTTLE = 0.80  # Costo per bottiglia da 1 litro
COST_CORK = 0.20    # Costo per tappo di bottiglia
PRICE_VIRGIN_BOTTLED = 30.0 
PRICE_EVO_BOTTLED = 20.0
# Tempo di elaborazione (in minuti)
TIME_SPREMITURA = 120
TIME_FILTRAZIONE = 60
TIME_IMBOTTIGLIAMENTO_UNIT = 2 # 2 minuti per 1 bottiglia

def can_afford(current_money, cost):
    """Controlla se ci sono abbastanza soldi per l'operazione"""
    return current_money >= cost

def has_resources(current_stock, required_amount):
    """Controlla se ci sono abbastanza risorse per l'operazione"""
    return current_stock >= required_amount