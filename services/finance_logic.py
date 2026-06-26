"""
Oleificio Simulation - Finance Logic Module

Modulo dedicato ai calcoli di bilancio, analisi dei costi di produzione 
e stima della redditività operativa.
"""
from utils.validators import (
    COST_BUY_OLIVES, COST_PRODUCTION_BATCH, 
    COST_BOTTLE, COST_CORK, ESTIMATED_HARVEST_Q, DEFAULT_YIELD_LITERS, SANSA_KG_PER_BATCH,
    PRICE_SANSA, COST_BAG
)

# =============================================================================
# CALCOLO COSTI DI PRODUZIONE AGRICOLA
# =============================================================================

def calculate_own_olive_cost(plantation):
    """
    Calcola il costo di produzione al quintale (100kg) per le olive proprie.
    
    Il calcolo si basa sui costi fissi (irrigazione e salari) spalmati 
    sulla produzione annua stimata.

    Args:
        plantation (Plantation): Oggetto contenente i costi fissi operativi.

    Returns:
        float: Costo unitario calcolato per 100kg di olive.
    """
    # Somma dei costi operativi fissi per la gestione del terreno
    total_fixed_costs = plantation.irrigation_cost + plantation.workers_salary 
    
   # Calcolo costo per quintale (es: 2500€ / 15q = 166.67€)
    return round(total_fixed_costs / ESTIMATED_HARVEST_Q, 2) 

# =============================================================================
# ANALISI DI RENTABILITÀ E COSTI UNITARI
# =============================================================================

def estimate_unit_cost(oil_type, plantation, yield_liters=18):
    """
    Calcola il costo totale unitario per litro di olio prodotto.
    
    La logica integra:
    1. Costo della materia prima (differenziato tra olive proprie e acquistate).
    2. Costi di trasformazione industriale e packaging.
    3. Detrazione del bonus derivante dalla vendita del sottoprodotto (sansa).

    Args:
        oil_type (str): Tipologia di olio ("evo" o "virgin").
        plantation (Plantation): Dati relativi alla gestione del terreno.
        yield_liters (int): Resa media in litri per lotto.

    Returns:
        float: Costo netto finale per litro di prodotto finito.
    """
    # 1. COSTO DELLE MATERIE PRIME 
    if oil_type.lower() == "evo":
        # Per l'EVO usiamo il prezzo di acquisto di mercato
        raw_material_cost = COST_BUY_OLIVES 
    else:
        # Per la Virgin calcoliamo i costi di coltivazione (irrigazione + lavoratori)
        raw_material_cost = calculate_own_olive_cost(plantation) 
    
    # 2. COSTI DI TRASFORMAZIONE E IMBOTTIGLIAMENTO
    processing_cost = COST_PRODUCTION_BATCH
    packaging_oil = (COST_BOTTLE + COST_CORK) * DEFAULT_YIELD_LITERS
    

    # 3. VALUTAZIONE ECONOMICA DEL SOTTOPRODOTTO (SANSA)
    # Calcolo ricavo lordo dalla sansa meno costi di insacchettamento
    sansa_revenue = SANSA_KG_PER_BATCH * PRICE_SANSA 
    sansa_packaging_cost = (SANSA_KG_PER_BATCH / 10) * COST_BAG 
    sansa_bonus = sansa_revenue - sansa_packaging_cost
    
    # 4. CALCOLO FINALE (Netto)
    # (Costi totali di filiera) - (Bonus recuperato dallo scarto)
    total_batch_cost = (raw_material_cost + processing_cost + packaging_oil) - sansa_bonus
    
    # Ritorna il costo unitario per litro
    return round(total_batch_cost / DEFAULT_YIELD_LITERS, 2)