# Aurora Production Blueprint Backlog

## 1. Incremental Refactoring Protocol (The "Go" Loop)
When Delta feeds the AI a file to refactor, upgrade, or extend, the engine must never return the entire file or multiple patches at once. The engine must strictly parse and deliver the update using the following conversational loop:
1. **The Partition Task**: Break the code updates down into highly localized, un-nested Surgical Block Anchor patches (e.g., `PATCH 1 OF X`, `PATCH 2 OF X`).
2. **The Single-Block Lock**: Deliver exactly **one single block** (e.g., `PATCH 1 OF X`) in the response window.
3. **The Yield Block**: Immediately halt output generation, provide a brief summary of what that specific patch modifies, and wait for Delta's confirmation.
4. **The Step Signal**: The AI must not output the next sequential patch until Delta explicitly enters the text variable keyword: **"go"**.
5. **Numbering Continuity Retention**: When returning patches for a file containing pre-existing numbered blocks, the engine must strictly preserve the file's original master index layout numbering (e.g., matching `PATCH 4 OF 5`) to prevent pipeline parsing offsets.

## 2. Refactoring & Code Delivery Standards
1. **Modification Trimming**: When refactoring or delivering codebase updates, only return patches that contain active modifications. Do not output unedited code blocks.
2. **Line Count Limits**: Keep individual code chunks under 100 lines of code whenever possible, with a strict maximum limit ceiling of 200 lines per patch.
