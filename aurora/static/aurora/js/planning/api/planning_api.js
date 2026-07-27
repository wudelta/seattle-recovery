// ======================================================================
// FILE: aurora/static/aurora/js/planning/api/planning_api.js
// START: PLANNING_API_CLIENT
// ======================================================================
(function(window, $) {
    "use strict";

    const Planning = window.AuroraPlanning = (
        window.AuroraPlanning || {}
    );

    Planning.api = Planning.api || {};

    function fetchPlanningData(endpoint, requestData) {
        return $.ajax({
            url: endpoint,
            method: "GET",
            dataType: "json",
            data: requestData || {},
        });
    }

    Planning.api.planning = {
        fetch: fetchPlanningData,
    };
})(window, jQuery);
// ======================================================================
// END: PLANNING_API_CLIENT
// ======================================================================