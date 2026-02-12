# Bundle Optimization Setup

## Required Dependencies

To enable bundle analysis, install the following dev dependency:

```bash
npm install --save-dev rollup-plugin-visualizer
```

## Usage

After installing the dependency, the bundle analyzer will automatically generate a `stats.html` file in the `dist` folder when you run:

```bash
npm run build
```

Open `dist/stats.html` in your browser to view the interactive bundle analysis.

## Alternative: Manual Analysis

If you prefer not to install the visualizer, you can still optimize the bundle using the configuration in `vite.config.ts`. The manual chunks and optimization settings will still apply.

To analyze without the visualizer:
1. Comment out the visualizer plugin in `vite.config.ts`
2. Run `npm run build`
3. Check the console output for chunk sizes
4. Manually inspect the `dist/assets` folder

## Bundle Size Monitoring

Monitor bundle sizes by checking the build output:
- Look for warnings about large chunks (>1MB)
- Compare sizes between builds
- Use Chrome DevTools Network tab to measure actual load times
