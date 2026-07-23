# Future Initiatives

Ideas intentionally deferred to future phases.

---

## Repository Intelligence

### Progress Visualization

**Motivation**

Long-running repository operations should expose structured progress through
TelemetryLogger for both the terminal and Aurora UI.

**Desired Outcome**

- Live progress bar
- Current component
- Percent complete
- ETA (when practical)
- Restart point
- Failure diagnostics
- Shared telemetry events for terminal and UI

**Priority**

Medium

**Dependencies**

Telemetry UI
Structured telemetry events

**Promotion trigger:** Begin the telemetry UI integration phase.