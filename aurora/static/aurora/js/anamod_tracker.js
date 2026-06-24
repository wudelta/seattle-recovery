// ======================================================================
// FILE: aurora/static/aurora/js/anamod_tracker.js (PATCH 1 OF 1)
// START: STANDALONE_IDE_BUFFER_DELEGATION_TRACKER
// ======================================================================
$(document).ready(function() {
    console.log("[Anamod Tracker] Activating high-performance DOM buffer delegation engine...");

    // 1. Listen for keydown events inside Monaco's workspace viewport text fields via global delegation
    $(document).on('keydown', '#anamod-monaco-viewport .monaco-editor textarea', function() {
        const $indicator = $('#active-file-indicator');
        const titleText = $indicator.text().trim();
        
        if (titleText && !titleText.endsWith('*')) {
            $indicator.text(titleText + ' *').addClass('text-warning');
            $('#anamod-save-btn').removeClass('btn-outline-warning').addClass('btn-warning text-dark font-weight-bold');
        }
    });

    // 2. Intercept save action button transaction completions to clear the dirty token state
    $(document).on('click', '#anamod-save-btn', function() {
        const $btn = $(this);
        // Delay execution slightly to allow the primary core script's AJAX transaction loop to finish commits to disk
        setTimeout(function() {
            const $indicator = $('#active-file-indicator');
            const titleText = $indicator.text().replace(' *', '').trim();
            $indicator.text(titleText).removeClass('text-warning');
            $btn.removeClass('btn-warning text-dark font-weight-bold').addClass('btn-outline-warning');
        }, 400);
    });
});
// ======================================================================
// END: STANDALONE_IDE_BUFFER_DELEGATION_TRACKER (PATCH 1 OF 1)
// ======================================================================
