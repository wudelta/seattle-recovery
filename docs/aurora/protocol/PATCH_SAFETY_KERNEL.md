# ======================================================================
# FILE: docs/aurora/protocol/PATCH_SAFETY_KERNEL.md (PATCH 1 OF 3)
# START: TITLE_PURPOSE_AND_FOUNDATIONAL_RULES
# ======================================================================

# Aurora Patch Safety Kernel

**Version: 2.0**

---

# Purpose

The Patch Safety Kernel defines the minimum engineering rules that apply to every Aurora implementation session.

It is intentionally concise so it can be loaded at the beginning of development without significant context overhead.

The full Aurora Refactoring Protocol remains the authoritative engineering standard.

The Safety Kernel exists to answer one question:

> **"How do we avoid delivering a bad patch?"**

---

# 1. Human-Safe Editing

The objective of every patch is to minimize opportunities for both AI mistakes and human editing mistakes.

Whenever practical:

- replace complete anchored regions;
- avoid manual editing;
- eliminate partial merge operations;
- provide deterministic copy-and-paste replacements.

The safest patch is the smallest complete replacement unit—not necessarily the patch with the fewest changed lines.

---

# 2. Architectural Replacement Units

Anchored patches represent logical architectural units.

Whenever practical, an anchored region should contain one cohesive responsibility such as:

- imports and configuration;
- one complete function;
- one complete class;
- one API handler;
- one utility group;
- one documentation section.

Do not split a logical implementation simply to satisfy an arbitrary line-count preference.

Architecture determines anchor boundaries.

---

# 3. Complete Replacement Rule

Every anchored patch replaces the entire region between its START and END markers.

A replacement patch must:

- preserve all unchanged content inside its boundaries;
- include every remaining symbol belonging to the region;
- remain syntactically complete;
- require no manual merging;
- be immediately usable as delivered.

Never deliver only the changed lines from an anchored replacement region.

# ======================================================================
# END: TITLE_PURPOSE_AND_FOUNDATIONAL_RULES (PATCH 1 OF 3)
# ======================================================================

# ======================================================================
# FILE: docs/aurora/protocol/PATCH_SAFETY_KERNEL.md (PATCH 2 OF 3)
# START: PATCH_VERIFICATION_AND_DELIVERY_DISCIPLINE
# ======================================================================

# 4. Inspect Before Modifying

Never generate a replacement patch for code that has not been inspected.

Before implementation:

- verify the repository-relative file path;
- inspect the current source;
- understand the surrounding anchor boundaries;
- identify the intended modification.

Never invent unseen code.

When uncertainty exists, request the current source before proceeding.

---

# 5. Preserve Patch Topology

Anchored regions are part of the repository architecture.

A replacement patch inherits the identity of the patch it replaces.

Verify:

- FILE path;
- PATCH numbering;
- START heading;
- END heading;
- replacement boundaries.

Do not renumber, split, merge, or eliminate anchored regions unless the implementation explicitly changes the file's anchor topology.

When topology changes are required, deliver the complete revised topology.

---

# 6. Symbol Preservation

Before delivering a replacement patch, account for every symbol contained within the current anchor.

Examples include:

- imports;
- constants;
- decorators;
- classes;
- methods;
- functions;
- configuration;
- exported symbols.

Any omitted symbol must be intentionally removed.

Unexplained symbol loss is a patch failure.

---

# 7. Explicit Delivery Instructions

Every patch should describe exactly one editing operation.

Examples:

- "Replace the current PATCH 2 OF 5 with:"
- "Insert this new PATCH immediately after PATCH 3 OF 6."
- "Delete this file."

Avoid ambiguous instructions such as:

- "add this below";
- "merge this into";
- "update this section";
- "include the following."

The required editing operation should never require interpretation.

# ======================================================================
# END: PATCH_VERIFICATION_AND_DELIVERY_DISCIPLINE (PATCH 2 OF 3)
# ======================================================================

# ======================================================================
# FILE: docs/aurora/protocol/PATCH_SAFETY_KERNEL.md (PATCH 3 OF 3)
# START: VALIDATION_AND_GOVERNING_PRINCIPLES
# ======================================================================

# 8. Validate Before Continuing

After each patch:

1. perform the smallest validation capable of confirming the intended change;
2. review the result;
3. stop;
4. continue only after explicit approval.

A successful syntax check confirms only that the code is structurally valid.

Whenever runtime behavior changes, perform an appropriate behavioral validation before considering the implementation complete.

---

# 9. The GO Loop

Every implementation follows the same review cycle:

```text
Inspect
    ↓
Plan
    ↓
Deliver One Complete Patch
    ↓
Validate
    ↓
Review
    ↓
GO
```

Do not skip review cycles.

Frequent validation and small recovery points are fundamental engineering practices, not optional workflow preferences.

---

# 10. Final Pre-Delivery Checklist

Before sending any patch, confirm all of the following:

□ The correct file was inspected.

□ The repository-relative path is correct.

□ The patch numbering matches the existing topology.

□ START and END anchors match the current file.

□ The replacement boundary is correct.

□ Every existing symbol has been accounted for.

□ The replacement is complete.

□ No manual merge is required.

□ The patch is syntactically valid.

□ The intended validation method has been identified.

If any item cannot be confidently answered, stop and resolve the uncertainty before delivering the patch.

---

# Governing Rule

When speed conflicts with safety, choose safety.

A complete, deterministic, and reviewable patch is always preferable to a faster patch that depends on manual editing, assumptions, or incomplete context.

The Safety Kernel exists to prevent implementation mistakes before they reach the repository.

# ======================================================================
# END: VALIDATION_AND_GOVERNING_PRINCIPLES (PATCH 3 OF 3)
# ======================================================================
