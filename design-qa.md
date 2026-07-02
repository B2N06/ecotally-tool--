# EcoTally desktop design QA

- Source reference: `design-reference-desktop.png`
- Implementation capture: unavailable; the approved app-window capture session
  timed out, and full-screen capture was intentionally not used because it
  could include unrelated private content.
- Target viewport: 1180 × 780
- Tested state: first-run import screen
- Runtime verification: packaged `EcoTally.exe` remained running after the
  six-second startup smoke test.
- Comparison: code-level review confirms the reference structure (left
  navigation, three-step progress, import panel, preview table, and green
  primary action), but a screenshot-to-screenshot comparison is still pending.
- Fidelity findings: no runtime crash was observed; visual fidelity cannot be
  signed off without a window-only implementation capture.
- Final result: blocked pending safe packaged-app window capture
