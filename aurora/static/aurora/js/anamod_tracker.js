// ======================================================================
// FILE: aurora/static/aurora/js/anamod_tracker.js (PATCH 1 OF 1)
// START: STANDALONE_IDE_BUFFER_DELEGATION_TRACKER
// ======================================================================
$(document).ready(function() {
    console.log("[Anamod Tracker] Activating high-performance DOM buffer delegation engine...");

    // Hoist a globally accessible hook so Monaco can notify the tracker of exact text mutations
    window.triggerAnamodDirtyState = function() {
        const $indicator = $('#active-file-indicator');
        const titleText = $indicator.text().trim();

        // Only mark dirty if a file is loaded and not already marked modified
        if (titleText && titleText !== "No file active" && !titleText.endsWith('*')) {
            $indicator.text(titleText + ' *').addClass('text-warning');
            
            // Enable and highlight Save button
            $('#anamod-save-btn').prop('disabled', false)
                .removeClass('btn-outline-warning')
                .addClass('btn-warning text-dark font-weight-bold');
                
            // Enable and highlight Discard button
            $('#anamod-discard-btn').prop('disabled', false)
                .removeClass('btn-outline-danger')
                .addClass('btn-danger text-dark font-weight-bold');
        }
    };

    // 2. Clear dirty state marks only when primary AJAX transactions succeed via global events
    $(document).on('buffer:saved buffer:discarded', function() {
        const $indicator = $('#active-file-indicator');
        const titleText = $indicator.text().replace(' *', '').trim();
        
        $indicator.text(titleText).removeClass('text-warning');

        // Cool down Save button to disabled outline state
        $('#anamod-save-btn').prop('disabled', true)
            .removeClass('btn-warning text-dark font-weight-bold')
            .addClass('btn-outline-warning');

        // Cool down Discard button to disabled outline state
        $('#anamod-discard-btn').prop('disabled', true)
            .removeClass('btn-danger text-dark font-weight-bold')
            .addClass('btn-outline-danger');
    });
});
// ======================================================================
// END: STANDALONE_IDE_BUFFER_DELEGATION_TRACKER (PATCH 1 OF 1)
// ======================================================================
