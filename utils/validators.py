# Prezzi e limiti (costanti)
COST_BUY_OLIVES = 105.0
COST_PRODUCTION_BATCH = 16.5
PRICE_VIRGIN = 25.0
PRICE_EXTRA = 15.0
PRICE_SANSA = 0.20

def can_afford(current_money, cost):
    """Controlla se ci sono abbastanza soldi per l'operazione"""
    return current_money >= cost

def has_resources(current_stock, required_amount):
    """Controlla se ci sono abbastanza risorse per l'operazione"""
    return current_stock >= required_amount