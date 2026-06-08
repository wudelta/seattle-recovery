document.addEventListener("DOMContentLoaded", function () {
    console.log("🪐 [Aurora Matrix] Initializing clean graph layout script...");

    // Helper to read your Bootswatch theme colors dynamically for the text labels
    function getThemeColor(variableName) {
        return getComputedStyle(document.documentElement).getPropertyValue(variableName).trim();
    }

    // Capture dynamic text and outline profile variables
    const themeText = getThemeColor('--bs-body-color') || '#ffffff';
    const themeSecondary = getThemeColor('--bs-secondary') || '#94a3b8';
    const themeDark = getThemeColor('--bs-dark') || '#212529';

    // 1. DATASET MATRIX SPECIFICATIONS (Restored to your original hex colors)
    const nodes = new vis.DataSet([
        { id: 1, label: 'Aurora Core', url: "/aurora/", color: '#38bdf8', size: 30 },
        { id: 2, label: 'Console', url: "/aurora/console/", color: '#818cf8' },
        { id: 3, label: 'Neo4j', url: "http://localhost:7474/browser/", color: '#f97316', target: '_blank' },
        { id: 4, label: 'PgWeb', url: "http://localhost:8081/", color: '#f97316', target: '_blank' },
        { id: 5, label: 'Django Admin', url: "/admin/", color: '#f43f5e' },
        { id: 6, label: 'HopeHub', url: "/hopehub/", color: '#d946ef', target: '_blank' },
        //{ id: 7, label: 'Aurora Forge', url: "http://localhost:8000/aurora/pipeline/under_construction_page/", color: '#818cf8' },
        { id: 8, label: 'Delta Notes', url: "/aurora/delta_notes/", color: '#10b981' },
        { id: 9, label: 'GitHub', url: "https://github.com", color: '#94a3b8', target: '_blank' }
    ]);

    const edges = new vis.DataSet([
        { from: 1, to: 2 },
        { from: 1, to: 3 },
        { from: 1, to: 4 },
        { from: 1, to: 5 },
        { from: 1, to: 6 },
        //{ from: 1, to: 7 },
        { from: 1, to: 8 },
        { from: 1, to: 9 }
    ]);

    const container = document.getElementById('network-container');

    // Safety check if the element template wrapper is missing from the drive
    if (!container) {
        console.error("❌ [Aurora Matrix ERROR] Core canvas anchor targeting ID '#network-container' was not found.");
        return;
    }

    const data = { nodes: nodes, edges: edges };

    // 2. STYLING & INTERACTION PARAMETERS
    const options = {
        nodes: {
            shape: 'dot',
            font: {
                color: themeText, // Automatically handles text colors via your active Bootswatch CSS variables
                size: 16
            },
            chosen: {
                node: function(values, id, selected, hovering) {
                    if (hovering) {
                        values.size = values.size + 5;
                        values.borderColor = themeDark;
                        values.borderWidth = 2;
                    }
                },
                label: function(values, id, selected, hovering) {
                    if (hovering) {
                        values.color = themeText;
                        values.mod = 'bold';
                    }
                }
            }
        },
        edges: {
            color: themeSecondary,
            width: 2
        },
        interaction: {
            hover: true,
            zoomView: true
        }
    };

    // 3. INITIALIZE GRAPH LAYER
    const network = new vis.Network(container, data, options);

    const MIN_ZOOM = 0.5;
    const MAX_ZOOM = 2.5;
    let isAdjusting = false; // ANTI-LOOP ATOMIC FLAG SHIELD

    // 4. LOOP-PROOF BOUNDARY THRESHOLD MANAGEMENT
    network.on("zoom", function (params) {
        if (isAdjusting) return; // Breaks recursive call-stack execution loops cleanly!
        const currentScale = network.getScale();
        let targetScale = currentScale;
        let needsFix = false;

        if (currentScale < MIN_ZOOM) {
            targetScale = MIN_ZOOM;
            needsFix = true;
        } else if (currentScale > MAX_ZOOM) {
            targetScale = MAX_ZOOM;
            needsFix = true;
        }

        if (needsFix) {
            isAdjusting = true;
            network.moveTo({ scale: targetScale, position: { x: 0, y: 0 }, animation: false });
            isAdjusting = false;
        } else {
            // Keep content neatly centered during traditional scroll adjustments
            isAdjusting = true;
            network.moveTo({ position: { x: 0, y: 0 }, animation: false });
            isAdjusting = false;
        }
    });

    // 5. MOUSE UI CURSOR TRIGGERS
    network.on("hoverNode", function () {
        container.style.cursor = 'pointer';
    });

    network.on("blurNode", function () {
        container.style.cursor = 'default';
    });

    // 6. GLOBAL ROUTING PIPELINE ENGINE
    network.on("click", function (params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0]; // Safely grab the exact ID number/string from the selection list array
            const clickedNode = nodes.get(nodeId);
            if (clickedNode && clickedNode.url) {
                if (clickedNode.target === '_blank') {
                    window.open(clickedNode.url, '_blank', 'noopener,noreferrer');
                } else {
                    window.location.href = clickedNode.url;
                }
            }
        }
    });

    console.log("✅ [Aurora Matrix] Visual clusters initialization finalized smoothly.");
});
