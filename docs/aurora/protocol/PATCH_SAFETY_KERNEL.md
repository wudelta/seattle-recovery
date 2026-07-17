# Aurora Patch Safety Kernel

Version: 1.0

## Purpose

This document defines the minimum patch-safety rules that apply to every Aurora code-editing session.

It is intentionally small enough to load at session start without creating significant context overhead.

The full refactoring protocol remains authoritative for larger implementation work.

---

## 1. Anchored Patches Are Complete Replacement Units

Every anchored patch replaces the entire region between its START and END markers.

A replacement patch must:

- preserve all unchanged code inside the existing region;
- include every function, class, constant, import, and comment that remains valid;
- remove code only when the removal is intentional and stated;
- parse or compile independently within the existing file;
- require no manual merging.

Never deliver only the changed lines inside an anchored replacement patch.

---

## 2. Do Not Mix Replacement and Insertion Instructions

An anchored patch must use one clear operation:

- replace an existing anchored region; or
- insert a new separately anchored region at an exact location.

Never say “add this beneath” while presenting the content as a replacement for an existing patch.

When inserting new code, identify the exact surrounding anchor or symbol.

---

## 3. Symbol Preservation Check

Before delivering a replacement patch, compare the current region with the proposed region.

Account for all existing:

- imports;
- constants;
- classes;
- methods;
- functions;
- properties;
- signal receivers;
- command arguments.

Any symbol missing from the proposed patch must be deliberately removed and explicitly identified.

Unexplained symbol loss is a patch failure.

---

## 4. Patch Boundary Check

Before delivery, verify:

- the FILE path is correct;
- PATCH numbering is correct;
- START and END headings match;
- the replacement boundary is neither broader nor narrower than intended;
- neighboring patch regions are not included;
- indentation remains valid at the insertion point.

---

## 5. Delivery Language

Use explicit language:

- “Replace the current PATCH X OF Y with:”
- “Insert this new patch immediately after:”
- “Delete this file entirely:”

Do not use ambiguous instructions such as:

- “add this somewhere below”;
- “update this section”;
- “include this method”;
- “merge this into the existing patch.”

---

## 6. Validation

After each patch:

1. run the smallest relevant validation command;
2. stop;
3. review the result;
4. continue only after explicit approval.

A passing system check does not prove behavioral correctness. Run a focused behavioral validation when the patch changes runtime behavior.

---

## 7. Governing Rule

When speed conflicts with patch completeness, preserve completeness.

A smaller complete patch is better than a faster partial patch.