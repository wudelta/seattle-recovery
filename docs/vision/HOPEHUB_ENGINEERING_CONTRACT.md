engineering_tolerance:

  aurora:
    classification: internal_development_platform
    user_base: controlled
    policy: >
      Prefer correctness, but allow bounded non-blocking technical debt
      when it does not threaten HopeHub or the development workflow.

  hopehub:
    classification: public_production_application
    user_base: vulnerable_and_mobile_dependent
    policy: >
      Treat every approved feature as production work from its first
      implementation. Require explicit architecture, authorization,
      privacy, API, accessibility, and failure-path consideration
      before code generation.