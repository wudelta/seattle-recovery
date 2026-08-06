// ======================================================================
// FILE: aurora/static/aurora/js/anamod_workspace.js (PATCH 1 OF 3)
// START: DECOUPLED_IDE_TREE_WORKSPACE_CONTROLLER
// ======================================================================
(function(window) {
    window.initAnamodWorkspaceTree = function() {
        console.log("[Anamod Workspace Tree] Mounting decoupled tree asset...");
        const $treeContainer = $('#anamod-file-tree');
        const $fileContextMenu = $('#anamod-tree-context-menu');
        const $folderContextMenu = $('#anamod-folder-context-menu');
        let selectedNodeId = null;

        if (!$treeContainer.length) return;

        window.refreshWorkspaceTree = function() {
            const treeInstance = $treeContainer.jstree(true);
            if (treeInstance) {
                console.log("[Anamod Workspace Tree] Reloading tree layout...");
                treeInstance.refresh();
            }
        };

        // 1. Initialize jsTree with absolute baseline profile properties
        $treeContainer.jstree({
            'core': {
                'check_callback': true,
                'data': {
                    'url': '/aurora/api/files/tree/',
                    'dataType': 'json',
                    'dataFilter': function(rawString) {
                        let jsonArray = JSON.parse(rawString);
                        function transformAndSortNodeMeta(nodes) {
                            if (!nodes || !Array.isArray(nodes)) return;
                            nodes.forEach(node => {
                                if (node.children && Array.isArray(node.children)) {
                                    node.type = 'folder';
                                    node.icon = false;
                                    node.a_attr = { "class": "anamod-tree-folder-text font-weight-bold" };
                                    node.state = { opened: false };
                                    transformAndSortNodeMeta(node.children);
                                } else {
                                    const ext = node.text.split('.').pop().toLowerCase();
                                    node.type = 'file';
                                    if (ext === 'py') node.icon = 'jstree-file text-info fw-bold';
                                    else if (ext === 'html' || ext === 'htm') node.icon = 'jstree-file text-danger';
                                    else if (ext === 'css') node.icon = 'jstree-file text-success';
                                    else if (ext === 'js' || ext === 'ts') node.icon = 'jstree-file text-warning';
                                    else if (['json', 'yaml', 'yml', 'ini', 'cfg'].includes(ext)) node.icon = 'jstree-file text-secondary';
                                    else node.icon = 'jstree-file text-muted';
                                }
                            });

                            nodes.sort((a, b) => {
                                const isAFolder = (a.type === 'folder');
                                const isBFolder = (b.type === 'folder');
                                if (isAFolder && !isBFolder) return -1;
                                if (!isAFolder && isBFolder) return 1;
                                return a.text.localeCompare(b.text, undefined, { sensitivity: 'base', numeric: true });
                            });
                        }
                        transformAndSortNodeMeta(jsonArray);
                        return JSON.stringify(jsonArray);
                    }
                },
                'themes': {
                    'name': 'default',
                    'dots': true,
                    'icons': true,
                    'url': '/static/css/jstree-style.min.css'
                }
            }
        });
// ======================================================================
// END: DECOUPLED_IDE_TREE_WORKSPACE_CONTROLLER (PATCH 1 OF 3)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/anamod_workspace.js (PATCH 2 OF 3)
// START: ANAMOD_TREE_CONTEXT_ROUTING_AND_BOUNDS
// ======================================================================
        // Helper calculation function to position any context menu while strictly avoiding screen bleed
        function openContextMenu($menu, e) {
            const $parentContainer = $menu.parent();
            const containerOffset = $parentContainer.offset();
            
            let posX = e.pageX - (containerOffset ? containerOffset.left : 0);
            let posY = e.pageY - (containerOffset ? containerOffset.top : 0);

            $menu.css({ display: 'block', visibility: 'hidden' });
            const menuHeight = $menu.outerHeight() || 80;
            const containerHeight = $parentContainer.innerHeight() || $(window).height();
            $menu.css({ visibility: 'visible' });

            if (posY + menuHeight > containerHeight) {
                posY = posY - menuHeight;
                if (posY < 0) posY = 4;
            }

            $menu.css({
                left: (posX + 2) + 'px',
                top: posY + 'px'
            });
        }

        // 2. Dual-Track Context Menu Routing Interception Loop
        $treeContainer.on('contextmenu', '.jstree-anchor', function(e) {
            e.preventDefault();
            e.stopPropagation();

            $fileContextMenu.hide();
            $folderContextMenu.hide();

            const $anchor = $(this);
            const $li = $anchor.closest('.jstree-node');
            selectedNodeId = $li.attr('id');

            if ($anchor.hasClass('anamod-tree-folder-text')) {
                // TRACK A: Right-clicked folder launches folder-scoped action matrix panel
                openContextMenu($folderContextMenu, e);
            } else {
                // TRACK B: Right-clicked file surfaces asset rename and delete operations
                openContextMenu($fileContextMenu, e);
            }
        });

        // Globally hide context menus on mouse clicks outside the wrapper blocks
        $(document).on('click contextmenu', function(e) {
            if (!$(e.target).closest('#anamod-tree-context-menu, #anamod-folder-context-menu').length) {
                $fileContextMenu.hide();
                $folderContextMenu.hide();
            }
        });
// ======================================================================
// END: ANAMOD_TREE_CONTEXT_ROUTING_AND_BOUNDS (PATCH 2 OF 3)
// ======================================================================

// ======================================================================
// FILE: aurora/static/aurora/js/anamod_workspace.js (PATCH 3 OF 3)
// START: ANAMOD_TREE_ACTION_DELEGATIONS_AND_CREATION
// ======================================================================
        // 3. Connect Desktop Context Item Trigger Elements
        $('#ctx-rename-btn').off('click').on('click', function(e) {
            e.stopPropagation();
            $fileContextMenu.hide();

            if (selectedNodeId) {
                $treeContainer.jstree(true).edit(selectedNodeId);
            }
        });

        $('#ctx-delete-btn').off('click').on('click', function(e) {
            e.stopPropagation();
            $fileContextMenu.hide();

            if (selectedNodeId) {
                const nodeData = $treeContainer
                    .jstree(true)
                    .get_node(selectedNodeId);

                if (
                    nodeData &&
                    nodeData.data &&
                    nodeData.data.path
                ) {
                    if (
                        typeof window.deleteWorkspaceFile ===
                        'function'
                    ) {
                        window.deleteWorkspaceFile(
                            nodeData.data.path
                        );
                    }
                }
            }
        });

        function refreshAndFocusWorkspaceNode(
            treeInstance,
            parentNodeId,
            targetPath
        ) {
            $treeContainer.one('refresh.jstree', function() {
                console.log(
                    '[Anamod Workspace Tree] Rebuild finished. ' +
                    'Enforcing layout expansion parameters...'
                );

                treeInstance.open_node(parentNodeId, function() {
                    setTimeout(function() {
                        let foundNodeId = null;

                        Object.keys(
                            treeInstance._model.data
                        ).forEach(function(id) {
                            const item =
                                treeInstance._model.data[id];

                            if (
                                item.data &&
                                item.data.path === targetPath
                            ) {
                                foundNodeId = id;
                            }
                        });

                        if (foundNodeId) {
                            console.log(
                                '[Anamod Workspace Tree] New ' +
                                'workspace node resolved. Shifting ' +
                                'viewport focus.'
                            );

                            treeInstance.deselect_all();
                            treeInstance.select_node(foundNodeId);
                            treeInstance.open_node(foundNodeId);
                        } else {
                            console.warn(
                                '[Anamod Workspace Tree] Focus ' +
                                'route path resolution failed for ' +
                                'pointer: ' +
                                targetPath
                            );
                        }
                    }, 80);
                });
            });

            if (
                typeof window.refreshWorkspaceTree === 'function'
            ) {
                window.refreshWorkspaceTree();
            } else {
                treeInstance.refresh();
            }
        }

        // 4. File Creation Execution Routing Pipeline Integration
        $('#ctx-add-file-btn')
            .off('click')
            .on('click', function(e) {
                e.stopPropagation();
                $folderContextMenu.hide();

                if (!selectedNodeId) return;

                const treeInstance =
                    $treeContainer.jstree(true);
                const nodeData =
                    treeInstance.get_node(selectedNodeId);

                if (
                    nodeData &&
                    nodeData.data &&
                    nodeData.data.path
                ) {
                    const parentFolderPath =
                        nodeData.data.path;
                    const folderIdToOpen = selectedNodeId;

                    const inputName = prompt(
                        'Add New File Here\n' +
                        'Directory Context: ' +
                        parentFolderPath +
                        '\nEnter file name ' +
                        "(e.g., 'utils.py'):"
                    );

                    if (
                        !inputName ||
                        !inputName.trim()
                    ) {
                        return;
                    }

                    const cleanParent = parentFolderPath
                        .replace(/^\/app\/?/, '')
                        .trim();
                    const cleanName = inputName.trim();
                    const fullNewFilePath = cleanParent
                        ? (
                            cleanParent.replace(/\/$/, '') +
                            '/' +
                            cleanName
                        )
                        : cleanName;
                    const finalContainerPath =
                        '/app/' + fullNewFilePath;

                    window.updateAnamodTerminal(
                        '[SYSTEM] Scaffolding new file ' +
                        'inside selected directory...\n'
                    );

                    $.ajax({
                        url: '/aurora/api/files/op/',
                        type: 'POST',
                        contentType: 'application/json',
                        headers: {
                            'X-CSRFToken':
                                window.csrfToken ||
                                $(
                                    '[name=csrfmiddlewaretoken]'
                                ).val() ||
                                ''
                        },
                        data: JSON.stringify({
                            path: fullNewFilePath,
                            type: 'file',
                            content: ''
                        }),
                        success: function() {
                            window.updateAnamodTerminal(
                                '[SUCCESS] New file created at ' +
                                finalContainerPath +
                                '.\n'
                            );

                            refreshAndFocusWorkspaceNode(
                                treeInstance,
                                folderIdToOpen,
                                finalContainerPath
                            );
                        },
                        error: function(xhr) {
                            const message = (
                                xhr.responseJSON &&
                                xhr.responseJSON.error
                            )
                                ? xhr.responseJSON.error
                                : xhr.statusText;

                            window.updateAnamodTerminal(
                                '[ERROR] File creation failed: ' +
                                message +
                                '\n'
                            );
                        }
                    });
                }
            });

        // 5. Directory Creation Execution Routing Pipeline Integration
        $('#ctx-add-directory-btn')
            .off('click')
            .on('click', function(e) {
                e.stopPropagation();
                $folderContextMenu.hide();

                if (!selectedNodeId) return;

                const treeInstance =
                    $treeContainer.jstree(true);
                const nodeData =
                    treeInstance.get_node(selectedNodeId);

                if (
                    nodeData &&
                    nodeData.data &&
                    nodeData.data.path
                ) {
                    const parentFolderPath =
                        nodeData.data.path;
                    const folderIdToOpen = selectedNodeId;

                    const inputName = prompt(
                        'Add New Directory Here\n' +
                        'Directory Context: ' +
                        parentFolderPath +
                        '\nEnter directory name:'
                    );

                    if (
                        !inputName ||
                        !inputName.trim()
                    ) {
                        return;
                    }

                    const cleanParent = parentFolderPath
                        .replace(/^\/app\/?/, '')
                        .trim();
                    const cleanName = inputName.trim();
                    const fullNewDirectoryPath =
                        cleanParent
                            ? (
                                cleanParent.replace(/\/$/, '') +
                                '/' +
                                cleanName
                            )
                            : cleanName;
                    const finalContainerPath =
                        '/app/' + fullNewDirectoryPath;

                    window.updateAnamodTerminal(
                        '[SYSTEM] Creating new directory ' +
                        'inside selected workspace branch...\n'
                    );

                    $.ajax({
                        url: '/aurora/api/files/op/',
                        type: 'POST',
                        contentType: 'application/json',
                        headers: {
                            'X-CSRFToken':
                                window.csrfToken ||
                                $(
                                    '[name=csrfmiddlewaretoken]'
                                ).val() ||
                                ''
                        },
                        data: JSON.stringify({
                            path: fullNewDirectoryPath,
                            type: 'directory'
                        }),
                        success: function() {
                            window.updateAnamodTerminal(
                                '[SUCCESS] New directory ' +
                                'created at ' +
                                finalContainerPath +
                                '.\n'
                            );

                            refreshAndFocusWorkspaceNode(
                                treeInstance,
                                folderIdToOpen,
                                finalContainerPath
                            );
                        },
                        error: function(xhr) {
                            const message = (
                                xhr.responseJSON &&
                                xhr.responseJSON.error
                            )
                                ? xhr.responseJSON.error
                                : xhr.statusText;

                            window.updateAnamodTerminal(
                                '[ERROR] Directory creation ' +
                                'failed: ' +
                                message +
                                '\n'
                            );
                        }
                    });
                }
            });

        // 6. Refresh Project Hierarchy Control
        $('#anamod-refresh-tree-btn')
            .off('click')
            .on('click', function(e) {
                e.preventDefault();

                if (
                    typeof window.refreshWorkspaceTree ===
                    'function'
                ) {
                    window.updateAnamodTerminal(
                        '[SYSTEM] Refreshing Project ' +
                        'Hierarchy from disk...\n'
                    );

                    window.refreshWorkspaceTree();
                }
            });

        // 7. Load File by Repository-Relative Path Controls
        $('#anamod-load-file-btn')
            .off('click')
            .on('click', function(e) {
                e.preventDefault();

                const $panel =
                    $('#anamod-load-file-panel');
                const panelIsHidden =
                    $panel.hasClass('d-none');

                $panel.toggleClass(
                    'd-none',
                    !panelIsHidden
                );

                $(this).attr(
                    'aria-expanded',
                    panelIsHidden
                        ? 'true'
                        : 'false'
                );

                $('#anamod-load-file-error')
                    .addClass('d-none')
                    .text('');

                if (panelIsHidden) {
                    setTimeout(function() {
                        $('#anamod-load-file-path')
                            .trigger('focus')
                            .select();
                    }, 0);
                }
            });

        $('#anamod-load-file-cancel-btn')
            .off('click')
            .on('click', function(e) {
                e.preventDefault();

                $('#anamod-load-file-panel')
                    .addClass('d-none');

                $('#anamod-load-file-btn')
                    .attr('aria-expanded', 'false');

                $('#anamod-load-file-error')
                    .addClass('d-none')
                    .text('');
            });

        $('#anamod-load-file-form')
            .off('submit')
            .on('submit', function(e) {
                e.preventDefault();

                const $pathInput =
                    $('#anamod-load-file-path');
                const $error =
                    $('#anamod-load-file-error');

                const filePath = (
                    $pathInput.val() || ''
                )
                    .trim()
                    .replace(/^\/app\/?/, '')
                    .replace(/^app\/?/, '')
                    .replace(/^\/+/, '');

                if (!filePath) {
                    $error
                        .removeClass('d-none')
                        .text(
                            'Enter a repository-relative ' +
                            'file path.'
                        );

                    return;
                }

                if (
                    typeof window.loadWorkspaceFile !==
                    'function'
                ) {
                    $error
                        .removeClass('d-none')
                        .text(
                            'The Anamod file loader is ' +
                            'not available.'
                        );

                    return;
                }

                $error
                    .addClass('d-none')
                    .text('');

                $('#anamod-load-file-panel')
                    .addClass('d-none');

                $('#anamod-load-file-btn')
                    .attr('aria-expanded', 'false');

                $pathInput.val('');

                window.loadWorkspaceFile(filePath);
            });

        // 8. Handle Inline Rename Commits
        $treeContainer.on(
            'rename_node.jstree',
            function(e, data) {
                if (data.text === data.old) return;

                if (
                    data.node.data &&
                    data.node.data.path
                ) {
                    if (
                        typeof window.renameWorkspaceFile ===
                        'function'
                    ) {
                        window.renameWorkspaceFile(
                            data.node.data.path,
                            data.text
                        );
                    }
                }
            }
        );

        // 9. Handle Directory Tree Node Selection Lifecycle
        $treeContainer
            .off('select_node.jstree')
            .on(
                'select_node.jstree',
                function(e, data) {
                    const activeNode = data.node;

                    if (!activeNode) return;

                    if (
                        activeNode.type === 'folder' ||
                        (
                            activeNode.children &&
                            activeNode.children.length > 0
                        )
                    ) {
                        $treeContainer
                            .jstree(true)
                            .toggle_node(data.node);

                        return;
                    }

                    if (
                        activeNode.data &&
                        activeNode.data.path
                    ) {
                        if (
                            typeof window.loadWorkspaceFile ===
                            'function'
                        ) {
                            window.loadWorkspaceFile(
                                activeNode.data.path
                            );
                        }
                    }
                }
            );
    };
})(window);
// ======================================================================
// END: ANAMOD_TREE_ACTION_DELEGATIONS_AND_CREATION (PATCH 3 OF 3)
// ======================================================================