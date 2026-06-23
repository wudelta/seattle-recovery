// ======================================================================
// FILE: aurora/static/aurora/js/anamod.js (PATCH 1 OF 1)
// START: COMPLETE_ANAMOD_FRONTEND_CONTROLLER
// ======================================================================
(function(window) {
    let editor = null;
    let currentFilePath = null;

    window.initAnamodConsole = function(csrfToken) {
        console.log("[Anamod Workspace] Spawning control channels...");
        
        // 1. Initialize Monaco Editor Frame inside a safe layout calculation block
        if (typeof require !== 'undefined') {
            require.config({ paths: { 'vs': '/static/js/vs' }});
            
            // Explicitly force Monaco to resolve internal background workers absolutely from local folders
            window.MonacoEnvironment = {
                getWorkerUrl: function(workerId, label) {
                    return 'data:text/javascript;charset=utf-8,' + encodeURIComponent(
                        `self.MonacoEnvironment = { baseUrl: '/static/js/vs' }; importScripts('/static/js/vs/base/worker/workerMain.js');`
                    );
                }
            };

            require(['vs/editor/editor.main'], function() {
                const targetDom = document.getElementById('anamod-monaco-viewport');
                if (!targetDom) return;
                
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
                console.log("[Anamod Workspace] Monaco core editor engine unlocked and active.");
            });
        }

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
        $treeContainer.on("select_node.jstree", function (e, data) {
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
                        if (ext === 'py') {
                            monaco.editor.setModelLanguage(editor.getModel(), 'python');
                        } else if (ext === 'css') {
                            monaco.editor.setModelLanguage(editor.getModel(), 'css');
                        } else if (ext === 'html') {
                            monaco.editor.setModelLanguage(editor.getModel(), 'html');
                        } else if (ext === 'js') {
                            monaco.editor.setModelLanguage(editor.getModel(), 'javascript');
                        } else if (ext === 'json') {
                            monaco.editor.setModelLanguage(editor.getModel(), 'json');
                        }
                        
                        setTimeout(function() { editor.layout(); }, 50);
                    } else {
                        updateTerminalStream(`[WARNING] Core editor initializing. Re-click file to display.\n`);
                    }
                    
                    $('#active-file-indicator').text(filePath.split('/').pop()).attr('title', filePath);
                    toggleActionButtons(true);
                    // FIXED: Removed the stray token 'Pis' causing the script interpreter runtime to crash
                    updateTerminalStream(`[SYSTEM] File loaded successfully into viewport.\n`);
                },
                error: function(xhr) {
                    updateTerminalStream(`[ERROR] Failed to load target node filesystem pointer: ${xhr.statusText}\n`);
                }
            });
        }

        $('#anamod-save-btn').on('click', function() {
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
        $('#anamod-run-btn').on('click', function() {
            if (!editor) return;
            updateTerminalStream(`[SYSTEM] Deploying micro-worker runtime inside sandboxed engine...\n`);
            $.ajax({
                url: '/aurora/api/sandbox/run/',
                type: 'POST',
                contentType: 'application/json',
                headers: { 'X-CSRFToken': csrfToken },
                data: JSON.stringify({ code: editor.getValue() }),
                success: function(response) {
                    updateTerminalStream(`[SANDBOX RUN OUTPUT]\n${response.output}`);
                },
                error: function(xhr) {
                    updateTerminalStream(`[ERROR] Worker failed to initialize or timed out: ${xhr.statusText}\n`);
                }
            });
        });

        // 6. Asynchronous Flake8 Linter Interface Call
        $('#anamod-lint-btn').on('click', function() {
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
            if (editor) {
                setTimeout(function() { editor.layout(); }, 100);
            }
        };

        function toggleActionButtons(enabled) {
            $('#anamod-run-btn, #anamod-lint-btn, #anamod-save-btn').prop('disabled', !enabled);
        }

        function updateTerminalStream(message) {
            const $term = $('#anamod-terminal-stream');
            if ($term.length) {
                $term.text($term.text() + message);
                $term.scrollTop($term.scrollHeight);
            }
        }
    };
})(window);
// ======================================================================
// END: COMPLETE_ANAMOD_FRONTEND_CONTROLLER (PATCH 1 OF 1)
// ======================================================================
