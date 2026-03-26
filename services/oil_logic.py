import random

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