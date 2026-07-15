# Final Baseline Regression Checklist

**Purpose**

This checklist validates that the Aurora AI Execution Platform baseline is production-ready before merging `feature/provider-abstraction` into `main`.

This is a manual smoke test intended to verify end-to-end behavior after the architectural refactor.

---

# 1. Wu Chat

Verify normal AI interaction.

* [ ] Normal conversation
* [ ] Multi-message conversation
* [ ] `[READ_FILE: path]` workflow
* [ ] Plain repository path detection
* [ ] Missing file handling
* [ ] Invalid repository path rejection

Expected result:

* Wu responds normally.
* Repository context loads correctly.
* Invalid paths are rejected safely.

---

# 2. Structured Patch Pipeline

Verify AI patch generation and validation.

* [ ] Valid structured patch
* [ ] Malformed patch rejection
* [ ] Truncated patch rejection
* [ ] Wrong target file rejection
* [ ] Multiple PATCH blocks rejected

Expected result:

* Only one valid structured patch is accepted.
* Invalid responses never reach the review stage.

---

# 3. Review Workflow

Verify Monaco review interface.

* [ ] Review slider opens
* [ ] Current source displayed correctly
* [ ] Proposed source displayed correctly
* [ ] Close button functions correctly
* [ ] Multiple open/close cycles
* [ ] No duplicate Monaco editors

Expected result:

* Review interface remains stable during repeated use.

---

# 4. Approval Workflow

Verify repository mutation safety.

* [ ] Approve performs exactly one repository write
* [ ] Reject performs no repository mutation
* [ ] Conflict detection prevents overwrite
* [ ] Pending → Applied transition
* [ ] Pending → Rejected transition
* [ ] Pending → Conflict transition

Expected result:

* Repository mutation occurs only after explicit approval.
* Conflicts are detected before writing.

---

# 5. Workspace Isolation

Verify editor independence.

* [ ] Anamod operates normally
* [ ] Wu Monaco viewer operates normally
* [ ] No editor interference
* [ ] Console loads correctly
* [ ] No JavaScript errors

Expected result:

* Wu and Anamod remain completely isolated.

---

# 6. Telemetry

Verify execution visibility.

* [ ] Provider displayed
* [ ] Model displayed
* [ ] Input token count
* [ ] Output token count
* [ ] Total token count
* [ ] Execution latency
* [ ] Provider errors displayed correctly

Expected result:

* Telemetry accurately reflects each AI execution.

---

# 7. Startup & Stability

Verify application startup behavior.

* [ ] `daurora-cmd check`
* [ ] Daphne restart
* [ ] Fresh browser load
* [ ] Browser refresh
* [ ] New chat session
* [ ] Existing chat session

Expected result:

* Aurora starts cleanly with no regressions.

---

# 8. Release Readiness

Complete before merging.

* [ ] Temporary diagnostics removed
* [ ] Documentation updated
* [ ] PROJECT_STATE.yaml reviewed
* [ ] MIGRATION_CHECKLIST.md reviewed
* [ ] SESSION_LOG.md updated
* [ ] Git working tree clean
* [ ] Final regression passed
* [ ] Merge approved

---

# Exit Criteria

The Aurora baseline is considered complete when:

* All checklist items pass.
* No critical or high-severity defects remain.
* The Wu-assisted engineering workflow has been validated end-to-end.
* The provider abstraction is functioning correctly.
* The repository mutation workflow is source-verified and approval-gated.
* The branch is ready for merge into `main`.

---

**Completion Milestone**

Upon successful completion of this checklist, Aurora transitions from platform construction to platform utilization. Subsequent development should prioritize building HopeHub and shared capabilities using the completed Aurora AI execution platform rather than expanding Aurora's baseline architecture.
