// ======================================================================
// FILE: aurora/static/aurora/js/decision_engine/decision_engine.js
// START: DECISION_ENGINE_SUBCONSOLE_CLIENT
// ======================================================================

(function() {
    "use strict";

    const DEFAULT_VIEW = "inbox";

    function text(id, value) {
        const node = document.getElementById(id);
        if (node) node.textContent = String(value);
    }

    function el(tag, className, value) {
        const node = document.createElement(tag);
        if (className) node.className = className;
        if (value !== undefined && value !== null) {
            node.textContent = String(value);
        }
        return node;
    }

    function when(value) {
        const date = new Date(value);
        return Number.isNaN(date.getTime())
            ? String(value || "")
            : date.toLocaleString();
    }

    function provenance(record) {
        if (!record.originating_step) {
            return "No Planning Step provenance";
        }

        const parts = [];

        if (record.project) parts.push(record.project.title);
        if (record.initiative) parts.push(record.initiative.title);
        if (record.phase) parts.push(record.phase.title);

        parts.push(record.originating_step.title);

        return parts.join(" → ");
    }

    function renderItem(item) {
        const record = item.source_record;
        const card = el("article", "decision-engine-item");

        if (item.source_type === "DELTA_NOTE") {
            card.appendChild(
                el(
                    "div",
                    "decision-engine-source",
                    `DELTA NOTE #${record.note_id}`
                )
            );
            card.appendChild(
                el("div", "decision-engine-body", record.text)
            );
            card.appendChild(
                el(
                    "div",
                    "decision-engine-meta",
                    `${record.author} • ${when(record.created_at)}`
                )
            );

            return card;
        }

        card.appendChild(
            el(
                "div",
                "decision-engine-source",
                `ENGINEERING FINDING #${record.finding_id}`
            )
        );
        card.appendChild(
            el(
                "div",
                "decision-engine-classification",
                `${record.category} • ${record.blocking_classification}`
            )
        );
        card.appendChild(
            el(
                "div",
                "decision-engine-body",
                record.observed_condition
            )
        );
        card.appendChild(
            el(
                "div",
                "decision-engine-meta",
                provenance(record)
            )
        );
        card.appendChild(
            el(
                "div",
                "decision-engine-meta",
                `${record.discovered_by} • ${when(record.created_at)}`
            )
        );

        return card;
    }

    function render(payload) {
        const counts = payload.counts || {};
        const items = Array.isArray(payload.items)
            ? payload.items
            : [];

        text("decision-engine-total-count", counts.total || 0);
        text("decision-engine-delta-count", counts.delta_notes || 0);
        text(
            "decision-engine-finding-count",
            counts.engineering_findings || 0
        );

        const inbox = document.getElementById("decision-engine-inbox");

        if (!inbox) return;

        inbox.replaceChildren();

        if (!items.length) {
            inbox.appendChild(
                el(
                    "div",
                    "decision-engine-empty",
                    "No raw organizational inbox items."
                )
            );
            return;
        }

        items.forEach(
            item => inbox.appendChild(renderItem(item))
        );
    }

    window.initDecisionEngineConsole = function(systemEndpoints) {
        const root = document.getElementById("decision-engine-console");

        if (!root || root.dataset.initialized === "true") {
            return;
        }

        root.dataset.initialized = "true";

        const endpoint = systemEndpoints.decision_engine_endpoint;
        const refresh = document.getElementById("decision-engine-refresh");
        const navButtons = Array.from(
            root.querySelectorAll("[data-decision-engine-view]")
        );
        const workspaces = Array.from(
            root.querySelectorAll("[data-decision-engine-workspace]")
        );

        let currentView = DEFAULT_VIEW;

        function showView(viewName) {
            const target = workspaces.find(
                workspace =>
                    workspace.dataset.decisionEngineWorkspace === viewName
            );

            if (!target) {
                throw new Error(
                    `Unknown Decision Engine view: ${viewName}`
                );
            }

            currentView = viewName;

            workspaces.forEach(workspace => {
                const isActive =
                    workspace.dataset.decisionEngineWorkspace === currentView;

                workspace.classList.toggle("d-none", !isActive);
                workspace.setAttribute(
                    "aria-hidden",
                    isActive ? "false" : "true"
                );
            });

            navButtons.forEach(button => {
                const isActive =
                    button.dataset.decisionEngineView === currentView;

                button.classList.toggle("active", isActive);
                button.setAttribute(
                    "aria-selected",
                    isActive ? "true" : "false"
                );
            });
        }

        async function loadInbox() {
            text(
                "decision-engine-status",
                "Loading raw inbox..."
            );

            try {
                const response = await fetch(endpoint, {
                    method: "GET",
                    credentials: "same-origin",
                    headers: {
                        "Accept": "application/json"
                    }
                });

                const payload = await response.json();

                if (
                    !response.ok
                    || payload.status !== "SUCCESS"
                ) {
                    throw new Error(
                        payload.message
                        || "Decision Engine inbox load failed."
                    );
                }

                render(payload);
                text(
                    "decision-engine-status",
                    "Read-only organizational evidence."
                );
            } catch (error) {
                text(
                    "decision-engine-status",
                    `Inbox error: ${error.message}`
                );
            }
        }

        navButtons.forEach(button => {
            button.addEventListener("click", function() {
                showView(
                    button.dataset.decisionEngineView
                );
            });
        });

        if (refresh) {
            refresh.addEventListener("click", loadInbox);
        }

        showView(DEFAULT_VIEW);
        loadInbox();
    };
})();

// ======================================================================
// END: DECISION_ENGINE_SUBCONSOLE_CLIENT
// ======================================================================
