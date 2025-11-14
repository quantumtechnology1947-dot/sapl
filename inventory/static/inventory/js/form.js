let itemRowCount = 1;

function addItemRow() {
    const tbody = document.getElementById('items-tbody');
    const newRow = tbody.rows[0].cloneNode(true);
    
    // Update field names
    newRow.querySelectorAll('input, select').forEach(field => {
        const name = field.getAttribute('name');
        if (name) {
            field.setAttribute('name', name.replace('_0_', `_${itemRowCount}_`));
            if (field.type === 'checkbox') {
                field.checked = true;
            } else {
                field.value = '';
            }
        }
    });
    
    tbody.appendChild(newRow);
    itemRowCount++;
}

