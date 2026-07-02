# EcoTally desktop design QA

- Source visual truth path: `design-reference-desktop.png`
- Implementation screenshot: Computer Use window capture `screenshot-0`
  (1772 × 1218, EcoTally 0.27.1)
- Viewport: maximized Windows desktop window
- State: built-in example data selected and preview populated
- Full-view evidence: the implementation retains the reference hierarchy of
  sidebar, three-step progress, import area, selected-file row, preview table,
  and primary continuation action.
- Focused-region evidence: the selected-file row and preview table were
  inspected at full capture resolution; no additional crop was needed because
  their text, borders, and alternating rows were clearly legible.

## Findings

- No actionable P0, P1, or P2 findings remain for the reported contrast issue.
- Typography: selected filename is now bold dark green and remains readable.
- Spacing and layout: the selected state keeps the existing vertical rhythm
  without shifting surrounding controls.
- Colors and tokens: the page uses a gray-green background, white surfaces,
  and a distinct pale-green selected state with a strong green border.
- Image quality: no raster product imagery is used in this workflow; the
  native controls render sharply at the tested Windows scale.
- Copy: filename, size, and selected status remain visible in one line.

## Patches made

- Darkened and separated the page and sidebar background tokens.
- Added `surface_selected` and `line_strong` semantic tokens.
- Added a two-pixel green selected-file border and bold selected text.
- Added a preview-table boundary and alternating row backgrounds.
- Added a regression test ensuring state colors remain distinct.

## Follow-up polish

- P3: add a native application icon in a later release.

final result: passed
