// ======================================================================
// FILE: aurora/static/aurora/js/anamod_workspace.js (PATCH 1 OF 1)
// START: DECOUPLED_IDE_TREE_WORKSPACE_CONTROLLER
// ======================================================================
(function(window) {
    window.initAnamodWorkspaceTree = function() {
        console.log("[Anamod Workspace Tree] Mounting decoupled tree asset...");
        const $treeContainer = $('#anamod-file-tree');
        const $contextMenu = $('#anamod-tree-context-menu');
        let selectedNodeId = null;

        if (!$treeContainer.length) return;

        window.refreshWorkspaceTree = function() {
            const treeInstance = $treeContainer.jstree(true);
            if (treeInstance) {
                console.log("[Anamod Workspace Tree] Invalidating cache matrices, reloading tree layout...");
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

        // 2. Intercept Context Menu Actions with Overflow Flip Calculation
        $treeContainer.on('contextmenu', '.jstree-anchor', function(e) {
            const $anchor = $(this);
            if ($anchor.hasClass('anamod-tree-folder-text')) return;

            e.preventDefault();
            e.stopPropagation();

            const $li = $anchor.closest('.jstree-node');
            selectedNodeId = $li.attr('id');

            // Find the closest absolute relative container bounds to calculate position exactly
            const $parentContainer = $contextMenu.parent();
            const containerOffset = $parentContainer.offset();
            
            let posX = e.pageX - (containerOffset ? containerOffset.left : 0);
            let posY = e.pageY - (containerOffset ? containerOffset.top : 0);

            // Temporarily unhide the popup element hidden offscreen to capture true rendered height boundaries
            $contextMenu.css({ display: 'block', visibility: 'hidden' });
            const menuHeight = $contextMenu.outerHeight() || 80;
            const containerHeight = $parentContainer.innerHeight() || $(window).height();
            $contextMenu.css({ visibility: 'visible' });

            // Boundary Overflow Guard: Flip popups upwards if they would bleed past the bottom panel wall
            if (posY + menuHeight > containerHeight) {
                posY = posY - menuHeight;
                if (posY < 0) posY = 4; // Absolute safety cap to stop top bleed overflows
            }

            $contextMenu.css({
                left: (posX + 2) + 'px', // Minor padding offset so the cursor sits comfortably outside the item row edges
                top: posY + 'px'
            });
        });

        $(document).on('click contextmenu', function(e) {
            if (!$(e.target).closest('#anamod-tree-context-menu').length) {
                $contextMenu.hide();
            }
        });

        // 3. Connect Desktop Context Item Trigger Elements
        $('#ctx-rename-btn').off('click').on('click', function(e) {
            e.stopPropagation();
            $contextMenu.hide();
            if (selectedNodeId) {
                $treeContainer.jstree(true).edit(selectedNodeId);
            }
        });

        $('#ctx-delete-btn').off('click').on('click', function(e) {
            e.stopPropagation();
            $contextMenu.hide();
            if (selectedNodeId) {
                const nodeData = $treeContainer.jstree(true).get_node(selectedNodeId);
                if (nodeData && nodeData.data && nodeData.data.path) {
                    if (typeof window.deleteWorkspaceFile === 'function') {
                        window.deleteWorkspaceFile(nodeData.data.path);
                    }
                }
            }
        });

        // 4. Handle Inline Rename Commits
        $treeContainer.on('rename_node.jstree', function(e, data) {
            if (data.text === data.old) return;
            if (data.node.data && data.node.data.path) {
                if (typeof window.renameWorkspaceFile === 'function') {
                    window.renameWorkspaceFile(data.node.data.path, data.text);
                }
            }
        });

        // 5. Handle Directory Tree Node Selection Lifecycle
        $treeContainer.off("select_node.jstree").on("select_node.jstree", function (e, data) {
            const activeNode = data.node;
            if (!activeNode) return;

            if (activeNode.type === 'folder' || (activeNode.children && activeNode.children.length > 0)) {
                $treeContainer.jstree(true).toggle_node(data.node);
                return;
            }

            if (activeNode.data && activeNode.data.path) {
                if (typeof window.loadWorkspaceFile === 'function') {
                    window.loadWorkspaceFile(activeNode.data.path);
                }
            }
        });
    };
})(window);
// ======================================================================
// END: DECOUPLED_IDE_TREE_WORKSPACE_CONTROLLER (PATCH 1 OF 1)
// ======================================================================
