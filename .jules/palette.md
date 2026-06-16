## 2024-06-16 - Custom Interactive Elements Need Full ARIA and Keyboard Support
**Learning:** In this project, custom interactive elements (like `<span>` used for the theme switcher dots) must explicitly include `role="button"`, `tabindex="0"`, dynamic `aria-pressed`/`aria-label` states, AND mapped keyboard listeners for `Enter` and `Space` keys to ensure full accessibility for screen readers and keyboard users.
**Action:** Always verify that non-native interactive elements are upgraded with full ARIA semantics and keydown event handlers.
