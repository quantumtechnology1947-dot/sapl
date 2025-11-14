// Auto-calculate tax and total amount
document.addEventListener('DOMContentLoaded', function() {
    const serviceAmountInput = document.getElementById('id_service_amount');
    const taxRateInput = document.getElementById('id_tax_rate');
    const taxAmountInput = document.getElementById('id_tax_amount');
    const totalAmountInput = document.getElementById('id_total_amount');
    
    function calculateAmounts() {
        const serviceAmount = parseFloat(serviceAmountInput.value) || 0;
        const taxRate = parseFloat(taxRateInput.value) || 0;
        
        const taxAmount = (serviceAmount * taxRate) / 100;
        const totalAmount = serviceAmount + taxAmount;
        
        taxAmountInput.value = taxAmount.toFixed(2);
        totalAmountInput.value = totalAmount.toFixed(2);
    }
    
    serviceAmountInput.addEventListener('input', calculateAmounts);
    taxRateInput.addEventListener('input', calculateAmounts);
    
    // Calculate on page load if values exist
    calculateAmounts();
});

