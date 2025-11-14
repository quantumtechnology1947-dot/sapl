// Set today's date as default for gate entry date
document.addEventListener('DOMContentLoaded', function() {
    const gdateInput = document.getElementById('id_gdate');
    const gtimeInput = document.getElementById('id_gtime');
    
    // Set today's date if empty
    if (gdateInput && !gdateInput.value) {
        const today = new Date().toISOString().split('T')[0];
        gdateInput.value = today;
    }
    
    // Set current time if empty
    if (gtimeInput && !gtimeInput.value) {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        gtimeInput.value = `${hours}:${minutes}`;
    }
});

