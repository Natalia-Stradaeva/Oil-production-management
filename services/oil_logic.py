"""
Oleificio Simulation - Oil Logic Module

Modulo dedicato alla logica di trasformazione industriale delle olive:
gestione dei rendimenti produttivi, tempi di processo, condizioni climatiche
e operazioni di imbottigliamento/confezionamento.
"""

from utils.validators import (
    OIL_YIELD_PREMIUM, OIL_YIELD_EVO, 
    SANSA_YIELD_PREMIUM, SANSA_YIELD_EVO,
    WASTE_COEFFICIENT, MAX_TEMP_COLD_PRESS,
    TIME_COOLING, TIME_FILTRATION 
)

import random

# =============================================================================
# LOGICA AGRICOLA E RACCOLTA
# =============================================================================

def get_weather_impact():
    """
    Simula l'impatto delle condizioni meteorologiche sul raccolto annuale.
    UTILIZZA LA FUNZIONE RANDOM PER LA SELEZIONE CASUALE DEL METEO.
    
    Returns:
        dict: Dizionario contenente il tipo di meteo, il fattore di impatto 
              e un messaggio descrittivo per l'interfaccia utente.
    """
    weather_types = [
        {"type": "Soleggiato", "impact": 1.2, "msg": "Bel tempo! Il raccolto è superiore alla media."},
        {"type": "Variabile", "impact": 1.0, "msg": "Raccolto normale."},
        {"type": "Piovoso", "impact": 0.7, "msg": "Pioggia! Il raccolto è difficoltoso, la produzione è inferiore."},
        {"type": "Tempesta", "impact": 0.3, "msg": "Tempesta! Una grande parte delle olive è danneggiata."}
    ]
    return random.choice(weather_types)

def get_random_harvest(hectares):
    """
    Stima il raccolto totale basato sull'estensione dei terreni.
    UTILIZZA LA FUNZIONE RANDOM PER GENERARE LA RESA VARIABILE PER ETTARO.
    
    Args:
        hectares (float): Numero di ettari coltivati.
        
    Returns:
        float: Peso totale stimato del raccolto in kg.
    """
    yield_per_hectare = random.uniform(3000, 6000)
    total_harvest = hectares * yield_per_hectare
    return round(total_harvest, 2)

# =============================================================================
# LOGICA DI TRASFORMAZIONE (FRANTOIO)
# =============================================================================

def calculate_bottling(liters, bottles_available, corks_available):
    """
    Determina quante bottiglie da 1 litro possono essere prodotte.
    
    Returns:
        tuple: (Numero di bottiglie prodotte, litri di olio rimanenti).
    """
    max_by_oil = int(liters)
    
    # Il vincolo è dato dalla risorsa scarsa (olio, bottiglie o tappi)
    can_bottle = min(max_by_oil, bottles_available, corks_available)
    
    # Residui oleosi dopo l'imbottigliamento
    remaining_oil = round(liters - can_bottle, 2)
    
    return can_bottle, remaining_oil


def calculate_yield(olive_type: str, quantity: float, capacity_per_hour: float) -> dict:
    """
    Calcola la resa industriale in olio e sansa, includendo tempi e temperatura.
    
    Args:
        olive_type (str): "premium" (olive proprie) o "evo" (acquistate).
        quantity (float): Quantità di olive in ingresso (kg).
        capacity_per_hour (float): Capacità del macchinario (kg/h).
        
    Returns:
        dict: Risultati della produzione (olio, sansa, tempi, temp. e scarti).
    """
    
    # Selezione dei coefficienti di resa basati sulla qualità
    if olive_type == "premium":
        oil_yield_factor = OIL_YIELD_PREMIUM # Oliva da plantazione propria ha resa leggermente superiore
        sansa_yield_factor =SANSA_YIELD_PREMIUM
    else:
        oil_yield_factor = OIL_YIELD_EVO # Oliva da olio EVO ha resa leggermente inferiore
        sansa_yield_factor = SANSA_YIELD_EVO

    # Calcolo quantità grezze    
    raw_oil = quantity * oil_yield_factor
    sansa = quantity * sansa_yield_factor
    
    # Calcolo scarti produttivi 
    waste = raw_oil * WASTE_COEFFICIENT
    final_oil = round(raw_oil - waste, 2)
    
    # Calcolo del tempo basato sulla potenza (Capacity = Weight / Time)
    # Tempo base in minuti = (Quantità / Capacità) * 60
    base_time = int((quantity / capacity_per_hour) * 60)
    
    # Simulazione Temperatura e Surriscaldamento
    # Se temp > 27°C, aggiungiamo tempo di raffreddamento
    current_temp = round(random.uniform(22.0, 30.0), 1)
    cooling_time = TIME_COOLING if current_temp > MAX_TEMP_COLD_PRESS else 0
        
    total_time = base_time + cooling_time + TIME_FILTRATION
    
    return {
        "oil": final_oil,
        "sansa": round(sansa, 2),
        "time": total_time,
        "temp": current_temp,
        "waste": round(waste, 2)
    }

def calculate_sansa_packaging(sansa_kg: float, bags_available: int) -> tuple:
    """
    Determina il numero di sacchi da 10kg ottenibili dalla sansa disponibile.
    
    Returns:
        tuple: (Numero di sacchi prodotti, sansa residua in kg).
    """
    max_bags = int(sansa_kg // 10)
    actual_bags = min(max_bags, bags_available)
    remaining_sansa = round(sansa_kg - (actual_bags * 10), 2)
    return actual_bags, remaining_sansa
