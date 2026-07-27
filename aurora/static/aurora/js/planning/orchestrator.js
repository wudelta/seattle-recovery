// ======================================================================
// FILE: aurora/static/aurora/js/planning/orchestrator.js
// START: PLANNING_DATA_LOADER
// ======================================================================
(function(window) {
    "use strict";

    const Planning = window.AuroraPlanning = (
        window.AuroraPlanning || {}
    );

    const state = Planning.state;
    const workspace = Planning.workspace;
    const planningApi = Planning.api.planning;
    const renderers = Planning.renderers;

    function buildRequestData(projectSlug, initiativeId) {
        const requestData = {};

        if (projectSlug) {
            requestData.project = projectSlug;
        }

        if (initiativeId) {
            requestData.initiative = initiativeId;
        }

        return requestData;
    }

    function resolveErrorMessage(xhr) {
        if (
            xhr.responseJSON
            && xhr.responseJSON.error
        ) {
            return xhr.responseJSON.error;
        }

        if (xhr.status) {
            return `The planning request failed. HTTP ${xhr.status}.`;
        }

        return "The planning request failed.";
    }

    function loadPlanningData(projectSlug, initiativeId) {
        const endpoints = state.getEndpoints();
        const endpoint = endpoints.planning_endpoint;

        const requestedProjectSlug = (
            projectSlug
            || state.getActiveProjectSlug()
            || ""
        );

        const requestedInitiativeId = (
            initiativeId
            || state.getActiveInitiativeId()
            || ""
        );

        if (!endpoint) {
            workspace.showError(
                "The planning endpoint was not supplied by Aurora Console."
            );
            return;
        }

        const existingRequest = state.getRequest("planning");

        if (existingRequest) {
            existingRequest.abort();
        }

        workspace.setLoadingState(true);

        const request = planningApi.fetch(
            endpoint,
            buildRequestData(
                requestedProjectSlug,
                requestedInitiativeId
            )
        )
            .done(function(response) {
                if (
                    !response
                    || response.status !== "success"
                ) {
                    workspace.showError(
                        "The planning endpoint returned an invalid response."
                    );
                    return;
                }

                renderers.workspace.renderPayload(response);
            })
            .fail(function(xhr, textStatus) {
                if (textStatus === "abort") {
                    return;
                }

                workspace.showError(
                    resolveErrorMessage(xhr)
                );
            })
            .always(function() {
                state.setRequest("planning", null);
                workspace.setLoadingState(false);
            });

        state.setRequest("planning", request);
    }

    Planning.orchestrator = {
        loadPlanningData: loadPlanningData,
    };
})(window);
// ======================================================================
// END: PLANNING_DATA_LOADER
// ======================================================================