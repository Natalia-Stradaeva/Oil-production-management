// Funzione per mostrare un avviso se la temperatura è alta
function checkTemperature(temp) {
    if (temp > 27.0) {
        console.warn("Attenzione: Temperatura elevata (" + temp + "°C). Sistema in raffreddamento.");
        
    }
}

// Esempio: conferma prima di vendere tutto
document.querySelectorAll('.btn-red').forEach(button => {
    button.addEventListener('click', function(e) {
        const confirmAction = confirm("Sei sicuro di voler vendere l'intero stock?");
        if (!confirmAction) {
            e.preventDefault();
        }
    });
});

window.addEventListener('load', function() {
    const savedScroll = localStorage.getItem('scrollPosition');
    if (savedScroll) {
        window.scrollTo(0, parseInt(savedScroll));
        localStorage.removeItem('scrollPosition');
    }
});

window.addEventListener('beforeunload', function() {
    localStorage.setItem('scrollPosition', window.scrollY);
});

document.addEventListener('submit', function() {
    
    const activeBtn = document.activeElement;
    if (activeBtn && activeBtn.tagName === 'BUTTON') {
        activeBtn.style.opacity = '0.5';
        activeBtn.innerText = 'Elaborazione...';
    }
});


setTimeout(() => {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(a => a.style.display = 'none');
}, 3000);