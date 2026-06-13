## 2025-06-13 - Add ARIA Labels to Icon-Only Buttons
**Learning:** Found several icon-only interactive elements lacking accessibility context (the close modal "×" button, the favorites "★" star button, and the folder "📁" browse button). The star toggle is dynamic, so managing `aria-pressed` state alongside `aria-label` provides crucial context for screen readers navigating the tool categories.
**Action:** Always check dynamically generated interactive DOM elements in vanilla JS apps for missing accessibility attributes, especially when they act as toggles where `aria-pressed` is necessary.
