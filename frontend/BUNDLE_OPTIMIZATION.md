# Bundle Optimization Guide

This document describes the bundle optimization strategies implemented in the AI Health Intelligence Platform frontend.

## Implemented Optimizations

### 1. Code Splitting

**Route-based code splitting**: All pages are lazy-loaded using React.lazy()
- Landing, Login, and Register pages are eagerly loaded (critical for initial load)
- All authenticated pages are lazy-loaded
- Reduces initial bundle size significantly

**Component-based lazy loading**: Use `useLazyComponent` hook for non-critical components
```typescript
import { useLazyComponent } from '@/hooks/useLazyComponent';

// Load after 1 second delay
const { Component, isLoaded } = useLazyComponent(
  () => import('./HeavyComponent'),
  { delay: 1000 }
);

// Load when visible
const { Component, isLoaded, ref } = useLazyComponent(
  () => import('./HeavyComponent'),
  { loadOnVisible: true }
);
```

**Image lazy loading**: Use `LazyImage` component for images
```typescript
import { LazyImage } from '@/components/common/LazyImage';

<LazyImage
  src="/path/to/image.jpg"
  alt="Description"
  placeholder="/path/to/placeholder.jpg"
/>
```

### 2. Vendor Chunk Splitting

Dependencies are split into logical chunks:
- `react-vendor`: React core libraries
- `mui-vendor`: Material-UI components
- `firebase-vendor`: Firebase SDK
- `chart-vendor`: Recharts library
- `stores`: Zustand stores

This allows for better caching and parallel loading.

### 3. Tree Shaking

Vite automatically performs tree shaking to remove unused code. To maximize effectiveness:
- Use named imports: `import { Button } from '@mui/material'`
- Avoid default imports from barrel files when possible
- Use ES modules throughout the codebase

### 4. Minification

Production builds use Terser for aggressive minification:
- Removes console.log statements
- Removes debugger statements
- Compresses variable names
- Removes dead code

### 5. Static Asset Caching

Service worker implements cache-first strategy for:
- JavaScript bundles
- CSS files
- Images
- Fonts

### 6. Dependency Optimization

Vite pre-bundles common dependencies for faster loading:
- React and React DOM
- React Router
- Material-UI
- Zustand
- Axios

## Bundle Analysis

### Running Bundle Analysis

```bash
# Build and analyze bundle
npm run build

# View detailed analysis
# Open dist/stats.html in browser
```

### Analyzing Results

The `stats.html` file provides:
- Visual treemap of bundle composition
- Size breakdown by module
- Gzipped and Brotli sizes
- Dependency relationships

### Bundle Size Targets

- **Initial bundle**: < 500 KB (gzipped)
- **Total bundle**: < 3 MB (uncompressed)
- **Largest chunk**: < 1 MB (uncompressed)

## Optimization Checklist

### Before Adding Dependencies

- [ ] Check bundle size impact using `npm run build`
- [ ] Look for lighter alternatives
- [ ] Consider if functionality can be implemented without dependency
- [ ] Check if dependency supports tree shaking

### Regular Maintenance

- [ ] Run bundle analysis monthly
- [ ] Review and remove unused dependencies
- [ ] Update dependencies to latest versions (often include optimizations)
- [ ] Monitor Core Web Vitals in production

### Code Review Guidelines

- [ ] Verify lazy loading for new pages
- [ ] Check for proper import statements (named vs default)
- [ ] Ensure images use LazyImage component
- [ ] Verify heavy components use lazy loading

## Performance Monitoring

### Key Metrics

Monitor these metrics in production:
- **First Contentful Paint (FCP)**: < 1.8s
- **Largest Contentful Paint (LCP)**: < 2.5s
- **Time to Interactive (TTI)**: < 3.8s
- **Total Blocking Time (TBT)**: < 200ms
- **Cumulative Layout Shift (CLS)**: < 0.1

### Tools

- Chrome DevTools Performance tab
- Lighthouse CI
- WebPageTest
- Bundle analyzer (stats.html)

## Common Issues and Solutions

### Issue: Large vendor chunks

**Solution**: Split large vendors into smaller chunks
```javascript
// vite.config.ts
manualChunks: {
  'mui-core': ['@mui/material/Button', '@mui/material/TextField'],
  'mui-icons': ['@mui/icons-material'],
}
```

### Issue: Duplicate dependencies

**Solution**: Use npm dedupe or check for version conflicts
```bash
npm dedupe
```

### Issue: Slow initial load

**Solution**: 
1. Reduce eager-loaded code
2. Implement more lazy loading
3. Optimize images
4. Enable compression on server

### Issue: Large CSS bundle

**Solution**:
1. Use CSS-in-JS with Material-UI (already implemented)
2. Remove unused CSS
3. Consider critical CSS extraction

## Future Optimizations

Potential improvements for future iterations:
- [ ] Implement HTTP/2 server push
- [ ] Add Brotli compression
- [ ] Implement progressive web app (PWA) features
- [ ] Add resource hints (preload, prefetch)
- [ ] Implement critical CSS extraction
- [ ] Add image optimization pipeline (WebP, AVIF)
- [ ] Implement dynamic imports for heavy libraries
- [ ] Add bundle budget enforcement in CI/CD

## Resources

- [Vite Build Optimizations](https://vitejs.dev/guide/build.html)
- [React Code Splitting](https://react.dev/reference/react/lazy)
- [Web.dev Performance](https://web.dev/performance/)
- [Bundle Phobia](https://bundlephobia.com/) - Check dependency sizes
