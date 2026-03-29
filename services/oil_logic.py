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


def calculate_yield(olive_type, quantity):
    """
    calcolare l'uscita dell'olio e sansa basata sul tipo di olive.
    Premium (proprie) danno un po' più e qualità migliore.
    """
    if olive_type == "premium":
        # olive proprie: uscita 16-19% + meno sansa
        oil_yield = quantity * 0.18  # 18 litri su 100 kg
        sansa_yield = quantity * 0.40 # 40 kg di sansa
    else:
        # olive acquistate (EVO): uscita 13-16%
        oil_yield = quantity * 0.15  # 15 litri su 100 kg
        sansa_yield = quantity * 0.45 # 45 kg di sansa
    
    return round(oil_yield, 2), round(sansa_yield, 2)