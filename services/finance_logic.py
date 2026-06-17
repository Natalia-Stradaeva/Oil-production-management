# services/finance_logic.py
from utils.validators import (
    COST_BUY_OLIVES, COST_PRODUCTION_BATCH, 
    COST_BOTTLE, COST_CORK, ESTIMATED_HARVEST_Q, DEFAULT_YIELD_LITERS, SANSA_KG_PER_BATCH,
    PRICE_SANSA, COST_BAG
)
def calculate_own_olive_cost(plantation):
    """
    Calcola il costo reale al quintale (100kg) delle olive proprie.
    Basato su: irrigazione + salari / raccolto stimato.
    """
    """ 
    Se non c'è ancora stato raccolto, prendiamo
    come riferimento una stima media di 1500 kg (15 quintali).

    
    Рассчитывает реальную стоимость 100кг (квинталя) собственных оливок.
    Использует константу ESTIMATED_HARVEST_Q из validators.py.
    """
    
    total_fixed_costs = plantation.irrigation_cost + plantation.workers_salary # 500 + 2000 = 2500€
    
    # Prezzo di costo di 100 kg delle olive proprie
    return round(total_fixed_costs / ESTIMATED_HARVEST_Q, 2) 

def estimate_unit_cost(oil_type, plantation, yield_liters=18):
    """
    Calcola il costo totale unitario (materia prima + produzione + packaging)
    Рассчитывает себестоимость 1 литра масла.
    Использует DEFAULT_YIELD_LITERS и SANSA_KG_PER_BATCH из validators.py.
    """
    # 1. COSTO DELLE MATERIE PRIME  СТОИМОСТЬ СЫРЬЯ
    if oil_type.lower() == "evo":
        raw_material_cost = COST_BUY_OLIVES # 105€ (prezzo di mercato)
    else:
        # Per la Virgin calcoliamo i costi di coltivazione (irrigazione + lavoratori)
        raw_material_cost = calculate_own_olive_cost(plantation) # ~166€
    
    # 2. TRASFORMAZIONE (Press) ПРОИЗВОДСТВО И УПАКОВКА
    processing_cost = COST_PRODUCTION_BATCH
    packaging_oil = (COST_BOTTLE + COST_CORK) * DEFAULT_YIELD_LITERS
    

    # 3. БОНУС ОТ ПРОДАЖИ ЖМЫХА (SANSA)
    sansa_revenue = SANSA_KG_PER_BATCH * PRICE_SANSA 
    sansa_packaging_cost = (SANSA_KG_PER_BATCH / 10) * COST_BAG 
    sansa_bonus = sansa_revenue - sansa_packaging_cost
    
    # 4. ИТОГОВЫЙ РАСЧЕТ
    # (Сырье + Производство + Упаковка) - Бонус от жмыха
    total_batch_cost = (raw_material_cost + processing_cost + packaging_oil) - sansa_bonus
    
    # Делим на средний выход масла из партии
    return round(total_batch_cost / DEFAULT_YIELD_LITERS, 2)