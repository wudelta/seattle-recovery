# Aurora

Aurora is the local-first engineering console and AI orchestration environment used to design, build, validate, and maintain HopeHub and related software projects.

## Project Status

- **Slug:** `aurora`
- **Status:** Active
- **Position:** 1
- **Active:** Yes

## Initiative 1: Decision Engine Planning MVP

Create a database-backed planning system that allows structured engineering work to be defined, organized, estimated, revised, imported, exported, and tracked through Projects, Initiatives, Phases, and Steps.

**Status:** Active

### Phase 1: Planning Domain Model

Establish the persisted planning hierarchy and runtime user position required by the Decision Engine.

**Status:** Completed

#### Step 1: Create Project model

Add the top-level planning container used to separate Aurora, HopeHub, and future projects.

- **Status:** Completed
- **Risk:** Low
- **Estimated effort:** 60 minutes
- **Estimate confidence:** High

**Validation**

Projects can be created and retrieved with unique slugs.

#### Step 2: Associate Initiatives with Projects

Make each Initiative a child of one Project with ordered sibling positions.

- **Status:** Completed
- **Risk:** Medium
- **Estimated effort:** 45 minutes
- **Estimate confidence:** High

**Risk details**

Existing test Initiative records were intentionally disposable.

**Validation**

Initiative queries are scoped by project.

#### Step 3: Preserve Phase and Step hierarchy

Retain ordered Phases beneath Initiatives and ordered Steps beneath Phases.

- **Status:** Completed
- **Risk:** Low
- **Estimated effort:** 45 minutes
- **Estimate confidence:** High

**Validation**

The complete Project, Initiative, Phase, and Step hierarchy can be persisted.

#### Step 4: Add UserPosition navigation state

Persist the Project, Initiative, Phase, and Step currently selected by each user.

- **Status:** Completed
- **Risk:** Medium
- **Estimated effort:** 60 minutes
- **Estimate confidence:** Medium

**Validation**

A user can retain their current planning location independently of planning lifecycle statuses.

### Phase 2: Planning CRUD Interface

Provide database-backed creation and selection controls for the complete planning hierarchy inside Aurora Console.

**Status:** Completed

#### Step 1: Implement Project CRUD foundation

Add API and interface support for creating and selecting Projects.

- **Status:** Completed
- **Risk:** Low
- **Estimated effort:** 90 minutes
- **Estimate confidence:** High

**Validation**

A Project can be created and selected in Aurora Console.

#### Step 2: Filter Initiatives by selected Project

Populate the Initiative selector using only Initiatives that belong to the selected Project.

- **Status:** Completed
- **Risk:** Medium
- **Estimated effort:** 90 minutes
- **Estimate confidence:** High

**Validation**

Changing Projects refreshes the Initiative selector.

#### Step 3: Display only the selected Initiative

Prevent Initiatives from accumulating in a scrolling viewport and render only the selected Initiative with its child work.

- **Status:** Completed
- **Risk:** Low
- **Estimated effort:** 60 minutes
- **Estimate confidence:** High

**Validation**

The planning viewport shows one selected Initiative.

#### Step 4: Complete Phase and Step CRUD

Add deterministic API and interface operations for the remaining planning hierarchy.

- **Status:** Completed
- **Risk:** Medium
- **Estimated effort:** 180 minutes
- **Estimate confidence:** Medium

**Validation**

Projects, Initiatives, Phases, and Steps can all be created and displayed through the planning console.

### Phase 3: Deterministic Plan Import

Import a complete versioned planning hierarchy from validated YAML without allowing AI-generated content to write directly to the database.

**Status:** Active

#### Step 1: Define planning I/O exceptions

Establish subsystem-specific schema, import, and export exception types.

- **Status:** Completed
- **Risk:** Low
- **Estimated effort:** 15 minutes
- **Estimate confidence:** High

**Validation**

Planning I/O failures expose explicit exception categories.

#### Step 2: Define version-one YAML schema validation

Validate fields, hierarchy, enums, positions, required text, and supported schema version before database access.

- **Status:** Completed
- **Risk:** Medium
- **Estimated effort:** 120 minutes
- **Estimate confidence:** Medium

**Validation**

Invalid or unknown planning values are rejected with a precise document path.

#### Step 3: Implement transactional hierarchy importer

Create the Project, Initiatives, Phases, and Steps in one atomic transaction after successful validation.

- **Status:** Completed
- **Risk:** High
- **Estimated effort:** 120 minutes
- **Estimate confidence:** Medium

**Risk details**

A partial hierarchy must never survive a failed import.

**Validation**

Any creation failure rolls back the entire imported hierarchy.

#### Step 4: Add import management command

Provide explicit dry-run and apply modes with user attribution and import counts.

- **Status:** Completed
- **Risk:** Low
- **Estimated effort:** 60 minutes
- **Estimate confidence:** High

**Validation**

Dry-run performs no writes and apply reports created record counts.

#### Step 5: Validate the Aurora planning document

Run the importer in dry-run mode against this versioned Aurora implementation plan.

- **Status:** Active
- **Risk:** Medium
- **Estimated effort:** 30 minutes
- **Estimate confidence:** High

**Validation**

The command reports one Project and the expected Initiative, Phase, and Step counts without writing records.

#### Step 6: Import the Aurora planning hierarchy

Apply the validated document so real Aurora work replaces the disposable Test Project as the planning interface data.

- **Status:** Planned
- **Risk:** High
- **Estimated effort:** 30 minutes
- **Estimate confidence:** High

**Risk details**

The Aurora project slug must not already exist before the create-only import.

**Validation**

The complete hierarchy appears in Aurora Console and no partial records exist.

### Phase 4: Planning Export

Export the canonical database hierarchy into durable, version-controlled planning documentation.

**Status:** Planned

#### Step 1: Implement deterministic YAML export

Serialize the current planning hierarchy using the supported versioned schema.

- **Status:** Planned
- **Risk:** Medium
- **Estimated effort:** 120 minutes
- **Estimate confidence:** Medium

**Validation**

Exported YAML can pass schema validation and preserve hierarchy order.

#### Step 2: Implement Markdown documentation export

Produce readable Project, Initiative, Phase, and Step documentation from canonical database records.

- **Status:** Planned
- **Risk:** Low
- **Estimated effort:** 120 minutes
- **Estimate confidence:** Medium

**Validation**

Exported Markdown accurately reflects the current database plan.

### Phase 5: Wu Planning Integration

Allow Wu to convert planning discussions into structured documents that pass through the deterministic importer.

**Status:** Planned

#### Step 1: Define Wu planning document contract

Specify how Wu produces versioned planning YAML without direct database authority.

- **Status:** Planned
- **Risk:** Medium
- **Estimated effort:** 90 minutes
- **Estimate confidence:** Medium

**Validation**

Wu output can be validated without interpretation by the importer.

#### Step 2: Add planning review workflow

Present generated planning changes for human review before applying them to the Decision Engine.

- **Status:** Planned
- **Risk:** High
- **Estimated effort:** 180 minutes
- **Estimate confidence:** Low

**Risk details**

Planning proposals must remain reviewable and must not silently overwrite canonical records.

**Validation**

Delta can review and explicitly approve or reject a generated plan before import.
