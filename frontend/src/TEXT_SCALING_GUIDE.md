# Text Scaling Guide - 200% Zoom Compliance

This guide ensures the AI Health Intelligence Platform remains fully functional at 200% browser zoom, meeting WCAG 2.1 Level AA requirements (Success Criterion 1.4.4 - Resize Text).

## Requirements

Users must be able to:
- Zoom text up to 200% without loss of content or functionality
- Read all text without horizontal scrolling
- Access all interactive elements
- Complete all tasks without assistive technology

## Implementation Strategy

### 1. Use Relative Units

✅ **Correct - Using rem units**
```css
.text {
  font-size: 1rem;      /* 16px at default */
  padding: 1rem;        /* Scales with text */
  margin: 0.5rem 1rem;  /* Scales proportionally */
}
```

❌ **Incorrect - Using fixed pixels**
```css
.text {
  font-size: 16px;      /* Won't scale with browser zoom */
  padding: 16px;        /* Fixed size */
}
```

### 2. Flexible Layouts

✅ **Correct - Flexbox with wrapping**
```tsx
<Box
  sx={{
    display: 'flex',
    flexWrap: 'wrap',
    gap: 2,
  }}
>
  <Button>Action 1</Button>
  <Button>Action 2</Button>
</Box>
```

❌ **Incorrect - Fixed widths**
```tsx
<Box sx={{ width: '800px' }}>
  {/* Content may overflow at 200% zoom */}
</Box>
```

### 3. Responsive Typography

Our theme uses responsive typography that scales properly:

```typescript
// From theme/index.ts
typography: {
  h1: {
    fontSize: '2rem',     // Base size
    '@media (min-width:768px)': {
      fontSize: '2.5rem',
    },
    '@media (min-width:1024px)': {
      fontSize: '3rem',
    },
  },
  body1: {
    fontSize: '1rem',     // 16px - scales with browser zoom
    lineHeight: 1.5,      // Relative line height
  },
}
```

### 4. Container Max-Widths

Use max-width instead of fixed width:

```tsx
<Container
  maxWidth="xl"
  sx={{
    px: { xs: 2, sm: 3, md: 4 }, // Responsive padding
  }}
>
  {content}
</Container>
```

## Testing Procedure

### Manual Testing Steps

1. **Set Browser Zoom to 100%**
   - Chrome/Edge: Ctrl/Cmd + 0
   - Firefox: Ctrl/Cmd + 0
   - Safari: Cmd + 0

2. **Navigate Through Application**
   - Test each major page
   - Note the layout and content visibility

3. **Increase Zoom to 150%**
   - Chrome/Edge: Ctrl/Cmd + Plus (+)
   - Firefox: Ctrl/Cmd + Plus (+)
   - Verify:
     - ✅ All text is readable
     - ✅ No horizontal scrolling
     - ✅ Interactive elements are accessible
     - ✅ Content reflows appropriately

4. **Increase Zoom to 200%**
   - Continue zooming to 200%
   - Verify same criteria as 150%
   - Check for:
     - ✅ No text truncation
     - ✅ No overlapping elements
     - ✅ All buttons/links are clickable
     - ✅ Forms remain usable

### Automated Testing

```typescript
import { validateTextScaling } from '@/utils/textScaling';

// In component tests
describe('Text Scaling', () => {
  it('should not have horizontal overflow at 200% zoom', () => {
    const { container } = render(<MyComponent />);
    const result = validateTextScaling(container);
    
    expect(result.passes).toBe(true);
    expect(result.issues).toHaveLength(0);
  });
});
```

## Common Issues and Solutions

### Issue 1: Horizontal Scrolling

**Problem**: Content requires horizontal scrolling at 200% zoom

**Solution**:
```tsx
// ❌ Bad
<Box sx={{ width: '1200px' }}>

// ✅ Good
<Box sx={{ maxWidth: '100%', width: '100%' }}>
```

### Issue 2: Text Truncation

**Problem**: Text is cut off with ellipsis

**Solution**:
```tsx
// ❌ Bad - Always truncates
<Typography noWrap>

// ✅ Good - Wraps when needed
<Typography sx={{ wordBreak: 'break-word' }}>
```

### Issue 3: Fixed Height Containers

**Problem**: Content overflows fixed-height containers

**Solution**:
```tsx
// ❌ Bad
<Box sx={{ height: '400px', overflow: 'hidden' }}>

// ✅ Good
<Box sx={{ minHeight: '400px', height: 'auto' }}>
```

### Issue 4: Overlapping Elements

**Problem**: Elements overlap at higher zoom levels

**Solution**:
```tsx
// ❌ Bad - Fixed positioning
<Box sx={{ position: 'absolute', top: '100px', left: '200px' }}>

// ✅ Good - Relative positioning with flex
<Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
```

## Component-Specific Guidelines

### Buttons

```tsx
// Ensure minimum touch target size
<Button
  sx={{
    minHeight: 44,
    minWidth: 44,
    px: 2,
    py: 1,
  }}
>
  Action
</Button>
```

### Forms

```tsx
// Allow labels and inputs to stack at higher zoom
<Box
  sx={{
    display: 'flex',
    flexDirection: { xs: 'column', md: 'row' },
    gap: 2,
  }}
>
  <FormLabel>Label</FormLabel>
  <TextField fullWidth />
</Box>
```

### Cards

```tsx
// Use flexible card layouts
<Card
  sx={{
    maxWidth: '100%',
    p: { xs: 2, md: 3 },
  }}
>
  <CardContent>
    {/* Content scales with zoom */}
  </CardContent>
</Card>
```

### Navigation

```tsx
// Sidebar should remain accessible
<Drawer
  sx={{
    '& .MuiDrawer-paper': {
      width: { xs: '80%', sm: 240 }, // Responsive width
      maxWidth: '100%',
    },
  }}
>
```

## Verification Checklist

Use this checklist when testing components:

### At 100% Zoom
- [ ] Layout appears as designed
- [ ] All text is readable
- [ ] All interactive elements work

### At 150% Zoom
- [ ] No horizontal scrolling
- [ ] Text remains readable
- [ ] Layout adapts appropriately
- [ ] All functionality works
- [ ] No overlapping elements

### At 200% Zoom
- [ ] No horizontal scrolling
- [ ] All text is readable (no truncation)
- [ ] All buttons/links are accessible
- [ ] Forms are fully usable
- [ ] Navigation works correctly
- [ ] No content is hidden or cut off
- [ ] Spacing is appropriate
- [ ] Images scale properly

## Browser-Specific Notes

### Chrome/Edge
- Text zoom: Ctrl/Cmd + Plus/Minus
- Reset: Ctrl/Cmd + 0
- Zoom level shown in address bar

### Firefox
- Text zoom: Ctrl/Cmd + Plus/Minus
- Text-only zoom: Ctrl/Cmd + Plus/Minus (in View menu)
- Reset: Ctrl/Cmd + 0

### Safari
- Text zoom: Cmd + Plus/Minus
- Reset: Cmd + 0
- Text-only zoom available in View menu

## Resources

- [WCAG 2.1 - Resize Text](https://www.w3.org/WAI/WCAG21/Understanding/resize-text.html)
- [MDN - CSS Units](https://developer.mozilla.org/en-US/docs/Learn/CSS/Building_blocks/Values_and_units)
- [Material-UI Responsive Typography](https://mui.com/material-ui/customization/typography/#responsive-font-sizes)

## Continuous Testing

Text scaling should be tested:
- When creating new components
- When modifying layouts
- During responsive design reviews
- As part of accessibility audits
- Before each release

## Last Updated

This guide was last updated: 2024-01-15

All components have been designed to support 200% zoom without loss of functionality.
