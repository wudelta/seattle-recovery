// ======================================================================
// FILE: aurora/static/aurora/js/planning/state.js
// START: PLANNING_SHARED_STATE
// ======================================================================
(function(window) {
    "use strict";

    const Planning = window.AuroraPlanning = (
        window.AuroraPlanning || {}
    );

    const state = {
        initialized: false,
        endpoints: {},
        requests: {
            planning: null,
            project: null,
            initiative: null,
            phase: null,
            step: null,
        },
        users: [],
        activeProjectSlug: null,
        activeProject: null,
        activeInitiativeId: null,
        activeInitiative: null,
    };

    Planning.state = {
        isInitialized: function() {
            return state.initialized;
        },

        markInitialized: function() {
            state.initialized = true;
        },

        getEndpoints: function() {
            return state.endpoints;
        },

        setEndpoints: function(endpoints) {
            state.endpoints = endpoints || {};
        },

        getRequest: function(requestName) {
            return state.requests[requestName] || null;
        },

        setRequest: function(requestName, request) {
            if (!Object.prototype.hasOwnProperty.call(
                state.requests,
                requestName
            )) {
                throw new Error(
                    `Unknown Planning request type: ${requestName}`
                );
            }

            state.requests[requestName] = request || null;
        },

        getUsers: function() {
            return state.users.slice();
        },

        setUsers: function(users) {
            state.users = Array.isArray(users)
                ? users.slice()
                : [];
        },

        getActiveProjectSlug: function() {
            return state.activeProjectSlug;
        },

        setActiveProjectSlug: function(projectSlug) {
            state.activeProjectSlug = projectSlug || null;
        },

        getActiveProject: function() {
            return state.activeProject;
        },

        setActiveProject: function(project) {
            state.activeProject = project || null;
            state.activeProjectSlug = (
                project && project.slug
                ? project.slug
                : null
            );
        },

        clearActiveProject: function() {
            state.activeProjectSlug = null;
            state.activeProject = null;
        },

        getActiveInitiativeId: function() {
            return state.activeInitiativeId;
        },

        setActiveInitiativeId: function(initiativeId) {
            state.activeInitiativeId = initiativeId || null;
        },

        getActiveInitiative: function() {
            return state.activeInitiative;
        },

        setActiveInitiative: function(initiative) {
            state.activeInitiative = initiative || null;
        },

        clearActiveInitiative: function() {
            state.activeInitiativeId = null;
            state.activeInitiative = null;
        },
    };
})(window);
// ======================================================================
// END: PLANNING_SHARED_STATE
// ======================================================================