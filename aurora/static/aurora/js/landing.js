// Define your cluster nodes with reused category colors
const nodes = new vis.DataSet([
    // Core Anchor
    { id: 1, label: 'Aurora Core', color: '#38bdf8', size: 30 },
    
    // Dashboards
    { id: 2, label: 'Console', url: "/aurora/dashboard/", color: '#818cf8' },
    
    // External / Data Ecosystem
    { id: 3, label: 'Neo4j', url: "http://localhost:7474/browser/", color: '#f97316', target: '_blank' },
    
    // Admin & Security
    { id: 4, label: 'Django Admin', url: "/admin/", color: '#f43f5e' },
    
    // User Spaces
    { id: 5, label: 'HopeHub', url: "/aurora/", color: '#d946ef', target: '_blank' },
    
    // Logs & Tracking
    { id: 6, label: 'Journal', url: "/aurora/", color: '#10b981' },
    { id: 7, label: 'Daily Brief', url: "/aurora/daily_brief/", color: '#10b981' },

    // External Tools / Code Repo
    { id: 8, label: 'GitHub', url: "https://github.com", color: '#94a3b8', target: '_blank' }
]);

// Connect the cluster together
const edges = new vis.DataSet([
    { from: 1, to: 2 },
    { from: 1, to: 3 },
    { from: 1, to: 4 },
    { from: 1, to: 5 },
    { from: 1, to: 6 },
    { from: 1, to: 7 },
    { from: 1, to: 8 }
]);

const container = document.getElementById('network-container');
const data = { nodes: nodes, edges: edges };

const options = {
    nodes: {
        shape: 'dot',
        font: { color: '#ffffff', size: 16 },
        chosen: {
            node: function(values, id, selected, hovering) {
                if (hovering) {
                    values.size = values.size + 5;
                    values.borderColor = '#ffffff';
                    values.borderWidth = 2;
                }
            },
            label: function(values, id, selected, hovering) {
                if (hovering) {
                    values.color = '#ffffff';
                    values.mod = 'bold';
                }
            }
        }
    },
    edges: {
        color: '#475569',
        width: 2
    },
    interaction: {
        hover: true,
        zoomView: true
    }
};

const network = new vis.Network(container, data, options);

const MIN_ZOOM = 0.5; 
const MAX_ZOOM = 2.5; 

// Boundary threshold management
network.on("zoom", function (params) {
    const currentScale = network.getScale();
    let needsAdjustment = false;
    let targetScale = currentScale;

    if (currentScale < MIN_ZOOM) {
        targetScale = MIN_ZOOM;
        needsAdjustment = true;
    } else if (currentScale > MAX_ZOOM) {
        targetScale = MAX_ZOOM;
        needsAdjustment = true;
    }

    if (needsAdjustment) {
        network.setScale(targetScale);
    }

    network.moveTo({
        position: { x: 0, y: 0 },
        animation: false
    });
});

// Cursor UI triggers
network.on("hoverNode", function (params) {
    container.style.cursor = 'pointer';
});

network.on("blurNode", function (params) {
    container.style.cursor = 'default';
});

// Global navigation router
network.on("click", function (params) {
    if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
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
