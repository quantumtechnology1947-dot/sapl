/**
 * SysAdmin Module - Cascading Dropdowns with HTMX
 * Cortex ERP
 * Created: 2025-10-11
 *
 * Handles dynamic dropdown population for:
 * - Country → State → City hierarchy
 * - Form validation
 * - Date range validation for Financial Years
 */

// =============================================================================
// CASCADING DROPDOWN UTILITIES
// =============================================================================

/**
 * Populate states dropdown based on selected country
 * Uses HTMX for AJAX loading
 */
function populateStates(countryId, targetElementId = 'id_state') {
    if (!countryId) {
        // Reset state dropdown
        const stateSelect = document.getElementById(targetElementId);
        if (stateSelect) {
            stateSelect.innerHTML = '<option value="">-- Select Country First --</option>';
            stateSelect.disabled = true;
        }
        return;
    }

    // HTMX will handle the actual loading via hx-get attribute
    // This function is here for manual invocation if needed
    const stateSelect = document.getElementById(targetElementId);
    if (stateSelect) {
        stateSelect.disabled = false;
    }
}

/**
 * Populate cities dropdown based on selected state
 * Uses HTMX for AJAX loading
 */
function populateCities(stateId, targetElementId = 'id_city') {
    if (!stateId) {
        // Reset city dropdown
        const citySelect = document.getElementById(targetElementId);
        if (citySelect) {
            citySelect.innerHTML = '<option value="">-- Select State First --</option>';
            citySelect.disabled = true;
        }
        return;
    }

    // HTMX will handle the actual loading via hx-get attribute
    const citySelect = document.getElementById(targetElementId);
    if (citySelect) {
        citySelect.disabled = false;
    }
}

// =============================================================================
// FORM VALIDATION
// =============================================================================

/**
 * Validate required fields in a form
 */
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;

    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    let firstInvalidField = null;

    requiredFields.forEach(field => {
        if (!field.value || field.value.trim() === '') {
            isValid = false;
            field.classList.add('is-invalid');

            if (!firstInvalidField) {
                firstInvalidField = field;
            }
        } else {
            field.classList.remove('is-invalid');
        }
    });

    if (!isValid && firstInvalidField) {
        firstInvalidField.focus();
        showValidationMessage('Please fill in all required fields');
    }

    return isValid;
}

/**
 * Show validation message
 */
function showValidationMessage(message, type = 'danger') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            <i class="bi bi-exclamation-triangle-fill"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    // Find or create messages container
    let messagesContainer = document.querySelector('.messages-container');
    if (!messagesContainer) {
        messagesContainer = document.createElement('div');
        messagesContainer.className = 'messages-container';
        const contentDiv = document.querySelector('.container-fluid.mt-4');
        if (contentDiv) {
            contentDiv.insertBefore(messagesContainer, contentDiv.firstChild);
        }
    }

    messagesContainer.insertAdjacentHTML('beforeend', alertHtml);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = messagesContainer.querySelector('.alert:last-child');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

// =============================================================================
// DATE VALIDATION FOR FINANCIAL YEARS
// =============================================================================

/**
 * Validate date range (from date must be before to date)
 */
function validateDateRange(fromDateId, toDateId) {
    const fromDate = document.getElementById(fromDateId);
    const toDate = document.getElementById(toDateId);

    if (!fromDate || !toDate || !fromDate.value || !toDate.value) {
        return true; // Skip validation if dates not filled
    }

    const from = new Date(fromDate.value);
    const to = new Date(toDate.value);

    if (from >= to) {
        toDate.classList.add('is-invalid');
        showValidationMessage('From date must be before To date', 'warning');
        return false;
    }

    toDate.classList.remove('is-invalid');
    return true;
}

/**
 * Auto-populate financial year name from date range
 */
function autoPopulateFYName(fromDateId, toDateId, fyNameId) {
    const fromDate = document.getElementById(fromDateId);
    const toDate = document.getElementById(toDateId);
    const fyName = document.getElementById(fyNameId);

    if (!fromDate || !toDate || !fyName) return;

    const updateFYName = () => {
        if (fromDate.value && toDate.value && !fyName.value) {
            const fromYear = new Date(fromDate.value).getFullYear();
            const toYear = new Date(toDate.value).getFullYear();
            fyName.value = `${fromYear}-${toYear}`;
        }
    };

    fromDate.addEventListener('change', updateFYName);
    toDate.addEventListener('change', updateFYName);
}

// =============================================================================
// HTMX EVENT HANDLERS
// =============================================================================

/**
 * Setup HTMX event listeners
 */
document.addEventListener('DOMContentLoaded', function() {
    // Show loading indicator on HTMX requests
    document.body.addEventListener('htmx:beforeRequest', function(event) {
        const indicator = event.target.getAttribute('hx-indicator');
        if (indicator) {
            const indicatorEl = document.querySelector(indicator);
            if (indicatorEl) {
                indicatorEl.classList.remove('d-none');
            }
        }
    });

    // Hide loading indicator after HTMX request completes
    document.body.addEventListener('htmx:afterRequest', function(event) {
        const indicator = event.target.getAttribute('hx-indicator');
        if (indicator) {
            const indicatorEl = document.querySelector(indicator);
            if (indicatorEl) {
                indicatorEl.classList.add('d-none');
            }
        }
    });

    // Handle HTMX errors
    document.body.addEventListener('htmx:responseError', function(event) {
        console.error('HTMX Error:', event.detail);
        showValidationMessage('An error occurred while loading data. Please try again.', 'danger');
    });

    // Handle successful HTMX swaps
    document.body.addEventListener('htmx:afterSwap', function(event) {
        // Re-initialize any JavaScript components in the swapped content
        initializeComponents(event.target);
    });
});

// =============================================================================
// DELETE CONFIRMATION WITH HTMX
// =============================================================================

/**
 * Enhanced delete confirmation with HTMX
 */
document.addEventListener('htmx:confirm', function(event) {
    const confirmMsg = event.target.getAttribute('hx-confirm');
    if (confirmMsg) {
        event.preventDefault();

        if (confirm(confirmMsg)) {
            event.detail.issueRequest(true);
        }
    }
});

// =============================================================================
// COMPONENT INITIALIZATION
// =============================================================================

/**
 * Initialize JavaScript components after dynamic content load
 */
function initializeComponents(container = document) {
    // Re-initialize Bootstrap tooltips
    const tooltipTriggerList = container.querySelectorAll('[data-bs-toggle="tooltip"]');
    [...tooltipTriggerList].map(el => new bootstrap.Tooltip(el));

    // Re-initialize Bootstrap popovers
    const popoverTriggerList = container.querySelectorAll('[data-bs-toggle="popover"]');
    [...popoverTriggerList].map(el => new bootstrap.Popover(el));
}

// =============================================================================
// SEARCH DEBOUNCING
// =============================================================================

/**
 * Debounce function for search inputs
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// =============================================================================
// TABLE ROW CLICK HANDLER
// =============================================================================

/**
 * Make table rows clickable (excluding action buttons)
 */
function initializeTableRowClicks() {
    document.querySelectorAll('.table-hover tbody tr').forEach(row => {
        row.addEventListener('click', function(e) {
            // Don't navigate if clicking on buttons or links
            if (e.target.closest('button, a')) {
                return;
            }

            // Find the view/edit link in the row
            const viewLink = row.querySelector('a[href*="update"], a[href*="detail"]');
            if (viewLink) {
                window.location.href = viewLink.href;
            }
        });
    });
}

// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initializeComponents();
    initializeTableRowClicks();

    // Setup financial year form if present
    const fyForm = document.getElementById('fy-form');
    if (fyForm) {
        autoPopulateFYName('id_finyearfrom', 'id_finyearto', 'id_finyear');
    }

    // Add real-time validation for date fields
    const fromDateFields = document.querySelectorAll('input[type="date"][name*="from"]');
    const toDateFields = document.querySelectorAll('input[type="date"][name*="to"]');

    fromDateFields.forEach((fromField, index) => {
        const toField = toDateFields[index];
        if (toField) {
            fromField.addEventListener('change', () => {
                if (fromField.value && toField.value) {
                    validateDateRange(fromField.id, toField.id);
                }
            });
            toField.addEventListener('change', () => {
                if (fromField.value && toField.value) {
                    validateDateRange(fromField.id, toField.id);
                }
            });
        }
    });
});

// =============================================================================
// EXPORT FUNCTIONS FOR GLOBAL USE
// =============================================================================

window.SysAdmin = {
    populateStates,
    populateCities,
    validateForm,
    validateDateRange,
    showValidationMessage,
    autoPopulateFYName
};

console.log('SysAdmin cascading dropdowns initialized successfully');
