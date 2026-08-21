// ======================================================================
// FILE: aurora/static/aurora/js/anamod/anamod.js (PATCH 1 OF 4)
// START: ANAMOD_CORE_BASE_AND_INITIALIZATION
// ======================================================================
(function(window) {
    window.editorInstance = null;
    let currentFilePath = null;

    window.initAnamodConsole = function(csrfToken) {
        console.log("[Anamod Workspace] Spawning control channels...");

        // Reverse Prepend Terminal Output Mechanism
        window.updateAnamodTerminal = function(message) {
            const $term = $('#anamod-terminal-stream');
            if ($term.length) {
                $term.prepend(message);
                $term.scrollTop(0);
            }
        };

        function setComponentRegistryDescription(
            message,
            className
        ) {
            const $viewport =
                $('#anamod-component-registry-description');

            if (!$viewport.length) {
                return;
            }

            $viewport
                .removeClass(
                    'text-muted text-info text-warning ' +
                    'text-danger text-success'
                )
                .addClass(className || 'text-muted')
                .text(message);
        }

        function normalizeRegistryFilePath(filePath) {
            return (
                filePath || ''
            )
                .trim()
                .replace(/^\/app\/?/, '')
                .replace(/^app\/?/, '')
                .replace(/^\/+/, '');
        }

        function loadComponentRegistryDescription(filePath) {
            const normalizedPath =
                normalizeRegistryFilePath(filePath);

            if (!normalizedPath) {
                setComponentRegistryDescription(
                    'No active file selected.',
                    'text-muted'
                );
                return;
            }

            setComponentRegistryDescription(
                'Loading Component Registry context...',
                'text-muted'
            );

            $.ajax({
                url: '/aurora/api/component_registry/',
                type: 'GET',
                data: {
                    file_path: normalizedPath
                },
                success: function(response) {
                    const component =
                        response.component || {};

                    if (
                        component.description_is_current &&
                        component.description
                    ) {
                        setComponentRegistryDescription(
                            component.description,
                            'text-info'
                        );
                        return;
                    }

                    if (component.freshness_message) {
                        setComponentRegistryDescription(
                            component.freshness_message,
                            (
                                component.analysis_status ===
                                'FAILED'
                            )
                                ? 'text-danger'
                                : 'text-warning'
                        );
                        return;
                    }

                    if (
                        component.analysis_status ===
                        'PENDING'
                    ) {
                        setComponentRegistryDescription(
                            'Component Registry description is ' +
                            'pending enrichment.',
                            'text-warning'
                        );
                        return;
                    }

                    if (
                        component.analysis_status ===
                        'FAILED'
                    ) {
                        setComponentRegistryDescription(
                            'Component Registry enrichment failed; ' +
                            'no current description is available.',
                            'text-danger'
                        );
                        return;
                    }

                    setComponentRegistryDescription(
                        'No current Component Registry ' +
                        'description is available for this file.',
                        'text-muted'
                    );
                },
                error: function(xhr) {
                    if (xhr.status === 404) {
                        setComponentRegistryDescription(
                            'No Component Registry record exists ' +
                            'for this file.',
                            'text-muted'
                        );
                        return;
                    }

                    const message = (
                        xhr.responseJSON &&
                        (
                            xhr.responseJSON.message ||
                            xhr.responseJSON.error
                        )
                    )
                        ? (
                            xhr.responseJSON.message ||
                            xhr.responseJSON.error
                        )
                        : xhr.statusText;

                    setComponentRegistryDescription(
                        'Component Registry lookup failed: ' +
                        message,
                        'text-danger'
                    );
                }
            });
        }

        function setAnamodActivity(
            message,
            className
        ) {
            const $activity =
                $('#anamod-session-activity');

            if (!$activity.length) {
                return;
            }

            $activity
                .removeClass(
                    'text-muted text-info text-warning ' +
                    'text-danger text-success'
                )
                .addClass(className || 'text-muted')
                .text(message);
        }

        function isAnamodRegistryTelemetry(messageChunk) {
            const message = String(
                messageChunk || ''
            ).trimStart();

            return (
                message.startsWith('[REGISTRY]') ||
                message.startsWith('[REGISTRY ERROR]') ||
                message.startsWith('[REGISTRY REVIEW]') ||
                message.startsWith('[REGISTRY FAILURE]') ||
                message.startsWith('Summary:')
            );
        }

        $(document)
            .off(
                'aurora:telemetry_stream.anamod'
            )
            .on(
                'aurora:telemetry_stream.anamod',
                function(event, messageChunk) {
                    if (
                        !isAnamodRegistryTelemetry(
                            messageChunk
                        )
                    ) {
                        return;
                    }

                    const message =
                        String(messageChunk || '');

                    window.updateAnamodTerminal(
                        message.endsWith('\n')
                            ? message
                            : message + '\n'
                    );
                }
            );

        function setRegistryActionButtonsDisabled(disabled) {
            $('#anamod-refresh-registry-btn')
                .prop('disabled', disabled);

            $('#anamod-enrich-registry-btn')
                .prop('disabled', disabled);
        }

        function runComponentRegistryAction(action) {
            setRegistryActionButtonsDisabled(true);

            const isRefresh =
                action === 'refresh';

            const actionLabel = (
                isRefresh
                    ? 'Refreshing Component Registry...'
                    : 'Enriching Component Registry...'
            );

            setAnamodActivity(
                actionLabel,
                'text-info'
            );

            $.ajax({
                url: '/aurora/api/component_registry/',
                type: 'POST',
                contentType: 'application/json',
                headers: {
                    'X-CSRFToken':
                        window.csrfToken ||
                        $('[name=csrfmiddlewaretoken]').val() ||
                        ''
                },
                data: JSON.stringify({
                    action: action
                }),
                success: function(response) {
                    setAnamodActivity(
                        response.message,
                        'text-success'
                    );

                    if (currentFilePath) {
                        loadComponentRegistryDescription(
                            currentFilePath
                        );
                    }
                },
                error: function(xhr) {
                    const message = (
                        xhr.responseJSON &&
                        (
                            xhr.responseJSON.message ||
                            xhr.responseJSON.error
                        )
                    )
                        ? (
                            xhr.responseJSON.message ||
                            xhr.responseJSON.error
                        )
                        : xhr.statusText;

                    setAnamodActivity(
                        message,
                        'text-danger'
                    );

                    if (currentFilePath) {
                        loadComponentRegistryDescription(
                            currentFilePath
                        );
                    }
                },
                complete: function() {
                    setRegistryActionButtonsDisabled(
                        false
                    );
                }
            });
        }

        $('#anamod-refresh-registry-btn')
            .off('click')
            .on('click', function(e) {
                e.preventDefault();
                runComponentRegistryAction(
                    'refresh'
                );
            });

        $('#anamod-enrich-registry-btn')
            .off('click')
            .on('click', function(e) {
                e.preventDefault();
                runComponentRegistryAction(
                    'enrich'
                );
            });

        $('#anamod-toggle-registry-description-btn')
            .off('click')
            .on('click', function(e) {
                e.preventDefault();

                const $viewport =
                    $('#anamod-component-registry-description');

                const hidden =
                    $viewport.hasClass('d-none');

                $viewport.toggleClass(
                    'd-none',
                    !hidden
                );

                $(this)
                    .attr(
                        'aria-expanded',
                        hidden ? 'true' : 'false'
                    )
                    .text(
                        hidden ? '−' : '+'
                    );
            });

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
// ======================================================================
// END: ANAMOD_CORE_BASE_AND_INITIALIZATION (PATCH 1 OF 4)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/anamod/anamod.js (PATCH 2 OF 4)
// START: ANAMOD_REALTIME_MULTI_MARKER_VALIDATOR
// ======================================================================
// Multi-marker frontend parser: splits filtered lint rows and plots markers line-by-line safely
function runInlineSyntaxValidation(codeText, model) {
    if (!currentFilePath || !currentFilePath.toLowerCase().endsWith('.py')) {
        monaco.editor.setModelMarkers(model, "owner", []);
        return;
    }

    $.ajax({
        url: '/aurora/api/sandbox/lint/',
        type: 'POST',
        contentType: 'application/json',
        headers: { 'X-CSRFToken': csrfToken },
        data: JSON.stringify({ code: codeText }),
        success: function(response) {
            const markers = [];
            const rawLines = response.errors ? response.errors.split('\n') : [];
            
            // 1. Process fallback fatal compiler syntax exceptions first
            if (response.errors && response.errors.includes('❌')) {
                const compileMatch = response.errors.match(/line\s+(\d+)/i);
                if (compileMatch) {
                    const lineNum = parseInt(compileMatch, 10);
                    markers.push({
                        startLineNumber: lineNum,
                        endLineNumber: lineNum,
                        startColumn: 1,
                        endColumn: 100,
                        message: response.errors,
                        severity: monaco.MarkerSeverity.Error
                    });
                }
            } else {
                // 2. Clear to parse individual flake8 rows line-by-line safely
                rawLines.forEach(function(line) {
                    const match = line.match(/current_file\.py:(\d+):(\d+):\s+(.*)/i);
                    if (match && match) {
                        const lineNum = parseInt(match, 10);
                        const colNum = parseInt(match, 10);
                        const msgStr = match || line;
                        markers.push({
                            startLineNumber: lineNum,
                            endLineNumber: lineNum,
                            startColumn: colNum || 1,
                            endColumn: colNum ? colNum + 15 : 100,
                            message: msgStr.trim(),
                            severity: monaco.MarkerSeverity.Error
                        });
                    }
                });
            }

            monaco.editor.setModelMarkers(model, "owner", markers);
        }
    });
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
            wordWrap: 'on',
            readOnly: false
        });
        
        let debounceTimer;
        window.editorInstance.onDidChangeModelContent(function() {
            // Activate Dirty State highlighting parameters programmatically
            $('#anamod-save-btn').prop('disabled', false)
                .removeClass('btn-outline-warning')
                .addClass('btn-warning text-dark font-weight-bold');

            $('#anamod-discard-btn').prop('disabled', false)
                .removeClass('btn-outline-danger')
                .addClass('btn-danger text-dark font-weight-bold');

            $('#active-file-indicator').addClass('text-warning');
            
            const model = window.editorInstance.getModel();
            const currentText = window.editorInstance.getValue();

            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(function() {
                runInlineSyntaxValidation(currentText, model);
            }, 600);
        });
        
        window.editorInstance.layout();
        window.updateAnamodTerminal(
            `[SYSTEM] Monaco core engine connected with active diagnostics loop.\n`
        );
    } catch (err) {
        window.updateAnamodTerminal(
            `[CRITICAL ERROR] Failed to build instance: ${err.message}\n`
        );
    }
}

mountEditorInstance();

function copyTextToClipboard(text, onSuccess) {
    if (
        navigator.clipboard &&
        typeof navigator.clipboard.writeText === 'function'
    ) {
        navigator.clipboard.writeText(text)
            .then(onSuccess)
            .catch(function() {
                copyTextWithFallback(text, onSuccess);
            });

        return;
    }

    copyTextWithFallback(text, onSuccess);
}

function copyTextWithFallback(text, onSuccess) {
    const tempTextarea = document.createElement('textarea');
    tempTextarea.value = text;
    tempTextarea.setAttribute('readonly', '');
    tempTextarea.style.position = 'fixed';
    tempTextarea.style.opacity = '0';

    document.body.appendChild(tempTextarea);
    tempTextarea.select();

    const copied = document.execCommand('copy');
    document.body.removeChild(tempTextarea);

    if (copied) {
        onSuccess();
    }
}

function flashClipboardSuccess($button, restoredText) {
    $button
        .css({
            'color': '#0f5132',
            'background-color': '#d1e7dd',
            'border-color': '#badbcc'
        })
        .text('✓ Copied');

    setTimeout(function() {
        $button
            .css({
                'color': '#8a9ba8',
                'background-color': 'transparent',
                'border-color': '#30404d'
            })
            .text(restoredText);
    }, 1000);
}

// Scoped clipboard copier for the complete active Monaco buffer
$(document)
    .off('click', '#anamod-copy-file-btn')
    .on('click', '#anamod-copy-file-btn', function(e) {
        e.preventDefault();

        if (
            !currentFilePath ||
            !window.editorInstance ||
            typeof window.editorInstance.getValue !== 'function'
        ) {
            return;
        }

        const fileContent = window.editorInstance.getValue();
        const $btn = $(this);

        copyTextToClipboard(fileContent, function() {
            flashClipboardSuccess($btn, '📄 Copy File');
        });
    });

// Scoped clipboard copier for the active repository-relative file path
$(document)
    .off('click', '#anamod-copy-path-btn')
    .on('click', '#anamod-copy-path-btn', function(e) {
        e.preventDefault();
        
        const $indicator = $('#active-file-indicator');
        let pathText =
            currentFilePath ||
            $indicator.attr('title') ||
            $indicator.text();

        pathText = pathText ? pathText.trim() : "";
        
        if (!pathText || pathText === "No file active") {
            return;
        }
        
        pathText = pathText
            .replace(/^\/app\//, '')
            .replace(/^app\//, '');

        const $btn = $(this);

        copyTextToClipboard(pathText, function() {
            flashClipboardSuccess($btn, '📋 Copy Path');
        });
    });
// ======================================================================
// END: ANAMOD_REALTIME_MULTI_MARKER_VALIDATOR (PATCH 2 OF 4)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/anamod/anamod.js (PATCH 3 OF 4)
// START: ANAMOD_SAVE_DISCARD_AND_MUTATION_HOOKS
// ======================================================================
// 3. Central Application Action Form Trigger Elements
$('#anamod-save-btn').off('click').on('click', function() {
    if (!currentFilePath || !window.editorInstance) return;

    window.updateAnamodTerminal(
        `[SYSTEM] Syncing active layout buffers to host disk...\n`
    );

    $.ajax({
        url: '/aurora/api/files/op/',
        type: 'PATCH',
        contentType: 'application/json',
        headers: { 'X-CSRFToken': csrfToken },
        data: JSON.stringify({
            path: currentFilePath,
            content: window.editorInstance.getValue()
        }),
        success: function() {
            window.updateAnamodTerminal(
                `[SUCCESS] File buffers saved to physical disk address.\n`
            );

            $('#anamod-save-btn')
                .prop('disabled', true)
                .removeClass('btn-warning text-dark font-weight-bold')
                .addClass('btn-outline-warning');

            $('#anamod-discard-btn')
                .prop('disabled', true)
                .removeClass('btn-danger text-dark font-weight-bold')
                .addClass('btn-outline-danger');

            $('#active-file-indicator').removeClass('text-warning');
        },
        error: function(xhr) {
            const message = xhr.responseJSON && xhr.responseJSON.error
                ? xhr.responseJSON.error
                : xhr.statusText;

            window.updateAnamodTerminal(
                `[ERROR] Commit transaction rejected: ${message}\n`
            );
        }
    });
});

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
            $('#anamod-save-btn').prop('disabled', true).removeClass('btn-warning text-dark font-weight-bold').addClass('btn-outline-warning');
            $('#anamod-discard-btn').prop('disabled', true).removeClass('btn-danger text-dark font-weight-bold').addClass('btn-outline-danger');
            $('#active-file-indicator').removeClass('text-warning');
        },
        error: function(xhr) {
            window.updateAnamodTerminal(`[ERROR] Reversion routine failure: ${xhr.statusText}\n`);
        }
    });
});

// Global File Operation Hooks Driven by decoupled tree controllers
window.renameWorkspaceFile = function(oldPath, newName) {
    window.updateAnamodTerminal(`[SYSTEM] Renaming storage node to: ${newName}...\n`);
    $.ajax({
        url: '/aurora/api/files/op/',
        type: 'PUT',
        contentType: 'application/json',
        headers: { 'X-CSRFToken': csrfToken },
        data: JSON.stringify({ path: oldPath, new_name: newName }),
        success: function() {
            window.updateAnamodTerminal(`[SUCCESS] Asset renamed successfully inside project tree.\n`);
            if (typeof window.refreshWorkspaceTree === 'function') window.refreshWorkspaceTree();
        },
        error: function(xhr) {
            window.updateAnamodTerminal(`[ERROR] Rename transaction rejected: ${xhr.statusText}\n`);
            if (typeof window.refreshWorkspaceTree === 'function') window.refreshWorkspaceTree();
        }
    });
};

window.deleteWorkspaceFile = function(filePath) {
    const fileName = filePath.split('/').pop();
    if (!confirm(`Are you absolutely sure you want to permanently delete "${fileName}"?`)) return;
    window.updateAnamodTerminal(`[SYSTEM] Purging file node from system: ${filePath}...\n`);
    $.ajax({
        url: '/aurora/api/files/op/',
        type: 'DELETE',
        contentType: 'application/json',
        headers: { 'X-CSRFToken': csrfToken },
        data: JSON.stringify({ path: filePath }),
        success: function() {
            window.updateAnamodTerminal(`[SUCCESS] File permanently removed from physical disk structure.\n`);
            if (currentFilePath === filePath) {
                currentFilePath = null;
                if (window.editorInstance) window.editorInstance.setValue("# Select a modular file from the directory tree to start coding...\n");
                $('#active-file-indicator').text("No file active").removeClass('text-warning');
                loadComponentRegistryDescription('');
            }
            if (typeof window.refreshWorkspaceTree === 'function') window.refreshWorkspaceTree();
        },
        error: function(xhr) {
            window.updateAnamodTerminal(`[ERROR] Purge execution failure: ${xhr.statusText}\n`);
        }
    });
};
// ======================================================================
// END: ANAMOD_SAVE_DISCARD_AND_MUTATION_HOOKS (PATCH 3 OF 4)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/anamod/anamod.js (PATCH 4 OF 4)
// START: ANAMOD_ACTION_TRIGGERS_AND_FILE_LOADER
// ======================================================================
// 4. Manual Core API Trigger Controls
$('#anamod-run-btn').off('click').on('click', function() {
    if (!currentFilePath || !window.editorInstance) return;
    window.updateAnamodTerminal(`[SYSTEM] Deploying micro-worker runtime inside sandboxed engine...\n`);
    $.ajax({
        url: '/aurora/api/sandbox/run/',
        type: 'POST',
        contentType: 'application/json',
        headers: { 'X-CSRFToken': csrfToken },
        data: JSON.stringify({ code: window.editorInstance.getValue() }),
        success: function(response) {
            window.updateAnamodTerminal(`[SANDBOX RUN OUTPUT] ${response.output}\n`);
        },
        error: function(xhr) {
            window.updateAnamodTerminal(`[ERROR] Sandbox communication breakdown: ${xhr.statusText}\n`);
        }
    });
});

// External asynchronous routing mechanism to hook directly into the project hierarchy layout trees
window.loadWorkspaceFile = function(filePath, options) {
    options = options || {};

    window.updateAnamodTerminal(
        `[SYSTEM] Reading file trace: ${filePath}...
`
    );

    $.ajax({
        url: '/aurora/api/files/op/',
        type: 'GET',
        data: {
            path: filePath
        },
        success: function(response) {
            currentFilePath = filePath;
            const ext = filePath.split('.').pop().toLowerCase();

            if (
                window.editorInstance !== null &&
                typeof window.editorInstance.setValue === 'function'
            ) {
                window.editorInstance.setValue(response.content);

                if (ext === 'py') {
                    monaco.editor.setModelLanguage(
                        window.editorInstance.getModel(),
                        'python'
                    );
                } else if (ext === 'css') {
                    monaco.editor.setModelLanguage(
                        window.editorInstance.getModel(),
                        'css'
                    );
                } else if (ext === 'html') {
                    monaco.editor.setModelLanguage(
                        window.editorInstance.getModel(),
                        'html'
                    );
                } else if (ext === 'js') {
                    monaco.editor.setModelLanguage(
                        window.editorInstance.getModel(),
                        'javascript'
                    );
                } else if (ext === 'json') {
                    monaco.editor.setModelLanguage(
                        window.editorInstance.getModel(),
                        'json'
                    );
                } else if (ext === 'md') {
                    monaco.editor.setModelLanguage(
                        window.editorInstance.getModel(),
                        'markdown'
                    );
                }

                // Enforce real-time hotkey intercepts directly upon a
                // clean file mount sequence.
                window.editorInstance.addCommand(
                    monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS,
                    function() {
                        $('#anamod-save-btn').click();
                    }
                );

                window.editorInstance.addCommand(
                    monaco.KeyCode.F5,
                    function() {
                        if (ext === 'py') {
                            $('#anamod-run-btn').click();
                        }
                    }
                );

                setTimeout(function() {
                    window.editorInstance.layout();
                }, 50);

                window.updateAnamodTerminal(
                    `[SYSTEM] File loaded successfully into viewport.
`
                );
            } else {
                window.updateAnamodTerminal(
                    `[WARNING] Core editor initializing. Re-click file.
`
                );
                mountEditorInstance();
            }

            let displayPath = filePath
                .replace(/^\/app\//, '')
                .replace(/^app\//, '');

            $('#active-file-indicator')
                .text(displayPath)
                .attr('title', filePath)
                .removeClass('text-warning');

            loadComponentRegistryDescription(
                filePath
            );

            if (ext === 'py') {
                $('#anamod-run-btn').prop('disabled', false);
            } else {
                $('#anamod-run-btn').prop('disabled', true);
            }

            $('#anamod-save-btn')
                .prop('disabled', true)
                .removeClass('btn-warning text-dark font-weight-bold')
                .addClass('btn-outline-warning');

            $('#anamod-discard-btn')
                .prop('disabled', true)
                .removeClass('btn-danger text-dark font-weight-bold')
                .addClass('btn-outline-danger');

            if (typeof options.onLoaded === 'function') {
                options.onLoaded(response);
            }
        },
        error: function(xhr) {
            if (
                xhr.status === 404 &&
                typeof options.onNotFound === 'function'
            ) {
                options.onNotFound(xhr);
                return;
            }

            const message = (
                xhr.responseJSON &&
                xhr.responseJSON.error
            )
                ? xhr.responseJSON.error
                : xhr.statusText;

            window.updateAnamodTerminal(
                `[ERROR] Failed to load target node filesystem pointer: ${message}
`
            );

            if (typeof options.onError === 'function') {
                options.onError(xhr, message);
            }
        }
    });
};

}; // This bracket seals window.initAnamodConsole from Patch 1 of 4

})(window); // Closes out the Immediately Invoked Function Expression (IIFE)
// ======================================================================
// END: ANAMOD_ACTION_TRIGGERS_AND_FILE_LOADER (PATCH 4 OF 4)
// ======================================================================
