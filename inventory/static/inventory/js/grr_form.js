// Set today's date as default for tax invoice date
document.addEventListener('DOMContentLoaded', function() {
    const taxInvoiceDateInput = document.getElementById('id_taxinvoicedate');
    
    // Set today's date if empty
    if (taxInvoiceDateInput && !taxInvoiceDateInput.value) {
        const today = new Date().toISOString().split('T')[0];
        taxInvoiceDateInput.value = today;
    }
});

