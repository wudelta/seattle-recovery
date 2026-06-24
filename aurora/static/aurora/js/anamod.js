// ======================================================================
// FILE: aurora/static/aurora/js/anamod.js (PATCH 1 OF 3)
// START: ANAMOD_CORE_BASE_AND_LOADER
// ======================================================================
(function(window) {
    window.editorInstance = null;
    let currentFilePath = null;

    window.initAnamodConsole = function(csrfToken) {
        console.log("[Anamod Workspace] Spawning control channels...");

        window.updateAnamodTerminal = function(message) {
            const $term = $('#anamod-terminal-stream');
            if ($term.length) {
                $term.append(message);
                $term.scrollTop($term.scrollHeight);
            }
        };

        window.MonacoEnvironment = {
            getWorkerUrl: function(workerId, label) {
                if (label === 'json') return '/static/js/vs/language/json/jsonWorker.js';
                if (label === 'css') return '/static/js/vs/language/css/cssWorker.js';
                if (label === 'html') return '/static/js/vs/language/html/htmlWorker.js';
                if (label === 'typescript' || label === 'javascript') return '/static/js/vs/language/typescript/tsWorker.js';
                return '/static/js/vs/base/worker/workerMain.js';
            }
        };

        function mountEditorInstance() {
            const targetDom = document.getElementById('anamod-monaco-viewport');
            if (!targetDom) return;
            if (typeof monaco !== 'undefined' && monaco.editor) {
                buildMonacoInstance(targetDom);
                return;
            }
            if (typeof require !== 'undefined' && typeof require.config === 'function') {
                require.config({ baseUrl: '/static/js' });
                require(['vs/editor/editor.main'], function() {
                    buildMonacoInstance(targetDom);
                });
            } else {
                window.updateAnamodTerminal(`[ERROR] Monaco vs/loader.js missing.\n`);
            }
        }

        function buildMonacoInstance(targetDom) {
            if (window.editorInstance !== null) return;
            try {
                window.editorInstance = monaco.editor.create(targetDom, {
                    value: "# Select a modular file from the directory tree to start coding...\n",
                    language: 'python',
                    theme: 'vs-dark',
                    automaticLayout: true,
                    fontSize: 13,
                    fontFamily: 'Fira Code, Courier New, monospace',
                    minimap: { enabled: false },
                    readOnly: false
                });

                // Bind Monaco's native content mutation loopback directly to the tracker hook
                window.editorInstance.onDidChangeModelContent(function() {
                    if (typeof window.triggerAnamodDirtyState === 'function') {
                        window.triggerAnamodDirtyState();
                    }
                });

                window.editorInstance.layout();
                window.updateAnamodTerminal(`[SYSTEM] Monaco core engine connected.\n`);
            } catch (err) {
                window.updateAnamodTerminal(`[CRITICAL ERROR] Failed to build instance: ${err.message}\n`);
            }
        }

        mountEditorInstance();

        window.loadWorkspaceFile = function(filePath) {
            window.updateAnamodTerminal(`[SYSTEM] Reading file trace: ${filePath}...\n`);
            $.ajax({
                url: '/aurora/api/files/op/',
                type: 'GET',
                data: { path: filePath },
                success: function(response) {
                    currentFilePath = filePath;
                    if (window.editorInstance !== null && typeof window.editorInstance.setValue === 'function') {
                        window.editorInstance.setValue(response.content);
                        const ext = filePath.split('.').pop().toLowerCase();
                        if (ext === 'py') monaco.editor.setModelLanguage(window.editorInstance.getModel(), 'python');
                        else if (ext === 'css') monaco.editor.setModelLanguage(window.editorInstance.getModel(), 'css');
                        else if (ext === 'html') monaco.editor.setModelLanguage(window.editorInstance.getModel(), 'html');
                        else if (ext === 'js') monaco.editor.setModelLanguage(window.editorInstance.getModel(), 'javascript');
                        else if (ext === 'json') monaco.editor.setModelLanguage(window.editorInstance.getModel(), 'json');
                        
                        setTimeout(function() { window.editorInstance.layout(); }, 50);
                        window.updateAnamodTerminal(`[SYSTEM] File loaded successfully into viewport.\n`);
                    } else {
                        window.updateAnamodTerminal(`[WARNING] Core editor initializing. Re-click file.\n`);
                        mountEditorInstance();
                    }
                    
                    $('#active-file-indicator').text(filePath.split('/').pop()).attr('title', filePath).removeClass('text-warning');
                    $('#anamod-run-btn, #anamod-lint-btn').prop('disabled', false);
                    $('#anamod-save-btn').prop('disabled', true).removeClass('btn-warning text-dark font-weight-bold').addClass('btn-outline-warning');
                    $('#anamod-discard-btn').prop('disabled', true).removeClass('btn-danger text-dark font-weight-bold').addClass('btn-outline-danger');
                },
                error: function(xhr) {
                    window.updateAnamodTerminal(`[ERROR] Failed to load target node filesystem pointer: ${xhr.statusText}\n`);
                }
            });
        };
// ======================================================================
// END: ANAMOD_CORE_BASE_AND_LOADER (PATCH 1 OF 3)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/anamod.js (PATCH 2 OF 3)
// START: ANAMOD_SAVE_AND_DISCARD_PIPELINE
// ======================================================================
        // 5. Action Controls Backend Pipeline Form Integrations
        $('#anamod-save-btn').off('click').on('click', function() {
            if (!currentFilePath || !window.editorInstance) return;
            window.updateAnamodTerminal(`[SYSTEM] Syncing active layout buffers to host disk...\n`);
            $.ajax({
                url: '/aurora/api/files/op/',
                type: 'POST',
                contentType: 'application/json',
                headers: { 'X-CSRFToken': csrfToken },
                data: JSON.stringify({ path: currentFilePath, content: window.editorInstance.getValue() }),
                success: function() {
                    window.updateAnamodTerminal(`[SUCCESS] File buffers saved to physical disk address.\n`);
                    // Trigger custom event notifying tracker that disk commit is finalized
                    $(document).trigger('buffer:saved');
                },
                error: function(xhr) {
                    window.updateAnamodTerminal(`[ERROR] Commit transaction rejected: ${xhr.statusText}\n`);
                }
            });
        });

        // Discard Button Handler: Re-fetch pristine snapshot from server disk file node
        $('#anamod-discard-btn').off('click').on('click', function() {
            if (!currentFilePath || !window.editorInstance) return;
            window.updateAnamodTerminal(`[SYSTEM] Discarding unsaved modifications, fetching head state...\n`);
            $.ajax({
                url: '/aurora/api/files/op/',
                type: 'GET',
                data: { path: currentFilePath },
                success: function(response) {
                    window.editorInstance.setValue(response.content);
                    window.updateAnamodTerminal(`[SUCCESS] Buffer rolled back cleanly to match source storage state.\n`);
                    // Trigger custom event notifying tracker that rollback execution is complete
                    $(document).trigger('buffer:discarded');
                },
                error: function(xhr) {
                    window.updateAnamodTerminal(`[ERROR] Reversion routine failure: ${xhr.statusText}\n`);
                }
            });
        });
// ======================================================================
// END: ANAMOD_SAVE_AND_DISCARD_PIPELINE (PATCH 2 OF 3)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/anamod.js (PATCH 3 OF 3)
// START: ANAMOD_RUNTIME_AND_RESIZER
// ======================================================================
        $('#anamod-run-btn').off('click').on('click', function() {
            if (!window.editorInstance) return;
            window.updateAnamodTerminal(`[SYSTEM] Deploying micro-worker runtime inside sandboxed engine...\n`);
            $.ajax({
                url: '/aurora/api/sandbox/run/',
                type: 'POST',
                contentType: 'application/json',
                headers: { 'X-CSRFToken': csrfToken },
                data: JSON.stringify({ code: window.editorInstance.getValue() }),
                success: function(response) {
                    window.updateAnamodTerminal(`[SANDBOX RUN OUTPUT]\n${response.output}\n`);
                },
                error: function(xhr) {
                    window.updateAnamodTerminal(`[ERROR] Worker failed to initialize or timed out: ${xhr.statusText}\n`);
                }
            });
        });

        $('#anamod-lint-btn').off('click').on('click', function() {
            if (!window.editorInstance) return;
            window.updateAnamodTerminal(`[SYSTEM] Piping file syntax to analysis checker...\n`);
            $.ajax({
                url: '/aurora/api/sandbox/lint/',
                type: 'POST',
                contentType: 'application/json',
                headers: { 'X-CSRFToken': csrfToken },
                data: JSON.stringify({ code: window.editorInstance.getValue() }),
                success: function(response) {
                    window.updateAnamodTerminal(`[LINTER ENGINE RESULTS]\n${response.errors}\n`);
                },
                error: function(xhr) {
                    window.updateAnamodTerminal(`[ERROR] Linter execution subsystem crashed: ${xhr.statusText}\n`);
                }
            });
        });

        window.resizeAnamodEditor = function() {
            if (window.editorInstance !== null && typeof window.editorInstance.layout === 'function') {
                window.editorInstance.layout();
            }
        };
    };
})(window);
// ======================================================================
// END: ANAMOD_RUNTIME_AND_RESIZER (PATCH 3 OF 3)
// ======================================================================
