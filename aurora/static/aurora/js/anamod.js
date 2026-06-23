// ======================================================================
// FILE: aurora/static/aurora/js/anamod.js (PATCH 1 OF 2)
// START: METRIC_OFFLINE_MONACO_REQUIRE_INIT
// ======================================================================
(function(window) {
    let editor = null;
    let currentFilePath = null;

    window.initAnamodConsole = function(csrfToken) {
        console.log("[Anamod Workspace] Spawning control channels...");
        
        // Define offline internal workers to use local paths
        window.MonacoEnvironment = {
            getWorkerUrl: function(workerId, label) {
                if (label === 'json') return '/static/js/vs/language/json/jsonWorker.js';
                if (label === 'css') return '/static/js/vs/language/css/cssWorker.js';
                if (label === 'html') return '/static/js/vs/language/html/htmlWorker.js';
                if (label === 'typescript' || label === 'javascript') return '/static/js/vs/language/typescript/tsWorker.js';
                return '/static/js/vs/base/worker/workerMain.js';
            }
        };

        function mountEditorInstance(callback) {
            const targetDom = document.getElementById('anamod-monaco-viewport');
            if (!targetDom) return;

            if (typeof monaco !== 'undefined' && monaco.editor) {
                buildMonacoInstance(targetDom);
                if (callback) callback();
                return;
            }

            // Official offline configuration using the verified local baseUrl
            if (typeof require !== 'undefined' && typeof require.config === 'function') {
                require.config({ baseUrl: '/static/js' });
                require(['vs/editor/editor.main'], function() {
                    buildMonacoInstance(targetDom);
                    if (callback) callback();
                });
            } else {
                updateTerminalStream(`[ERROR] Monaco vs/loader.js framework missing from template scope.\n`);
            }
        }

        function buildMonacoInstance(targetDom) {
            if (editor !== null) return;
            try {
                editor = monaco.editor.create(targetDom, {
                    value: "# Select a modular file from the directory tree to start coding...\n",
                    language: 'python',
                    theme: 'vs-dark',
                    automaticLayout: true,
                    fontSize: 13,
                    fontFamily: 'Fira Code, Courier New, monospace',
                    minimap: { enabled: false },
                    readOnly: false
                });
                editor.layout();
                updateTerminalStream(`[SYSTEM] Monaco core engine connected and fully typable.\n`);
            } catch (err) {
                updateTerminalStream(`[CRITICAL ERROR] Failed to build instance: ${err.message}\n`);
            }
        }

        // Initialize editor component immediately on panel load
        mountEditorInstance();
// ======================================================================
// END: METRIC_OFFLINE_MONACO_REQUIRE_INIT (PATCH 1 OF 2)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/anamod.js (PATCH 2 OF 2)
// START: STANDALONE_JSTREE_AND_AJAX_CHANNELS
// ======================================================================
        // 2. Initialize jsTree Component Loader with Flat Theme Overrides
        const $treeContainer = $('#anamod-file-tree');
        $treeContainer.jstree({
            'core': {
                'data': {
                    'url': '/aurora/api/files/tree/',
                    'dataType': 'json'
                },
                'themes': { 
                    'name': 'default', 
                    'dots': true, 
                    'icons': true,
                    'url': '/static/css/jstree-style.min.css'
                }
            },
            'types': {
                'default': { 'icon': 'jstree-folder' },
                'file': { 'icon': 'jstree-file' }
            },
            'plugins': ['types']
        });

        // 3. Handle File Tree Node Selection Lifecycle
        $treeContainer.off("select_node.jstree").on("select_node.jstree", function (e, data) {
            const selectedNode = data.node.original;
            if (selectedNode && selectedNode.type === 'file') {
                loadWorkspaceFile(selectedNode.path);
            }
        });

        // 4. Client Side AJAX Storage Pipeline View Wrappers
        function loadWorkspaceFile(filePath) {
            updateTerminalStream(`[SYSTEM] Reading file trace: ${filePath}...\n`);
            $.ajax({
                url: '/aurora/api/files/op/',
                type: 'GET',
                data: { path: filePath },
                success: function(response) {
                    currentFilePath = filePath;
                    
                    if (editor !== null && typeof editor.setValue === 'function') {
                        editor.setValue(response.content);
                        
                        const ext = filePath.split('.').pop().toLowerCase();
                        if (ext === 'py') monaco.editor.setModelLanguage(editor.getModel(), 'python');
                        else if (ext === 'css') monaco.editor.setModelLanguage(editor.getModel(), 'css');
                        else if (ext === 'html') monaco.editor.setModelLanguage(editor.getModel(), 'html');
                        else if (ext === 'js') monaco.editor.setModelLanguage(editor.getModel(), 'javascript');
                        else if (ext === 'json') monaco.editor.setModelLanguage(editor.getModel(), 'json');
                        
                        setTimeout(function() { editor.layout(); }, 50);
                        updateTerminalStream(`[SYSTEM] File loaded successfully into viewport.\n`);
                    } else {
                        updateTerminalStream(`[WARNING] Core editor initializing. Re-click file to display.\n`);
                        mountEditorInstance();
                    }
                    
                    $('#active-file-indicator').text(filePath.split('/').pop()).attr('title', filePath);
                    $('#anamod-run-btn, #anamod-lint-btn, #anamod-save-btn').prop('disabled', false);
                },
                error: function(xhr) {
                    updateTerminalStream(`[ERROR] Failed to load target node filesystem pointer: ${xhr.statusText}\n`);
                }
            });
        }

        $('#anamod-save-btn').off('click').on('click', function() {
            if (!currentFilePath || !editor) return;
            updateTerminalStream(`[SYSTEM] Syncing active layout buffers to host disk...\n`);
            $.ajax({
                url: '/aurora/api/files/op/',
                type: 'POST',
                contentType: 'application/json',
                headers: { 'X-CSRFToken': csrfToken },
                data: JSON.stringify({ path: currentFilePath, content: editor.getValue() }),
                success: function() {
                    updateTerminalStream(`[SUCCESS] File buffers saved to physical disk address.\n`);
                },
                error: function(xhr) {
                    updateTerminalStream(`[ERROR] Commit transaction rejected: ${xhr.statusText}\n`);
                }
            });
        });

        // 5. Sandbox Code Execution Channels
        $('#anamod-run-btn').off('click').on('click', function() {
            if (!editor) return;
            updateTerminalStream(`[SYSTEM] Deploying micro-worker runtime inside sandboxed engine...\n`);
            $.ajax({
                url: '/aurora/api/sandbox/run/',
                type: 'POST',
                contentType: 'application/json',
                headers: { 'X-CSRFToken': csrfToken },
                data: JSON.stringify({ code: editor.getValue() }),
                success: function(response) {
                    updateTerminalStream(`[SANDBOX RUN OUTPUT]\n${response.output}\n`);
                },
                error: function(xhr) {
                    updateTerminalStream(`[ERROR] Worker failed to initialize or timed out: ${xhr.statusText}\n`);
                }
            });
        });

        // 6. Asynchronous Flake8 Linter Interface Call
        $('#anamod-lint-btn').off('click').on('click', function() {
            if (!editor) return;
            updateTerminalStream(`[SYSTEM] Piping file syntax to analysis checker...\n`);
            $.ajax({
                url: '/aurora/api/sandbox/lint/',
                type: 'POST',
                contentType: 'application/json',
                headers: { 'X-CSRFToken': csrfToken },
                data: JSON.stringify({ code: editor.getValue() }),
                success: function(response) {
                    updateTerminalStream(`[LINTER ENGINE RESULTS]\n${response.errors}\n`);
                },
                error: function(xhr) {
                    updateTerminalStream(`[ERROR] Linter execution subsystem crashed: ${xhr.statusText}\n`);
                }
            });
        });

        window.resizeAnamodEditor = function() {
            if (editor !== null && typeof editor.layout === 'function') {
                editor.layout();
            }
        };

        function updateTerminalStream(message) {
            const $term = $('#anamod-terminal-stream');
            if ($term.length) {
                $term.append(message);
                $term.scrollTop($term[0].scrollHeight);
            }
        }
    };
})(window);
// ======================================================================
// END: STANDALONE_JSTREE_AND_AJAX_CHANNELS (PATCH 2 OF 2)
// ======================================================================
