// ======================================================================
// FILE: aurora/static/aurora/js/anamod.js (PATCH 1 OF 1)
// START: CLEAN_IDE_CORE_CONTROLLER
// ======================================================================
(function(window) {
    window.editorInstance = null; // Exposed inside window context for the tree module
    let currentFilePath = null;

    window.initAnamodConsole = function(csrfToken) {
        console.log("[Anamod Workspace] Spawning control channels...");
        
        // Hoist global terminal logging utility hook
        window.updateAnamodTerminal = function(message) {
            const $term = $('#anamod-terminal-stream');
            if ($term.length) {
                $term.append(message);
                $term.scrollTop($term[0].scrollHeight);
            }
        };

        // Define standalone worker overrides
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
                window.updateAnamodTerminal(`[ERROR] Monaco vs/loader.js framework missing from template.\n`);
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
                window.editorInstance.layout();
                window.updateAnamodTerminal(`[SYSTEM] Monaco core engine connected and fully typable.\n`);
            } catch (err) {
                window.updateAnamodTerminal(`[CRITICAL ERROR] Failed to build instance: ${err.message}\n`);
            }
        }

        mountEditorInstance();

        // 4. Client Side AJAX Storage Pipeline View Wrappers (Exposed globally for workspace tree)
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
                        window.updateAnamodTerminal(`[WARNING] Core editor initializing. Re-click file to display.\n`);
                        mountEditorInstance();
                    }
                    
                    $('#active-file-indicator').text(filePath.split('/').pop()).attr('title', filePath);
                    $('#anamod-run-btn, #anamod-lint-btn, #anamod-save-btn').prop('disabled', false);
                },
                error: function(xhr) {
                    window.updateAnamodTerminal(`[ERROR] Failed to load target node filesystem pointer: ${xhr.statusText}\n`);
                }
            });
        };

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
                success: function() { window.updateAnamodTerminal(`[SUCCESS] File buffers saved to physical disk address.\n`); },
                error: function(xhr) { window.updateAnamodTerminal(`[ERROR] Commit transaction rejected: ${xhr.statusText}\n`); }
            });
        });

        $('#anamod-run-btn').off('click').on('click', function() {
            if (!window.editorInstance) return;
            window.updateAnamodTerminal(`[SYSTEM] Deploying micro-worker runtime inside sandboxed engine...\n`);
            $.ajax({
                url: '/aurora/api/sandbox/run/',
                type: 'POST',
                contentType: 'application/json',
                headers: { 'X-CSRFToken': csrfToken },
                data: JSON.stringify({ code: window.editorInstance.getValue() }),
                success: function(response) { window.updateAnamodTerminal(`[SANDBOX RUN OUTPUT]\n${response.output}\n`); },
                error: function(xhr) { window.updateAnamodTerminal(`[ERROR] Worker failed to initialize or timed out: ${xhr.statusText}\n`); }
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
                success: function(response) { window.updateAnamodTerminal(`[LINTER ENGINE RESULTS]\n${response.errors}\n`); },
                error: function(xhr) { window.updateAnamodTerminal(`[ERROR] Linter execution subsystem crashed: ${xhr.statusText}\n`); }
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
// END: CLEAN_IDE_CORE_CONTROLLER (PATCH 1 OF 1)
// ======================================================================
