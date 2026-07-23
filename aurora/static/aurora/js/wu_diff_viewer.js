// ======================================================================
// FILE: aurora/static/aurora/js/wu_diff_viewer.js (PATCH 1 OF 1)
// START: WU_ISOLATED_MONACO_DIFF_VIEWER
// ======================================================================
(function () {
    "use strict";

    let diffEditor = null;
    let proposedModel = null;
    let currentModel = null;
    let pendingPayload = null;
    let monacoLoading = false;

    function getSlider() {
        return document.getElementById("wu-code-review-slider");
    }

    function disposeModels() {
        if (proposedModel) {
            proposedModel.dispose();
            proposedModel = null;
        }

        if (currentModel) {
            currentModel.dispose();
            currentModel = null;
        }
    }

    function createEditor() {
        const viewport = document.getElementById("wu-code-diff-viewport");

        if (!viewport || diffEditor || typeof monaco === "undefined") {
            return;
        }

        diffEditor = monaco.editor.createDiffEditor(viewport, {
            automaticLayout: true,
            readOnly: true,
            renderSideBySide: true,
            originalEditable: false,
            minimap: {
                enabled: false
            }
        });
    }

    function loadModels(payload) {
        createEditor();

        if (!diffEditor || typeof monaco === "undefined") {
            return;
        }

        disposeModels();

        const language = payload.language || "plaintext";

        currentModel = monaco.editor.createModel(
            payload.original_content || "",
            language
        );

        proposedModel = monaco.editor.createModel(
            payload.proposed_content || "",
            language
        );

        diffEditor.setModel({
            original: currentModel,
            modified: proposedModel
        });

        requestAnimationFrame(function () {
            diffEditor.layout();
        });
    }

    function loadMonaco(payload) {
        pendingPayload = payload;

        if (typeof monaco !== "undefined") {
            loadModels(pendingPayload);
            pendingPayload = null;
            return;
        }

        if (monacoLoading) {
            return;
        }

        if (typeof require !== "function") {
            console.error(
                "[WuDiffViewer] Monaco AMD loader is unavailable."
            );
            return;
        }

        monacoLoading = true;

        require(
            ["vs/editor/editor.main"],
            function () {
                monacoLoading = false;

                if (pendingPayload) {
                    loadModels(pendingPayload);
                    pendingPayload = null;
                }
            },
            function (error) {
                monacoLoading = false;
                console.error(
                    "[WuDiffViewer] Monaco failed to load.",
                    error
                );
            }
        );
    }

    function show(payload) {
        const slider = getSlider();

        if (!slider) {
            return;
        }

        const filePath = document.getElementById("wu-review-file-path");

        if (filePath) {
            filePath.textContent =
                payload.file_path || "Pending code review";
        }

        slider.style.transform = "translateX(-100%)";
        slider.setAttribute("aria-hidden", "false");

        loadMonaco(payload);
    }

    function hide() {
        const slider = getSlider();

        if (!slider) {
            return;
        }

        slider.style.transform = "translateX(0)";
        slider.setAttribute("aria-hidden", "true");
    }

    function bindControls() {
        const closeButton = document.getElementById(
            "wu-review-close-btn"
        );

        const rejectButton = document.getElementById(
            "wu-review-reject-btn"
        );

        if (closeButton) {
            closeButton.addEventListener("click", hide);
        }

        if (rejectButton) {
            rejectButton.addEventListener("click", hide);
        }
    }

    function showDemo() {
        show({
            file_path: "aurora/api/content_api.py",
            language: "python",
            original_content:
                "def load_content():\n" +
                "    return Content.objects.all()\n",
            proposed_content:
                "def load_content():\n" +
                "    return Content.objects.order_by(\"title\")\n"
        });
    }

    document.addEventListener("DOMContentLoaded", bindControls);

    window.WuDiffViewer = {
        show: show,
        hide: hide,
        showDemo: showDemo
    };
})();
// ======================================================================
// END: WU_ISOLATED_MONACO_DIFF_VIEWER (PATCH 1 OF 1)
// ======================================================================