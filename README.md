# Oil-production-management

# Oil-production-management
*Simulazione avanzata della gestione operativa e logistica di un oleificio (Settore Primario).*

**Autore:** Natalia Stradaeva  
**Università:** Università Telematica Pegaso  
**Corso di Laurea:** Informatica per le aziende digitali (L-31)  
**Project Work:** Tema n. 1 - La digitalizzazione dell’impresa (PW 15)

## Descrizione:

Questo progetto è un software per simulare il ciclo di vita di un oleificio. Gestisce tutto il processo: dalle olive in campo alla produzione, fino al confezionamento e alla vendita finale. L'obiettivo è analizzare l'efficienza economica e ottimizzare i costi aziendali.

## Caratteristiche principali e architettura:

### Architettura
Tecnologie usate: Il progetto è creato con Python e il framework Flask. Per il database viene utilizzato SQLAlchemy, mentre per aggiornare i grafici in tempo reale senza ricaricare la pagina viene implementato AJAX e Chart.js.

### Logica del progetto:
L'interfaccia serve solo per vedere come funziona il sistema. Il vero lavoro (il "cuore" del programma) è nel back-end, dove vengono calcolate le produzioni e gestiti i dati in modo preciso.

### Parte economica: 
Tutti i prezzi, i costi e il budget iniziale (5000 €) sono salvati in un file di configurazione separato (validators.py). In questo modo è facile cambiare i valori senza dover toccare il codice principale.

## Funzionalità principali

### Simulazione agricola:
Vengono utilizzate funzioni statistiche (random.uniform e random.choice) per simulare il raccolto delle olive. Ogni stagione è diversa: a novembre parte la raccolta e il sistema calcola automaticamente i costi per il lavoro e l'irrigazione.

### Controllo qualità:
Durante la frangitura, il sistema controlla la temperatura. Se supera i 27°C, viene aggiunto automaticamente un tempo di raffreddamento. Questo cambia l'efficienza della produzione.È prevista l'integrazione futura di sensori IoT per il monitoraggio dei dati in tempo reale.

### Produzione e imballaggi:
Il sistema lavora con tre prodotti: Olio Virgin (da olive di produzione propria), Olio EVO (da olive comprate) e la Sansa. Viene gestito l'imbottigliamento (bottiglie da 1L) e il confezionamento della sansa (sacchi da 10kg), aggiornando il magazzino in automatico.

### Magazzino e Logistica: 
Gestione semplice e diretta delle scorte: il sistema tiene traccia di tutto ciò che entra e esce. È possibile gestire sia la vendita di olio (sfuso o imbottigliato) che l'acquisto di materiali per l'imballaggio (bottiglie, tappi, sacchi). Ogni operazione aggiorna automaticamente le quantità disponibili nel magazzino e i risultati vengono visualizzati in una Dashboard pratica.

### Analisi e reportistica:
La Dashboard include 5 grafici (distribuzione prodotti, temperature, ricavi, efficienza, magazzino) e una tabella con le ultime 20 vendite. È disponibile una funzione per esportare l'intera pagina in PDF. È prevista in futuro l'implementazione di tasti di esportazione separati per singoli grafici e tabelle, per rendere l'analisi industriale più pratica e mirata.

### Ambiente:
La sansa non viene buttata, ma venduta come fertilizzante o per cosmetici. Questo riduce gli sprechi e aiuta l'ambiente (economia circolare).

## Struttura del progetto:

```
Oil-production-management
├── app.py              # Punto di ingresso, inizializzazione del server
├── models.py           # Schema del database (SQLAlchemy)
├── requirements.txt    # Elenco delle dipendenze del progetto
├── services/           # Logica di business e calcoli principali
│   ├── finance_logic.py # Calcoli finanziari, sussidi e margini
│   └── oil_logic.py     # Logica di produzione, temperatura e resa
├── static/             # Risorse statiche
│   ├── css/style.css   # Fogli di stile per l'interfaccia
│   ├── images/         # Immagini, logo e snapshot PDF della dashboard
│   └── js/main.js      # Script client-side e chiamate AJAX
├── templates/          # Template HTML (interfaccia utente)
└── utils/              # Funzioni di supporto e validatori
```


## Istruzioni per l'avvio
1. Assicurarsi di avere installato Python 3.x.
2. Clonare il repository: 
   `git clone https://github.com/Natalia-Stradaeva/Oil-production-management`
3. Installare le dipendenze: 
   `pip install -r requirements.txt`
4. Avviare l'applicazione: 
   `python app.py`
5. Aprire il browser all'indirizzo: 
   `http://127.0.0.1:5000`

## Visualizzazione e Media
Nella cartella images sono presenti:

Generazione di immagini: 
L'immagine promozionale è stata generata con l'ausilio di intelligenza artificiale (Nanabanana) per scopi illustrativi.

Anteprima della simulazione (PDF):
 È disponibile il file dashboard_full_view.pdf che fornisce una panoramica completa dell'interfaccia e dei dati, ideale per un'analisi rapida senza esecuzione del codice.   

### Sicurezza e Accesso
IIl sistema implementa un modello di autenticazione basato su Flask-Login per gestire le sessioni utente.

*   **Versione Demo:** Per i test delle funzionalità, è possibile accedere con le credenziali di amministratore:
    *   **Username:** `admin`
    *   **Password:** `123`
*   **Scalabilità:** L'attuale architettura è predisposta per l'integrazione di sistemi di autenticazione professionale (es. implementazione di hashing delle password tramite librerie crittografiche come BCrypt).

---
**Natalia Stradaeva** | *Informatica per le Aziende Digitali (L-31)* | *Università Telematica Pegaso*  