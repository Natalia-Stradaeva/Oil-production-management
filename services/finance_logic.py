# services/finance_logic.py
from utils.validators import (
    COST_BUY_OLIVES, COST_PRODUCTION_BATCH, 
    COST_BOTTLE, COST_CORK, 
    PRICE_VIRGIN_BOTTLED, PRICE_EVO_BOTTLED,
    PRICE_SANSA, COST_BAG,
)

def calculate_own_olive_cost(plantation):
    """
    Calcola il costo reale al quintale (100kg) delle olive proprie.
    Basato su: irrigazione + salari / raccolto stimato.
    """
    """ 
    Se non c'è ancora stato raccolto, prendiamo
    come riferimento una stima media di 1500 kg (15 quintali).
    """
    estimated_harvest_q = 15.0 
    
    total_fixed_costs = plantation.irrigation_cost + plantation.workers_salary # 500 + 2000 = 2500€
    
    # Prezzo di costo di 100 kg delle olive proprie
    return round(total_fixed_costs / estimated_harvest_q, 2) 

def estimate_unit_cost(oil_type, plantation, yield_liters=18):
    """
    Calcola il costo totale unitario (materia prima + produzione + packaging)
    """
    # 1. COSTO DELLE MATERIE PRIME
    if oil_type.lower() == "evo":
        raw_material_cost = COST_BUY_OLIVES # 105€ (prezzo di mercato)
    else:
        # Per la Virgin calcoliamo i costi di coltivazione (irrigazione + lavoratori)
        raw_material_cost = calculate_own_olive_cost(plantation) # ~166€
    
    # 2. TRASFORMAZIONE (Press)
    processing_cost = COST_PRODUCTION_BATCH # 16.5€
    
    # 3. IMBALLAGGIO (Bottiglia + Tappo)
    packaging_total = (COST_BOTTLE + COST_CORK) * yield_liters # 1.0€ * litri
    

    # Ricavo dalla vendita della sansa: 80 kg * 0,20 € = 16 €
    sansa_revenue = sansa_kg * PRICE_SANSA 
    # Costi di imballaggio della sansa: 8 sacchi * 0.50€ = 4€
    sansa_packaging_cost = (sansa_kg / 10) * COST_BAG 
    # Bonus netto dalla sansa, che riduce il costo totale della partita
    sansa_bonus = sansa_revenue - sansa_packaging_cost # 16€ - 4€ = 12€ di profitto
    
    # Costo totale di un lotto di OLIO (meno il profitto derivante dalla sansa)
    total_batch_cost = (raw_material_cost + processing_cost + packaging_oil) - sansa_bonus
    
    if yield_liters <= 0: return 0.0
    return round(total_batch_cost / yield_liters, 2)