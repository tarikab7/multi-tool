
## 2024-05-18 - Missing Accessibility on Interactive Spans
**Learning:** Custom interactive elements (like the theme customizer `.theme-dot` spans) frequently lack keyboard accessibility and screen reader support when they don't use native `<button>` tags. They require `role="button"`, `tabindex="0"`, `keydown` event handlers for Enter/Space, and dynamic `aria-pressed` state management.
**Action:** When inspecting non-button interactive elements (e.g. spans acting as toggles), always add full ARIA mapping and keyboard listener fallback to ensure equal accessibility.
