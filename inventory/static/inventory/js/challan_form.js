document.addEventListener('DOMContentLoaded', function() {
    const addFormRowBtn = document.getElementById('add-form-row');
    const formsetContainer = document.getElementById('formset-container');
    const totalForms = document.getElementById('id_form-TOTAL_FORMS');
    let formCount = parseInt(totalForms.value);

    addFormRowBtn.addEventListener('click', function() {
        const newForm = formsetContainer.children[0].cloneNode(true);
        const formRegex = new RegExp(`form-(\\d){1}-`, 'g');
        
        newForm.innerHTML = newForm.innerHTML.replace(formRegex, `form-${formCount}-`);
        formsetContainer.appendChild(newForm);
        
        totalForms.value = ++formCount;
    });

    formsetContainer.addEventListener('click', function(e) {
        if (e.target && e.target.classList.contains('remove-form-row')) {
            e.target.closest('.formset-row').remove();
            totalForms.value = --formCount;
        }
    });
});

