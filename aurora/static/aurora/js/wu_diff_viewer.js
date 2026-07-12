// ======================================================================
// FILE: aurora/static/aurora/js/wu_diff_viewer.js (PATCH 1 OF 1)
// START: WU_ISOLATED_MONACO_DIFF_VIEWER
// ======================================================================
(function () {
    "use strict";

    let diffEditor = null;
    let proposedModel = null;
    let currentModel = null;

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

    function ensureEditor() {
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
        ensureEditor();

        if (!diffEditor) {
            return;
        }

        disposeModels();

        const language = payload.language || "plaintext";

        proposedModel = monaco.editor.createModel(
            payload.proposed_content || "",
            language
        );

        currentModel = monaco.editor.createModel(
            payload.original_content || "",
            language
        );

        diffEditor.setModel({
            original: proposedModel,
            modified: currentModel
        });
    }

    function show(payload) {
        const slider = getSlider();

        if (!slider) {
            return;
        }

        const filePath = document.getElementById("wu-review-file-path");

        if (filePath) {
            filePath.textContent = payload.file_path || "Pending code review";
        }

        loadModels(payload);

        slider.style.transform = "translateX(-100%)";
        slider.setAttribute("aria-hidden", "false");

        requestAnimationFrame(function () {
            if (diffEditor) {
                diffEditor.layout();
            }
        });
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
        const closeButton = document.getElementById("wu-review-close-btn");
        const rejectButton = document.getElementById("wu-review-reject-btn");

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

    document.addEventListener("DOMContentLoaded", function () {
        bindControls();
    });

    window.WuDiffViewer = {
        show: show,
        hide: hide,
        showDemo: showDemo
    };
})();
// ======================================================================
// END: WU_ISOLATED_MONACO_DIFF_VIEWER (PATCH 1 OF 1)
// ======================================================================