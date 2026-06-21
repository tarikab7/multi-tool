## 2024-05-18 - Accessible Theme Toggles & Icon Buttons
**Learning:** Custom interactive elements like color theme toggle `span`s are completely invisible to keyboard and screen reader users without explicit ARIA roles, tabindex, and keyboard event handlers. Icon-only buttons (like modal close buttons) need `aria-label`s to provide context.
**Action:** Always add `role="button"`, `tabindex="0"`, `aria-pressed`, and mapped `Enter`/`Space` keyboard listeners to spans/divs acting as buttons. Ensure icon-only buttons have descriptive `aria-label`s.
