(function () {
    'use strict';

    var FIELD_SELECTOR = 'input, select, textarea';
    var IGNORED_INPUT_TYPES = new Set([
        'hidden', 'button', 'submit', 'reset', 'image', 'file', 'checkbox', 'radio', 'search', 'color'
    ]);

    function isVisibleAndEditable(field) {
        if (!field || field.disabled || field.readOnly || field.getAttribute('aria-hidden') === 'true') return false;
        if (field.matches('[data-fast-entry="off"], [contenteditable="true"]')) return false;
        if (field.closest('[hidden], [inert], .select2-container, .select2-search')) return false;
        if (field.tagName === 'INPUT' && IGNORED_INPUT_TYPES.has((field.type || 'text').toLowerCase())) return false;
        if (field.tagName === 'BUTTON') return false;
        return field.getClientRects().length > 0;
    }

    function getScope(field) {
        var row = field.closest('tr');
        if (row && row.querySelector(FIELD_SELECTOR)) return row;
        return field.closest('form, [data-fast-entry-scope]');
    }

    function getFields(scope) {
        return Array.from(scope.querySelectorAll(FIELD_SELECTOR)).filter(isVisibleAndEditable);
    }

    function submitForm(form) {
        if (!form || typeof form.requestSubmit !== 'function') return;
        form.requestSubmit();
    }

    document.addEventListener('keydown', function (event) {
        var field = event.target;
        if (!(field instanceof Element) || !field.matches(FIELD_SELECTOR) || !isVisibleAndEditable(field)) return;
        if (event.isComposing) return;

        var scope = getScope(field);
        if (!scope) return;

        if (event.key === 'Enter') {
            if (event.altKey || event.metaKey) return;
            if (event.ctrlKey) {
                var form = field.closest('form') || (scope.matches('form') ? scope : null);
                if (!form) return;
                event.preventDefault();
                submitForm(form);
                return;
            }

            // Keep native multiline editing, Select2/datalist selection, and ordinary select behavior.
            if (field.tagName === 'TEXTAREA' || field.tagName === 'SELECT' || field.hasAttribute('list')) return;
            if (field.closest('[role="combobox"], .select2-container')) return;

            var enterFields = getFields(scope);
            var enterIndex = enterFields.indexOf(field);
            if (enterIndex < 0) return;
            var nextIndex = enterIndex + (event.shiftKey ? -1 : 1);

            if (nextIndex >= 0 && nextIndex < enterFields.length) {
                event.preventDefault();
                enterFields[nextIndex].focus();
            } else if (event.shiftKey) {
                event.preventDefault();
                enterFields[0].focus();
            }
            // At the end of a form, preserve the browser's normal Enter-to-submit behavior.
            return;
        }

        // F2 shortcuts provide direct field navigation without overriding text/select editing keys.
        if (event.key !== 'F2' || event.altKey || event.metaKey) return;
        if (field.tagName === 'TEXTAREA' || field.tagName === 'SELECT' || field.hasAttribute('list')) return;
        if (field.closest('[role="combobox"], .select2-container')) return;

        var fields = getFields(scope);
        var index = fields.indexOf(field);
        if (index < 0 || fields.length < 2) return;

        var targetIndex;
        if (event.ctrlKey) {
            targetIndex = event.shiftKey ? fields.length - 1 : 0;
        } else {
            targetIndex = index + (event.shiftKey ? -1 : 1);
        }
        if (targetIndex < 0 || targetIndex >= fields.length || targetIndex === index) return;

        event.preventDefault();
        fields[targetIndex].focus();
    });
})();
