# Accessibility Guidelines

This document outlines the accessibility features and guidelines implemented in the AI Health Intelligence Platform Frontend.

## WCAG 2.1 Level AA Compliance

The application aims to meet WCAG 2.1 Level AA standards for accessibility.

## Semantic HTML

### Main Structural Elements

- `<header>` - AppBar/Header component
- `<nav>` - Sidebar navigation
- `<main>` - Main content area (with `id="main-content"` for skip links)
- `<article>` - Assessment cards, result displays
- `<section>` - Grouped content areas
- `<aside>` - Complementary information

### Form Elements

- All form inputs have associated `<label>` elements
- Error messages are associated with inputs via `aria-describedby`
- Required fields are marked with `aria-required="true"`

## ARIA Labels and Roles

### Interactive Elements

All interactive elements without visible text labels have appropriate ARIA labels:

```tsx
// Icon buttons
<IconButton aria-label="toggle menu">
  <MenuIcon />
</IconButton>

// Avatar images
<Avatar alt="User avatar" src={photoURL} />

// Navigation
<nav role="navigation" aria-label="Main navigation">
```

### Live Regions

Screen reader announcements for dynamic content:

```tsx
// Notifications use aria-live regions
<div role="status" aria-live="polite" aria-atomic="true">
  {notification.message}
</div>

// Critical errors use assertive announcements
<div role="alert" aria-live="assertive">
  {errorMessage}
</div>
```

### Form Validation

```tsx
<TextField
  error={hasError}
  aria-invalid={hasError}
  aria-describedby={hasError ? 'error-message-id' : undefined}
  helperText={<span id="error-message-id">{errorMessage}</span>}
/>
```

## Keyboard Navigation

### Global Shortcuts

- `Ctrl+D` - Go to Dashboard
- `Ctrl+N` - New Assessment
- `Ctrl+H` - View History
- `Ctrl+P` - View Profile
- `Ctrl+Enter` - Submit Form
- `Escape` - Cancel/Close

### Tab Order

- All interactive elements are keyboard accessible
- Tab order follows visual flow
- Skip links allow jumping to main content
- Focus indicators are visible (2px solid outline)

### Focus Management

- Focus is trapped within modals/dialogs
- Focus returns to trigger element when modal closes
- First focusable element receives focus when modal opens

## Color Contrast

### Text Contrast Ratios

- Normal text: Minimum 4.5:1 contrast ratio
- Large text (18pt+): Minimum 3:1 contrast ratio
- UI components: Minimum 3:1 contrast ratio

### Color Palette

```typescript
// Primary text on white background: #1F2937 (11.5:1)
// Secondary text on white background: #6B7280 (4.6:1)
// Primary button: #4A90E2 on white (3.2:1)
```

### Risk Level Colors (Non-alarming)

- Low Risk: Blue (#10B981) - Calm, reassuring
- Medium Risk: Amber (#F59E0B) - Cautionary
- Elevated Risk: Orange (#F59E0B) - Warning
- High Risk: Soft Red (#EF4444) - Alert without alarm

## Responsive Design

### Breakpoints

- Mobile: <768px
- Tablet: 768-1024px
- Desktop: >1024px

### Touch Targets

- Minimum touch target size: 44x44px on mobile
- Adequate spacing between interactive elements
- Buttons and links have sufficient padding

## Text Scaling

- Supports up to 200% zoom without loss of functionality
- Uses relative units (rem, em) for font sizes
- No horizontal scrolling at 200% zoom
- Content reflows appropriately

## Screen Reader Support

### Announcements

```typescript
import { ariaAnnouncer } from '@/utils/accessibility';

// Announce success
ariaAnnouncer.announce('Assessment submitted successfully', 'polite');

// Announce error
ariaAnnouncer.announce('Error submitting assessment', 'assertive');
```

### Hidden Content

```tsx
// Visually hidden but available to screen readers
<span className="sr-only">Loading...</span>
```

## Images and Media

### Alternative Text

- All images have descriptive `alt` attributes
- Decorative images use `alt=""` or `role="presentation"`
- Complex images have extended descriptions

### Icons

```tsx
// Icons with meaning have labels
<IconButton aria-label="Delete assessment">
  <DeleteIcon />
</IconButton>

// Decorative icons are hidden from screen readers
<Icon aria-hidden="true" />
```

## Forms

### Labels

- All inputs have associated labels
- Labels are visible and descriptive
- Placeholder text is not used as the only label

### Error Handling

- Errors are announced to screen readers
- Error messages are specific and actionable
- Errors are associated with fields via `aria-describedby`

### Required Fields

```tsx
<TextField
  required
  aria-required="true"
  label="Email Address"
/>
```

## Testing

### Manual Testing

1. Keyboard navigation - Tab through all interactive elements
2. Screen reader testing - NVDA (Windows), VoiceOver (Mac)
3. Color contrast - Use browser DevTools or contrast checker
4. Zoom testing - Test at 200% zoom level
5. Focus indicators - Verify visible focus on all elements

### Automated Testing

```bash
# Run accessibility tests
npm run test:a11y

# Check with axe-core
npm run test:axe
```

### Browser Extensions

- axe DevTools
- WAVE
- Lighthouse Accessibility Audit

## Common Patterns

### Modal Dialog

```tsx
<Dialog
  open={open}
  onClose={onClose}
  aria-labelledby="dialog-title"
  aria-describedby="dialog-description"
>
  <DialogTitle id="dialog-title">Title</DialogTitle>
  <DialogContent id="dialog-description">
    Content
  </DialogContent>
</Dialog>
```

### Loading States

```tsx
<Box role="status" aria-live="polite" aria-busy={loading}>
  {loading ? 'Loading...' : content}
</Box>
```

### Error Messages

```tsx
<Alert severity="error" role="alert">
  {errorMessage}
</Alert>
```

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [WebAIM](https://webaim.org/)
- [Material-UI Accessibility](https://mui.com/material-ui/guides/accessibility/)

## Continuous Improvement

Accessibility is an ongoing process. Regular audits and user testing with assistive technologies help identify and address issues.
