## 2026-06-15 - ARIA Roles for Custom Elements
**Learning:** Icon-only interactive `<span>` or `<div>` elements must be explicitly treated as buttons for accessibility. A click listener alone ignores keyboard users and screen readers.
**Action:** When a non-button element acts as a button, it must be augmented with `role="button"`, `tabindex="0"`, a meaningful `aria-label`, mapped keyboard listeners for `Enter` and `Space`, and dynamic `aria-pressed` states.
