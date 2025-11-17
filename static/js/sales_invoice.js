/**
 * Sales Invoice JavaScript
 * Handles tab navigation, cascading dropdowns, copy buyer to consignee, and calculations
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeSalesInvoice();
});

function initializeSalesInvoice() {
    // Initialize tab navigation
    initializeTabNavigation();

    // Initialize copy buyer to consignee button
    initializeCopyBuyer();

    // Initialize cascading dropdowns
    initializeCascadingDropdowns('buyer');
    initializeCascadingDropdowns('consignee');

    // Initialize commodity to tariff auto-fill
    initializeCommodityTariff();

    // Initialize tax calculations
    initializeTaxCalculations();

    // Initialize item calculations
    initializeItemCalculations();
}

/**
 * Tab Navigation
 */
function initializeTabNavigation() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabPanels = document.querySelectorAll('.tab-panel');

    tabButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const targetTab = this.getAttribute('data-tab');

            // Remove active from all buttons and panels
            tabButtons.forEach(btn => btn.classList.remove('active', 'bg-blue-600', 'text-white'));
            tabButtons.forEach(btn => btn.classList.add('bg-gray-200', 'text-gray-700'));
            tabPanels.forEach(panel => panel.classList.add('hidden'));

            // Add active to current button and panel
            this.classList.remove('bg-gray-200', 'text-gray-700');
            this.classList.add('active', 'bg-blue-600', 'text-white');
            document.getElementById(targetTab).classList.remove('hidden');
        });
    });

    // Handle next/previous buttons
    document.querySelectorAll('.btn-next-tab').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const nextTab = this.getAttribute('data-next-tab');
            if (nextTab) {
                const nextButton = document.querySelector(`[data-tab="${nextTab}"]`);
                if (nextButton) nextButton.click();
            }
        });
    });

    document.querySelectorAll('.btn-prev-tab').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const prevTab = this.getAttribute('data-prev-tab');
            if (prevTab) {
                const prevButton = document.querySelector(`[data-tab="${prevTab}"]`);
                if (prevButton) prevButton.click();
            }
        });
    });
}

/**
 * Copy Buyer to Consignee
 */
function initializeCopyBuyer() {
    const copyButton = document.getElementById('copy-buyer-btn');
    if (copyButton) {
        copyButton.addEventListener('click', function(e) {
            e.preventDefault();
            copyBuyerToConsignee();
        });
    }
}

function copyBuyerToConsignee() {
    // Map of buyer fields to consignee fields
    const fieldMappings = [
        { buyer: 'buyer_name', consignee: 'cong_name' },
        { buyer: 'buyer_add', consignee: 'cong_add' },
        { buyer: 'buyer_country', consignee: 'cong_country' },
        { buyer: 'buyer_state', consignee: 'cong_state' },
        { buyer: 'buyer_city', consignee: 'cong_city' },
        { buyer: 'buyer_cotper', consignee: 'cong_cotper' },
        { buyer: 'buyer_ph', consignee: 'cong_ph' },
        { buyer: 'buyer_mob', consignee: 'cong_mob' },
        { buyer: 'buyer_email', consignee: 'cong_email' },
        { buyer: 'buyer_tin', consignee: 'cong_tin' },
        { buyer: 'buyer_vat', consignee: 'cong_vat' },
        { buyer: 'buyer_fax', consignee: 'cong_fax' },
        { buyer: 'buyer_ecc', consignee: 'cong_ecc' }
    ];

    fieldMappings.forEach(mapping => {
        const buyerField = document.getElementById(`id_${mapping.buyer}`);
        const consigneeField = document.getElementById(`id_${mapping.consignee}`);

        if (buyerField && consigneeField) {
            consigneeField.value = buyerField.value;

            // Trigger change event for dropdowns
            if (buyerField.tagName === 'SELECT') {
                consigneeField.dispatchEvent(new Event('change'));
            }
        }
    });

    // Show success message
    showNotification('Buyer information copied to consignee successfully!', 'success');
}

/**
 * Cascading Dropdowns (Country -> State -> City)
 */
function initializeCascadingDropdowns(prefix) {
    const countrySelect = document.getElementById(`id_${prefix}_country`);
    const stateSelect = document.getElementById(`id_${prefix}_state`);
    const citySelect = document.getElementById(`id_${prefix}_city`);

    if (countrySelect && stateSelect) {
        countrySelect.addEventListener('change', function() {
            const countryId = this.value;
            if (countryId) {
                fetchStates(countryId, stateSelect, citySelect);
            } else {
                clearDropdown(stateSelect);
                clearDropdown(citySelect);
            }
        });
    }

    if (stateSelect && citySelect) {
        stateSelect.addEventListener('change', function() {
            const stateId = this.value;
            if (stateId) {
                fetchCities(stateId, citySelect);
            } else {
                clearDropdown(citySelect);
            }
        });
    }
}

function fetchStates(countryId, stateSelect, citySelect) {
    fetch(`/accounts/ajax/get-states-json/?country_id=${countryId}`)
        .then(response => response.json())
        .then(data => {
            populateDropdown(stateSelect, data.states, 'Select State');
            clearDropdown(citySelect);
        })
        .catch(error => {
            console.error('Error fetching states:', error);
            showNotification('Error loading states', 'error');
        });
}

function fetchCities(stateId, citySelect) {
    fetch(`/accounts/ajax/get-cities-json/?state_id=${stateId}`)
        .then(response => response.json())
        .then(data => {
            populateDropdown(citySelect, data.cities, 'Select City');
        })
        .catch(error => {
            console.error('Error fetching cities:', error);
            showNotification('Error loading cities', 'error');
        });
}

function populateDropdown(selectElement, options, defaultText) {
    selectElement.innerHTML = `<option value="">${defaultText}</option>`;
    options.forEach(option => {
        const optionElement = document.createElement('option');
        optionElement.value = option.id;
        optionElement.textContent = option.name;
        selectElement.appendChild(optionElement);
    });
    selectElement.disabled = false;
}

function clearDropdown(selectElement) {
    selectElement.innerHTML = '<option value="">---</option>';
    selectElement.disabled = true;
}

/**
 * Commodity to Tariff Auto-fill
 */
function initializeCommodityTariff() {
    const commoditySelect = document.getElementById('id_commodity');
    const tariffInput = document.getElementById('id_tariffheading');

    if (commoditySelect && tariffInput) {
        commoditySelect.addEventListener('change', function() {
            const commodityId = this.value;
            if (commodityId) {
                fetchTariffHeading(commodityId, tariffInput);
            } else {
                tariffInput.value = '';
            }
        });
    }
}

function fetchTariffHeading(commodityId, tariffInput) {
    fetch(`/accounts/transactions/sales-invoice/get-commodity-tariff/?commodity_id=${commodityId}`)
        .then(response => response.json())
        .then(data => {
            if (data.tariff) {
                tariffInput.value = data.tariff;
            }
        })
        .catch(error => {
            console.error('Error fetching tariff:', error);
        });
}

/**
 * Tax Calculations
 */
function initializeTaxCalculations() {
    const cenvatSelect = document.getElementById('id_cenvat');
    const vatSelect = document.getElementById('id_vat');

    if (cenvatSelect) {
        cenvatSelect.addEventListener('change', calculateTotals);
    }

    if (vatSelect) {
        vatSelect.addEventListener('change', calculateTotals);
    }

    // Add listeners for other amount fields
    const amountFields = ['otheramt', 'addamt', 'deduction', 'pf', 'sed', 'aed', 'freight', 'insurance'];
    amountFields.forEach(fieldName => {
        const field = document.getElementById(`id_${fieldName}`);
        if (field) {
            field.addEventListener('input', calculateTotals);
        }
    });
}

function calculateTotals() {
    const items = getInvoiceItems();
    if (items.length === 0) return;

    // Calculate subtotal
    let subtotal = 0;
    items.forEach(item => {
        subtotal += parseFloat(item.qty || 0) * parseFloat(item.rate || 0);
    });

    // Get tax rates
    const cenvatRate = extractRateFromSelect('id_cenvat');
    const vatRate = extractRateFromSelect('id_vat');

    // Calculate tax amounts
    const cenvatAmount = (subtotal * cenvatRate) / 100;
    const vatAmount = (subtotal * vatRate) / 100;

    // Get other amounts
    const otherAmt = parseFloat(document.getElementById('id_otheramt')?.value || 0);
    const addAmt = parseFloat(document.getElementById('id_addamt')?.value || 0);
    const deduction = parseFloat(document.getElementById('id_deduction')?.value || 0);
    const pf = parseFloat(document.getElementById('id_pf')?.value || 0);
    const sed = parseFloat(document.getElementById('id_sed')?.value || 0);
    const aed = parseFloat(document.getElementById('id_aed')?.value || 0);
    const freight = parseFloat(document.getElementById('id_freight')?.value || 0);
    const insurance = parseFloat(document.getElementById('id_insurance')?.value || 0);

    // Calculate grand total
    const grandTotal = subtotal + cenvatAmount + vatAmount + otherAmt + addAmt + pf + sed + aed + freight + insurance - deduction;

    // Display totals
    updateTotalsDisplay(subtotal, cenvatAmount, vatAmount, grandTotal);
}

function extractRateFromSelect(selectId) {
    const selectElement = document.getElementById(selectId);
    if (!selectElement || !selectElement.value) return 0;

    const selectedOption = selectElement.options[selectElement.selectedIndex];
    const text = selectedOption.text;

    // Extract number from text like "IGST@18%" or "SGST@ 9%"
    const match = text.match(/(\d+\.?\d*)/);
    return match ? parseFloat(match[1]) : 0;
}

function getInvoiceItems() {
    const items = [];
    const itemRows = document.querySelectorAll('.invoice-item-row');

    itemRows.forEach(row => {
        const checkbox = row.querySelector('input[type="checkbox"]');
        if (checkbox && checkbox.checked) {
            const qty = row.querySelector('.item-qty')?.value || 0;
            const rate = row.querySelector('.item-rate')?.value || 0;
            items.push({ qty, rate });
        }
    });

    return items;
}

function updateTotalsDisplay(subtotal, cenvatAmount, vatAmount, grandTotal) {
    const subtotalElement = document.getElementById('display-subtotal');
    const cenvatElement = document.getElementById('display-cenvat');
    const vatElement = document.getElementById('display-vat');
    const grandTotalElement = document.getElementById('display-grand-total');

    if (subtotalElement) subtotalElement.textContent = subtotal.toFixed(2);
    if (cenvatElement) cenvatElement.textContent = cenvatAmount.toFixed(2);
    if (vatElement) vatElement.textContent = vatAmount.toFixed(2);
    if (grandTotalElement) grandTotalElement.textContent = grandTotal.toFixed(2);
}

/**
 * Item Calculations and Validations
 */
function initializeItemCalculations() {
    const itemRows = document.querySelectorAll('.invoice-item-row');

    itemRows.forEach(row => {
        const qtyInput = row.querySelector('.item-req-qty');
        const percentageInput = row.querySelector('.item-percentage');

        if (qtyInput) {
            qtyInput.addEventListener('input', function() {
                validateItemQuantity(row);
                calculateItemTotal(row);
            });
        }

        if (percentageInput) {
            percentageInput.addEventListener('input', function() {
                validateItemPercentage(row);
            });
        }
    });
}

function validateItemQuantity(row) {
    const qtyInput = row.querySelector('.item-req-qty');
    const remainingQty = parseFloat(row.querySelector('.item-remaining-qty')?.textContent || 0);
    const requestedQty = parseFloat(qtyInput.value || 0);

    const errorElement = row.querySelector('.qty-error');

    if (requestedQty > remainingQty) {
        qtyInput.classList.add('border-red-500');
        if (errorElement) {
            errorElement.textContent = `Exceeds remaining quantity of ${remainingQty}`;
            errorElement.classList.remove('hidden');
        }
        return false;
    } else {
        qtyInput.classList.remove('border-red-500');
        if (errorElement) {
            errorElement.classList.add('hidden');
        }
        return true;
    }
}

function validateItemPercentage(row) {
    const percentageInput = row.querySelector('.item-percentage');
    const remainingPercentage = parseFloat(row.querySelector('.item-remaining-percentage')?.textContent || 100);
    const requestedPercentage = parseFloat(percentageInput.value || 0);

    const errorElement = row.querySelector('.percentage-error');

    if (requestedPercentage > remainingPercentage) {
        percentageInput.classList.add('border-red-500');
        if (errorElement) {
            errorElement.textContent = `Exceeds remaining ${remainingPercentage}%`;
            errorElement.classList.remove('hidden');
        }
        return false;
    } else {
        percentageInput.classList.remove('border-red-500');
        if (errorElement) {
            errorElement.classList.add('hidden');
        }
        return true;
    }
}

function calculateItemTotal(row) {
    const qtyInput = row.querySelector('.item-req-qty');
    const rateInput = row.querySelector('.item-rate');
    const totalElement = row.querySelector('.item-total');

    if (qtyInput && rateInput && totalElement) {
        const qty = parseFloat(qtyInput.value || 0);
        const rate = parseFloat(rateInput.value || 0);
        const total = qty * rate;

        totalElement.textContent = total.toFixed(2);
    }
}

/**
 * Customer Autocomplete and Auto-populate
 */
function initializeCustomerAutocomplete(prefix) {
    const customerNameInput = document.getElementById(`id_${prefix}_name`);
    const customerSearchButton = document.getElementById(`${prefix}-search-btn`);

    if (customerSearchButton) {
        customerSearchButton.addEventListener('click', function(e) {
            e.preventDefault();
            openCustomerSearchModal(prefix);
        });
    }

    if (customerNameInput) {
        // Add autocomplete functionality
        customerNameInput.addEventListener('input', debounce(function() {
            const query = this.value;
            if (query.length >= 2) {
                searchCustomers(query, prefix);
            }
        }, 300));
    }
}

function searchCustomers(query, prefix) {
    fetch(`/accounts/sales-invoice/customer-search/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            showCustomerSuggestions(data.customers, prefix);
        })
        .catch(error => {
            console.error('Error searching customers:', error);
        });
}

function showCustomerSuggestions(customers, prefix) {
    const suggestionsList = document.getElementById(`${prefix}-suggestions`);
    if (!suggestionsList) return;

    suggestionsList.innerHTML = '';

    customers.forEach(customer => {
        const li = document.createElement('li');
        li.className = 'px-4 py-2 hover:bg-gray-100 cursor-pointer';
        li.textContent = customer.name;
        li.addEventListener('click', function() {
            populateCustomerFields(customer, prefix);
            suggestionsList.innerHTML = '';
        });
        suggestionsList.appendChild(li);
    });

    suggestionsList.classList.remove('hidden');
}

function populateCustomerFields(customer, prefix) {
    // Populate all customer fields
    const fields = {
        'name': customer.name,
        'add': customer.address,
        'country': customer.country_id,
        'state': customer.state_id,
        'city': customer.city_id,
        'cotper': customer.contact_person,
        'ph': customer.phone,
        'mob': customer.mobile,
        'email': customer.email,
        'tin': customer.tin_cst,
        'vat': customer.tin_vat,
        'ecc': customer.ecc
    };

    Object.keys(fields).forEach(fieldName => {
        const element = document.getElementById(`id_${prefix}_${fieldName}`);
        if (element && fields[fieldName]) {
            element.value = fields[fieldName];

            // Trigger change for cascading dropdowns
            if (element.tagName === 'SELECT') {
                element.dispatchEvent(new Event('change'));
            }
        }
    });
}

/**
 * Utility Functions
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func.apply(this, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 px-6 py-3 rounded shadow-lg z-50 ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    notification.textContent = message;

    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Export functions for use in templates
window.salesInvoice = {
    copyBuyerToConsignee,
    calculateTotals,
    validateItemQuantity,
    validateItemPercentage,
    initializeCustomerAutocomplete
};
