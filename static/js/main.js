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


document.addEventListener('submit', function() {
    
    const activeBtn = document.activeElement;
    if (activeBtn && activeBtn.tagName === 'BUTTON') {
        activeBtn.style.opacity = '0.5';
        activeBtn.innerText = 'Elaborazione...';
    }
});

// Скрытие уведомлений через 3 секунды
setTimeout(() => {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(a => a.style.display = 'none');
}, 3000);

// --- ЭТОТ БЛОК ОТВЕЧАЕТ ЗА СОХРАНЕНИЕ ПОЗИЦИИ ПРОКРУТКИ ---
window.addEventListener('beforeunload', function() {
    localStorage.setItem('scrollPosition', window.scrollY);
});

window.addEventListener('load', function() {
    const savedScroll = localStorage.getItem('scrollPosition');
    if (savedScroll) {
        window.scrollTo({
            top: parseInt(savedScroll),
            behavior: 'instant' 
        });
        localStorage.removeItem('scrollPosition');
    }
});