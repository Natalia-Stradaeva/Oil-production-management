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
PRODUCTION_CAPACITY = 200.0  # кг/час
BATCH_SIZE = 100.0  # kg per batch di produzione
PACKAGING_BATCH_SIZE = 50 # комплект для 50 бутылок (50 литров масла)
TIME_SPREMITURA = 120
TIME_FILTRAZIONE = 60
TIME_IMBOTTIGLIAMENTO_UNIT = 2 # 2 minuti per 1 bottiglia
COST_BAG = 0.50             # prezzo per sacco vuoto da 10 kg per sansa
BAGS_PER_PACKAGE = 500      # prezzo per confezione di 500 sacchi vuoti
MAX_TEMP_COLD_PRESS = 27.0  # limite di temperatura per la spremitura a freddo
WASTE_COEFFICIENT = 0.02    # perdite durante la produzione (2%)
SANSA_BAG_CAPACITY = 10     # 10 kg di sansa per sacco

ESTIMATED_HARVEST_Q = 15.0      # Средний урожай в квинталях
DEFAULT_YIELD_LITERS = 18.0     # Средний выход масла в литрах с партии
SANSA_KG_PER_BATCH = 80.0       # Средний выход жмыха в кг

# Базовые коэффициенты для планирования
OIL_YIELD_PREMIUM = 0.18  # Сколько литров масла с 1 кг оливок
OIL_YIELD_EVO = 0.15     # Сколько литров масла с 1 кг оливок для EVO

# Коэффициенты выхода жмыха (Sansa)
SANSA_YIELD_PREMIUM = 0.40
SANSA_YIELD_EVO = 0.45

TIME_COOLING = 30      # Мин. на охлаждение
TIME_FILTRATION = 60   # Мин. на фильтрацию

def can_afford(current_money, cost):
    """Controlla se ci sono abbastanza soldi per l'operazione"""
    return current_money >= cost

def has_resources(current_stock, required_amount):
    """Controlla se ci sono abbastanza risorse per l'operazione"""
    return current_stock >= required_amount