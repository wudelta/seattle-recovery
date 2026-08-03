# Initiative: King County Data Acquisition Pipeline

**Project:** HopeHub

**Status:** ACTIVE

**Priority:** HIGH

---

# Objective

Design and implement a deterministic data acquisition pipeline that downloads, validates, stores, normalizes, and maintains public King County resource datasets for the HopeHub Resource Finder.

The pipeline must operate without manual data entry and must preserve raw source data so future imports remain reproducible.

---

# Success Criteria

When complete, HopeHub shall be capable of:

* Downloading supported King County datasets.
* Verifying dataset metadata before import.
* Acquiring every available record through paginated requests.
* Preserving unmodified source records.
* Detecting updates without duplicating existing records.
* Producing normalized HopeHub Resource records.
* Reporting acquisition statistics and failures.
* Supporting repeatable refresh operations.

---

# Scope

## Included

* Dataset registry
* Metadata validation
* Source acquisition
* Pagination
* Rate limiting
* Retry handling
* Raw data preservation
* Normalization
* Validation reports
* Incremental updates
* Logging
* Management commands

## Deferred

* AI enrichment
* Website crawling
* OCR
* PDF extraction
* Manual provider verification
* National datasets
* Non-King County sources

---

# Phase 1 — Dataset Discovery

## Goal

Verify every candidate dataset before implementation.

### Step 1.1 — Build Dataset Registry

Status: ☐

Deliverables

* Registry of candidate dataset IDs
* Human-readable names
* Expected purpose
* Source URLs

Validation

* Every dataset appears exactly once.

---

### Step 1.2 — Metadata Probe

Status: ☐

Deliverables

Management command capable of retrieving:

* dataset title
* description
* update frequency
* row count
* field definitions
* last modified date

Validation

* Metadata report generated for every registry entry.

---

### Step 1.3 — Verify Candidate Sources

Status: ☐

Deliverables

Each dataset classified as:

* Verified
* Rejected
* Duplicate
* Deprecated

Validation

* Registry contains only verified acquisition targets.

---

# Phase 2 — Acquisition Engine

## Goal

Reliably download every verified dataset.

### Step 2.1 — API Client

Status: ☐

Validation

* Successfully retrieves one page from every verified dataset.

---

### Step 2.2 — Pagination

Status: ☐

Validation

* Entire datasets downloaded regardless of size.

---

### Step 2.3 — Retry & Rate Limiting

Status: ☐

Validation

* Handles transient failures and 429 responses gracefully.

---

### Step 2.4 — Acquisition Logging

Status: ☐

Validation

Each run records:

* start time
* end time
* datasets processed
* records downloaded
* failures
* elapsed time

---

# Phase 3 — Raw Data Repository

## Goal

Preserve authoritative source records.

### Step 3.1 — Source Dataset Model

Status: ☐

Validation

* Metadata persisted.

---

### Step 3.2 — Source Record Model

Status: ☐

Validation

* Raw JSON preserved without modification.

---

### Step 3.3 — Stable Identity

Status: ☐

Validation

* Duplicate imports update existing records instead of creating new ones.

---

# Phase 4 — Normalization

## Goal

Transform heterogeneous source records into HopeHub resources.

### Step 4.1 — Mapping Rules

Status: ☐

Validation

* Field mappings documented for every dataset.

---

### Step 4.2 — Resource Builder

Status: ☐

Validation

* Normalized resources successfully generated.

---

### Step 4.3 — Source References

Status: ☐

Validation

* Every normalized resource links back to its originating source record.

---

# Phase 5 — Incremental Updates

## Goal

Support repeatable imports.

### Step 5.1 — Change Detection

Status: ☐

Validation

* Unchanged records are skipped.

---

### Step 5.2 — Update Processing

Status: ☐

Validation

* Modified records update correctly.

---

### Step 5.3 — Scheduled Refresh Readiness

Status: ☐

Validation

* Acquisition command is safe to execute repeatedly.

---

# Phase 6 — Prototype Validation

## Goal

Demonstrate a functioning Resource Finder.

### Step 6.1 — Import Sample Data

Status: ☐

Validation

* Providers visible within HopeHub.

---

### Step 6.2 — Search Validation

Status: ☐

Validation

User can search by:

* keyword
* service category
* location

---

### Step 6.3 — Resource Detail

Status: ☐

Validation

Each resource displays:

* provider
* address
* phone
* available services
* source attribution
* last imported timestamp

---

# Risks

* Dataset schema changes
* Dataset retirement
* Rate limiting
* Missing identifiers
* Inconsistent addresses
* Duplicate providers across datasets

---

# Architectural Decisions

* Preserve raw source data.
* Never modify imported records in place.
* Normalize into HopeHub models separately.
* Maintain provenance for every normalized resource.
* All acquisition must be deterministic and repeatable.

---

# Completion Checklist

## Planning

* [ ] Dataset registry complete
* [ ] Metadata verified
* [ ] Acquisition architecture approved

## Acquisition

* [ ] Downloader implemented
* [ ] Pagination validated
* [ ] Retry logic validated

## Storage

* [ ] Raw repository operational
* [ ] Normalization operational

## HopeHub

* [ ] Resources searchable
* [ ] Prototype validated

---

# Notes

This initiative intentionally separates acquisition from normalization so that source data remains reproducible and future datasets can be incorporated without redesigning the acquisition subsystem.
