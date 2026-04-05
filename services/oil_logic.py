import random

def get_weather_impact():
    """Condizioni meteorologiche imprevedibili per la raccolta delle olive"""
    weather_types = [
        {"type": "Soleggiato", "impact": 1.2, "msg": "Bel tempo! Il raccolto è superiore alla media."},
        {"type": "Variabile", "impact": 1.0, "msg": "Raccolto normale."},
        {"type": "Piovoso", "impact": 0.7, "msg": "Pioggia! Il raccolto è difficoltoso, la produzione è inferiore."},
        {"type": "Tempesta", "impact": 0.3, "msg": "Tempesta! Una grande parte delle olive è danneggiata."}
    ]
    return random.choice(weather_types)

def calculate_bottling(liters, bottles_available, corks_available):
    """
    Imbottigliamento dell'olio in bottiglie da 1 litro.
    1 litro di olio + 1 bottiglia + 1 tappo di sughero = 1 prodotto finito.
    """
    # Prendiamo un numero intero di litri
    max_by_oil = int(liters)
    
    # Troviamo il limite basato sul risorsa più limitata
    can_bottle = min(max_by_oil, bottles_available, corks_available)
    
    # Residui oleosi dopo l'imbottigliamento
    remaining_oil = round(liters - can_bottle, 2)
    
    return can_bottle, remaining_oil

def get_random_harvest(hectares):
    """
    Calcola il raccolto annuale basato sugli ettari.
    Resa media: 3000-6000 kg per ettaro.
    """
    yield_per_hectare = random.uniform(3000, 6000)
    total_harvest = hectares * yield_per_hectare
    return round(total_harvest, 2)


def calculate_yield(olive_type: str, quantity: float, capacity_per_hour: float) -> dict:
    """
    Calcola la resa dell'olio e della sansa con parametri accademici.
    
    :param olive_type: Tipo di oliva ("premium" o "evo")
    :param quantity: Quantità di olive in kg
    :param capacity_per_hour: Capacità del frantoio (kg/h)
    :return: Dizionario con risultati della produzione
    """
    
    # Calcolo base della resa 
    if olive_type == "premium":
        oil_yield_factor = 0.18 # Oliva da plantazione propria ha resa leggermente superiore
        sansa_yield_factor = 0.40
    else:
        oil_yield_factor = 0.15 # Oliva da olio EVO ha resa leggermente inferiore
        sansa_yield_factor = 0.45
        
    raw_oil = quantity * oil_yield_factor
    sansa = quantity * sansa_yield_factor
    
    # Perdite di produzione (Scrap 2%) 
    waste = raw_oil * 0.02
    final_oil = round(raw_oil - waste, 2)
    
    # Calcolo del tempo basato sulla potenza (Capacity = Weight / Time)
    # Tempo base in minuti = (Quantità / Capacità) * 60
    base_time = int((quantity / capacity_per_hour) * 60)
    
    # Simulazione Temperatura e Surriscaldamento
    # Se temp > 27°C, aggiungiamo tempo di raffreddamento
    current_temp = round(random.uniform(22.0, 30.0), 1)
    cooling_time = 0
    if current_temp > 27.0:
        cooling_time = 30 # 30 minuti di pausa per raffreddare
        
    total_time = base_time + cooling_time + 60 # +60 min per filtrazione fissa
    
    return {
        "oil": final_oil,
        "sansa": round(sansa, 2),
        "time": total_time,
        "temp": current_temp,
        "waste": round(waste, 2)
    }

def calculate_sansa_packaging(sansa_kg: float, bags_available: int) -> tuple:
    """
    Calcola il confezionamento della sansa in sacchi da 10kg.
    """
    max_bags = int(sansa_kg // 10)
    actual_bags = min(max_bags, bags_available)
    remaining_sansa = round(sansa_kg - (actual_bags * 10), 2)
    return actual_bags, remaining_sansa