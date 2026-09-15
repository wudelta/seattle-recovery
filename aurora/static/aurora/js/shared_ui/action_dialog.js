// ======================================================================
// FILE: aurora/static/aurora/js/shared_ui/action_dialog.js
// START: SHARED_UI_ACTION_DIALOG_CLIENT
// ======================================================================

(function() {
    "use strict";

    const ROOT_ID = "shared-ui-action-dialog";
    const TITLE_ID = "shared-ui-action-dialog-title";
    const SUMMARY_ID = "shared-ui-action-dialog-summary";
    const CONTENT_ID = "shared-ui-action-dialog-content";
    const STATUS_ID = "shared-ui-action-dialog-status";
    const SECONDARY_ID = "shared-ui-action-dialog-secondary";
    const PRIMARY_ID = "shared-ui-action-dialog-primary";

    const FOCUSABLE_SELECTOR = [
        'a[href]',
        'button:not([disabled])',
        'input:not([disabled]):not([type="hidden"])',
        'select:not([disabled])',
        'textarea:not([disabled])',
        '[tabindex]:not([tabindex="-1"])'
    ].join(",");

    let previousFocus = null;
    let primaryHandler = null;
    let closeHandler = null;
    let primaryPending = false;
    let mountedContent = null;
    let mountedContentOrigin = null;
    let mountedContentNextSibling = null;

    function getRequiredNode(id) {
        const node = document.getElementById(id);

        if (!node) {
            throw new Error(
                `Shared UI ActionDialog is missing required node #${id}.`
            );
        }

        return node;
    }

    function nodes() {
        const root = getRequiredNode(ROOT_ID);

        return {
            root,
            surface: root.querySelector(".shared-ui-action-dialog__surface"),
            title: getRequiredNode(TITLE_ID),
            summary: getRequiredNode(SUMMARY_ID),
            content: getRequiredNode(CONTENT_ID),
            status: getRequiredNode(STATUS_ID),
            secondary: getRequiredNode(SECONDARY_ID),
            primary: getRequiredNode(PRIMARY_ID)
        };
    }

    function isOpen() {
        const root = document.getElementById(ROOT_ID);
        return Boolean(
            root
            && root.getAttribute("aria-hidden") === "false"
        );
    }

    function setOptionalText(node, value) {
        const text = value === undefined || value === null
            ? ""
            : String(value).trim();

        node.textContent = text;
        node.classList.toggle("d-none", !text);
    }

    function setStatus(message) {
        const {status} = nodes();
        setOptionalText(status, message);
    }

    function setPrimaryEnabled(enabled) {
        const {primary} = nodes();
        primary.disabled = primaryPending || enabled === false;
    }

    function setPrimaryLabel(label) {
        const {primary} = nodes();
        primary.textContent = String(label || "Continue");
    }

    function setSecondaryLabel(label) {
        const {secondary} = nodes();
        secondary.textContent = String(label || "Cancel");
    }

    function rememberContentOrigin(contentNode) {
        mountedContent = contentNode;
        mountedContentOrigin = contentNode?.parentNode || null;
        mountedContentNextSibling = contentNode?.nextSibling || null;
    }

    function restoreMountedContent() {
        if (!mountedContent) return;

        if (mountedContentOrigin) {
            if (
                mountedContentNextSibling
                && mountedContentNextSibling.parentNode === mountedContentOrigin
            ) {
                mountedContentOrigin.insertBefore(
                    mountedContent,
                    mountedContentNextSibling
                );
            } else {
                mountedContentOrigin.appendChild(mountedContent);
            }
        } else {
            mountedContent.remove();
        }

        mountedContent = null;
        mountedContentOrigin = null;
        mountedContentNextSibling = null;
    }

    function mountContent(contentNode) {
        const {content} = nodes();

        restoreMountedContent();
        content.replaceChildren();

        if (!contentNode) return;

        if (!(contentNode instanceof Node)) {
            throw new TypeError(
                "ActionDialog contentNode must be a DOM Node."
            );
        }

        rememberContentOrigin(contentNode);
        content.appendChild(contentNode);
    }

    function focusableNodes() {
        const {surface} = nodes();

        return Array.from(
            surface.querySelectorAll(FOCUSABLE_SELECTOR)
        ).filter(node => {
            return !node.hidden
                && node.getAttribute("aria-hidden") !== "true"
                && node.offsetParent !== null;
        });
    }

    function focusInitial(initialFocus) {
        let target = null;

        if (initialFocus instanceof HTMLElement) {
            target = initialFocus;
        } else if (typeof initialFocus === "string" && initialFocus.trim()) {
            target = nodes().surface.querySelector(initialFocus);
        }

        if (!target) {
            target = focusableNodes()[0] || nodes().surface;
        }

        target.focus();
    }

    function resetSharedState() {
        const {
            title,
            summary,
            status,
            secondary,
            primary
        } = nodes();

        title.textContent = "";
        setOptionalText(summary, "");
        setOptionalText(status, "");

        secondary.textContent = "Cancel";
        primary.textContent = "Continue";
        primary.disabled = false;

        primaryHandler = null;
        closeHandler = null;
        primaryPending = false;
    }

    function close(reason = "close") {
        if (!isOpen()) return;

        const {root} = nodes();
        const onClose = closeHandler;
        const focusTarget = previousFocus;

        root.setAttribute("aria-hidden", "true");

        restoreMountedContent();
        resetSharedState();

        previousFocus = null;

        if (
            focusTarget
            && typeof focusTarget.focus === "function"
            && document.contains(focusTarget)
        ) {
            focusTarget.focus();
        }

        if (typeof onClose === "function") {
            onClose({reason});
        }
    }

    function open(options = {}) {
        if (isOpen()) {
            close("replace");
        }

        const {
            root,
            title,
            summary,
            status,
            secondary,
            primary
        } = nodes();

        previousFocus = document.activeElement instanceof HTMLElement
            ? document.activeElement
            : null;

        title.textContent = String(options.title || "");
        setOptionalText(summary, options.summary);
        setOptionalText(status, options.status);

        secondary.textContent = String(
            options.secondaryLabel || "Cancel"
        );
        primary.textContent = String(
            options.primaryLabel || "Continue"
        );

        primaryHandler = typeof options.onPrimary === "function"
            ? options.onPrimary
            : null;
        closeHandler = typeof options.onClose === "function"
            ? options.onClose
            : null;

        primaryPending = false;
        primary.disabled = options.primaryEnabled === false;

        mountContent(options.contentNode || null);

        root.setAttribute("aria-hidden", "false");
        focusInitial(options.initialFocus);
    }

    async function invokePrimary() {
        if (primaryPending || typeof primaryHandler !== "function") {
            return;
        }

        const {primary} = nodes();

        primaryPending = true;
        primary.disabled = true;

        try {
            await primaryHandler();
        } finally {
            primaryPending = false;

            if (isOpen()) {
                primary.disabled = false;
            }
        }
    }

    function trapFocus(event) {
        const focusable = focusableNodes();

        if (!focusable.length) {
            event.preventDefault();
            nodes().surface.focus();
            return;
        }

        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        const active = document.activeElement;

        if (event.shiftKey && active === first) {
            event.preventDefault();
            last.focus();
            return;
        }

        if (!event.shiftKey && active === last) {
            event.preventDefault();
            first.focus();
        }
    }

    function handleKeydown(event) {
        if (!isOpen()) return;

        if (event.key === "Escape") {
            event.preventDefault();
            close("escape");
            return;
        }

        if (event.key === "Tab") {
            trapFocus(event);
        }
    }

    function initialize() {
        const {secondary, primary} = nodes();

        secondary.addEventListener(
            "click",
            () => close("secondary")
        );
        primary.addEventListener(
            "click",
            () => {
                invokePrimary().catch(error => {
                    console.error(
                        "Shared UI ActionDialog primary action failed.",
                        error
                    );
                });
            }
        );
        document.addEventListener("keydown", handleKeydown);
    }

    window.AuroraActionDialog = Object.freeze({
        open,
        close,
        isOpen,
        setStatus,
        setPrimaryEnabled,
        setPrimaryLabel,
        setSecondaryLabel
    });

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            initialize,
            {once: true}
        );
    } else {
        initialize();
    }
})();

// ======================================================================
// END: SHARED_UI_ACTION_DIALOG_CLIENT
// ======================================================================
