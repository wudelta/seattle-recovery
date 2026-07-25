// ======================================================================
// FILE: aurora/static/aurora/js/planning/data.js
// START: PLANNING_DATA_LOADER
// ======================================================================
(function(window, $) {
    "use strict";

    const Planning = window.AuroraPlanning = (
        window.AuroraPlanning || {}
    );

    const state = Planning.state;
    const workspace = Planning.workspace;
    const renderers = Planning.renderers;

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

        const requestData = {};

        if (!endpoint) {
            workspace.showError(
                "The planning endpoint was not supplied by Aurora Console."
            );
            return;
        }

        if (requestedProjectSlug) {
            requestData.project = requestedProjectSlug;
        }

        if (requestedInitiativeId) {
            requestData.initiative = requestedInitiativeId;
        }

        const existingRequest = state.getRequest("planning");

        if (existingRequest) {
            existingRequest.abort();
        }

        workspace.setLoadingState(true);

        $("#planning-error-state").addClass("d-none");

        $("#planning-empty-state")
            .addClass("d-none")
            .removeClass("d-flex");

        const request = $.ajax({
            url: endpoint,
            method: "GET",
            dataType: "json",
            data: requestData,
        })
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

                renderers.renderPlanningPayload(response);
            })
            .fail(function(xhr, textStatus) {
                if (textStatus === "abort") {
                    return;
                }

                let message = "The planning request failed.";

                if (
                    xhr.responseJSON
                    && xhr.responseJSON.error
                ) {
                    message = xhr.responseJSON.error;
                } else if (xhr.status) {
                    message += ` HTTP ${xhr.status}.`;
                }

                workspace.showError(message);
            })
            .always(function() {
                state.setRequest("planning", null);
                workspace.setLoadingState(false);
            });

        state.setRequest("planning", request);
    }

    Planning.data = {
        loadPlanningData: loadPlanningData,
    };
})(window, jQuery);
// ======================================================================
// END: PLANNING_DATA_LOADER
// ======================================================================