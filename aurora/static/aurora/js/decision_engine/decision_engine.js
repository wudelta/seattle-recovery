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

    function sourceKey(item) {
        return `${item.source_type}:${item.source_id}`;
    }

    function renderClassificationItem(item, actionLabel, onAction) {
        const card = renderItem(item);
        const actions = el(
            "div",
            "decision-engine-classification-actions"
        );
        const button = el(
            "button",
            "btn btn-sm btn-outline-info",
            actionLabel
        );

        button.type = "button";
        button.addEventListener("click", onAction);

        actions.appendChild(button);
        card.appendChild(actions);

        return card;
    }

    function getCsrfToken() {
        const cookie = document.cookie
            .split(";")
            .map(part => part.trim())
            .find(part => part.startsWith("csrftoken="));

        if (cookie) {
            return decodeURIComponent(
                cookie.slice("csrftoken=".length)
            );
        }

        const formToken = document.querySelector(
            '[name="csrfmiddlewaretoken"]'
        );

        return formToken?.value || "";
    }

    function renderSelectedClassificationItem(
        item,
        confirmedKeys,
        onReturn,
        onConfirmationChange
    ) {
        const key = sourceKey(item);
        const card = renderItem(item);
        const confirmation = el(
            "label",
            "decision-engine-scope-confirmation"
        );
        const checkbox = document.createElement("input");
        const confirmationText = el(
            "span",
            "",
            "I confirm this entire intake item belongs to this one body of work."
        );
        const actions = el(
            "div",
            "decision-engine-classification-actions"
        );
        const returnButton = el(
            "button",
            "btn btn-sm btn-outline-info",
            "Return"
        );

        checkbox.type = "checkbox";
        checkbox.checked = confirmedKeys.has(key);
        checkbox.addEventListener("change", function() {
            onConfirmationChange(checkbox.checked);
        });

        returnButton.type = "button";
        returnButton.addEventListener("click", onReturn);

        confirmation.appendChild(checkbox);
        confirmation.appendChild(confirmationText);
        card.appendChild(confirmation);
        actions.appendChild(returnButton);
        card.appendChild(actions);

        return card;
    }

    window.initDecisionEngineConsole = function(systemEndpoints) {
        const root = document.getElementById("decision-engine-console");

        if (!root || root.dataset.initialized === "true") {
            return;
        }

        root.dataset.initialized = "true";

        const endpoint = systemEndpoints.decision_engine_endpoint;
        const commitEndpoint =
            systemEndpoints.decision_engine_commit_endpoint;
        const refresh = document.getElementById("decision-engine-refresh");
        const reviewCommit = document.getElementById(
            "decision-engine-review-commit"
        );
        const actionDialog = window.AuroraActionDialog;
        const commitContent = document.getElementById(
            "decision-engine-commit-content"
        );
        const navButtons = Array.from(
            root.querySelectorAll("[data-decision-engine-view]")
        );
        const workspaces = Array.from(
            root.querySelectorAll("[data-decision-engine-workspace]")
        );

        if (!actionDialog || !commitContent) {
            throw new Error(
                "Decision Engine Review & Commit requires Shared UI ActionDialog."
            );
        }

        let currentView = DEFAULT_VIEW;
        let latestItems = [];
        const selectedKeys = new Set();
        const confirmedKeys = new Set();

        function renderClassification() {
            const available = document.getElementById(
                "decision-engine-available-items"
            );
            const selected = document.getElementById(
                "decision-engine-selected-items"
            );

            if (!available || !selected) return;

            available.replaceChildren();
            selected.replaceChildren();

            const currentKeys = new Set(
                latestItems.map(item => sourceKey(item))
            );

            Array.from(selectedKeys).forEach(key => {
                if (!currentKeys.has(key)) {
                    selectedKeys.delete(key);
                    confirmedKeys.delete(key);
                }
            });

            const availableItems = [];
            const selectedItems = [];

            latestItems.forEach(item => {
                if (selectedKeys.has(sourceKey(item))) {
                    selectedItems.push(item);
                } else {
                    availableItems.push(item);
                }
            });

            text(
                "decision-engine-available-count",
                availableItems.length
            );
            text(
                "decision-engine-selected-count",
                selectedItems.length
            );
            if (reviewCommit) {
                reviewCommit.disabled = selectedItems.length === 0;
            }

            if (!availableItems.length) {
                available.appendChild(
                    el(
                        "div",
                        "decision-engine-empty",
                        "No authorized intake available."
                    )
                );
            } else {
                availableItems.forEach(item => {
                    available.appendChild(
                        renderClassificationItem(
                            item,
                            "Select",
                            function() {
                                selectedKeys.add(sourceKey(item));
                                renderClassification();
                            }
                        )
                    );
                });
            }

            if (!selectedItems.length) {
                selected.appendChild(
                    el(
                        "div",
                        "decision-engine-empty",
                        "No intake selected for action."
                    )
                );
            } else {
                selectedItems.forEach(item => {
                    selected.appendChild(
                        renderSelectedClassificationItem(
                            item,
                            confirmedKeys,
                            function() {
                                const key = sourceKey(item);
                                selectedKeys.delete(key);
                                confirmedKeys.delete(key);
                                renderClassification();
                            },
                            function(isConfirmed) {
                                const key = sourceKey(item);
                                if (isConfirmed) {
                                    confirmedKeys.add(key);
                                } else {
                                    confirmedKeys.delete(key);
                                }
                            }
                        )
                    );
                });
            }
        }

        function openCommitDialog() {
            const selectedCount = selectedKeys.size;

            if (!selectedCount) return;

            const title = document.getElementById(
                "decision-engine-work-title"
            );
            const summary = selectedCount === 1
                ? "1 reviewed intake item will be committed to one body of work."
                : `${selectedCount} reviewed intake items will be committed `
                    + "to one body of work.";

            actionDialog.open({
                title: "Review & Commit Selected Intake",
                summary,
                contentNode: commitContent,
                status: "Selection remains transient until explicit commit.",
                secondaryLabel: "Cancel",
                primaryLabel: "Commit Selected",
                onPrimary: commitSelectedIntake,
                initialFocus: title
            });
        }

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

                latestItems = Array.isArray(payload.items)
                    ? payload.items
                    : [];

                render(payload);
                renderClassification();

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

        async function commitSelectedIntake() {
            const title = document.getElementById(
                "decision-engine-work-title"
            );
            const description = document.getElementById(
                "decision-engine-work-description"
            );
            const reason = document.getElementById(
                "decision-engine-work-reason"
            );
            const selectedItems = latestItems.filter(
                item => selectedKeys.has(sourceKey(item))
            );

            if (!selectedItems.length) {
                actionDialog.setStatus(
                    "Select at least one intake item before commit."
                );
                return;
            }

            if (
                !title
                || !description
                || !reason
                || !title.value.trim()
                || !description.value.trim()
                || !reason.value.trim()
            ) {
                actionDialog.setStatus(
                    "Title, description, and commit reason are required."
                );
                return;
            }

            const sources = selectedItems.map(item => ({
                source_type: item.source_type,
                source_id: item.source_id,
                scope_confirmed: confirmedKeys.has(sourceKey(item))
            }));

            if (sources.some(source => source.scope_confirmed !== true)) {
                actionDialog.setStatus(
                    "Confirm every selected intake item belongs entirely to "
                    + "this one body of work before commit."
                );
                return;
            }

            actionDialog.setStatus(
                "Committing selected intake..."
            );

            try {
                const response = await fetch(commitEndpoint, {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCsrfToken()
                    },
                    body: JSON.stringify({
                        title: title.value.trim(),
                        description: description.value.trim(),
                        reason: reason.value.trim(),
                        sources: sources
                    })
                });

                const payload = await response.json();
                if (
                    !response.ok
                    || payload.status !== "SUCCESS"
                ) {
                    throw new Error(
                        payload.message
                        || "Decision Engine commit failed."
                    );
                }

                selectedKeys.clear();
                confirmedKeys.clear();
                title.value = "";
                description.value = "";
                reason.value = "";
                await loadInbox();

                actionDialog.setStatus(
                    `Committed DecisionEngineWork #${payload.work.id}.`
                );
                actionDialog.setSecondaryLabel("Close");
            } catch (error) {
                actionDialog.setStatus(
                    `Commit error: ${error.message}`
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

        if (reviewCommit) {
            reviewCommit.addEventListener(
                "click",
                openCommitDialog
            );
        }

        showView(DEFAULT_VIEW);
        loadInbox();
    };
})();

// ======================================================================
// END: DECISION_ENGINE_SUBCONSOLE_CLIENT
// ======================================================================
