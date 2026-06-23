// ======================================================================
// FILE: aurora/static/aurora/js/anamod_workspace.js (PATCH 1 OF 1)
// START: DECOUPLED_IDE_TREE_WORKSPACE_CONTROLLER
// ======================================================================
(function(window) {
    window.initAnamodWorkspaceTree = function() {
        console.log("[Anamod Workspace Tree] Mounting decoupled tree asset...");

        const $treeContainer = $('#anamod-file-tree');
        if (!$treeContainer.length) return;

        // 1. Initialize jsTree with Flat CSS Theme Stylesheets
        $treeContainer.jstree({
            'core': {
                'data': {
                    'url': '/aurora/api/files/tree/',
                    'dataType': 'json',
                    // Clean client-side preprocessing hook to format, type, and sort nodes
                    'dataFilter': function(rawString) {
                        let jsonArray = JSON.parse(rawString);
                        
                        function transformAndSortNodeMeta(nodes) {
                            if (!nodes || !Array.isArray(nodes)) return;
                            
                            nodes.forEach(node => {
                                if (node.children && Array.isArray(node.children)) {
                                    node.type = 'folder';
                                    node.icon = 'jstree-folder text-warning fw-bold';
                                    
                                    // Inject custom folder text styles and collapse by default
                                    node.a_attr = { "class": "anamod-tree-folder-text font-weight-bold" };
                                    node.state = { opened: false };
                                    
                                    // Deep recurse into nested subfolders
                                    transformAndSortNodeMeta(node.children);
                                } else {
                                    // Extract explicit extensions to handle specialized icon coloring
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

                            // DETERMINISTIC SORT GRID: Forces folders to the top, then sorts everything alphabetically
                            nodes.sort((a, b) => {
                                const isAFolder = (a.type === 'folder');
                                const isBFolder = (b.type === 'folder');
                                
                                if (isAFolder && !isBFolder) return -1;  // 'a' is a folder, move it up
                                if (!isAFolder && isBFolder) return 1;   // 'b' is a folder, move it up
                                
                                // Fallback: Standard case-insensitive alphabetical string comparison
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
            },
            'types': {
                'folder': { 'icon': 'jstree-folder text-warning' },
                'file': { 'icon': 'jstree-file text-muted' }
            },
            'plugins': ['types']
        });

        // 2. Handle Directory Tree Node Selection Lifecycle
        $treeContainer.off("select_node.jstree").on("select_node.jstree", function (e, data) {
            const activeNode = data.node;
            if (!activeNode) return;

            // Automatically open or collapse a subfolder row when clicked
            if (activeNode.type === 'folder' || (activeNode.children && activeNode.children.length > 0)) {
                $treeContainer.jstree(true).toggle_node(data.node);
                return;
            }

            // Framework-Native Path Resolution: Extract wrapped path metadata safely
            if (activeNode.data && activeNode.data.path) {
                if (typeof window.loadWorkspaceFile === 'function') {
                    window.loadWorkspaceFile(activeNode.data.path);
                }
            } else {
                console.warn("[Anamod Tree] Clicked node is missing its data.path attribute mapping context:", activeNode);
            }
        });
    };
})(window);
// ======================================================================
// END: DECOUPLED_IDE_TREE_WORKSPACE_CONTROLLER (PATCH 1 OF 1)
// ======================================================================
