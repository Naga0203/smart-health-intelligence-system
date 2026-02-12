#!/usr/bin/env node
// ============================================================================
// Bundle Analysis Script
// ============================================================================
// Analyzes bundle size and provides optimization recommendations

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');

console.log('🔍 Analyzing bundle size...\n');

// Build the project
console.log('📦 Building project...');
try {
  execSync('npm run build', { cwd: rootDir, stdio: 'inherit' });
} catch (error) {
  console.error('❌ Build failed');
  process.exit(1);
}

// Get dist directory size
const distDir = path.join(rootDir, 'dist');
const getDirectorySize = (dir) => {
  let size = 0;
  const files = fs.readdirSync(dir);
  
  files.forEach((file) => {
    const filePath = path.join(dir, file);
    const stats = fs.statSync(filePath);
    
    if (stats.isDirectory()) {
      size += getDirectorySize(filePath);
    } else {
      size += stats.size;
    }
  });
  
  return size;
};

const totalSize = getDirectorySize(distDir);
const totalSizeMB = (totalSize / 1024 / 1024).toFixed(2);

console.log('\n📊 Bundle Analysis Results:');
console.log('═══════════════════════════════════════');
console.log(`Total bundle size: ${totalSizeMB} MB`);

// Analyze individual chunks
const assetsDir = path.join(distDir, 'assets');
if (fs.existsSync(assetsDir)) {
  const assets = fs.readdirSync(assetsDir);
  const jsFiles = assets.filter((file) => file.endsWith('.js'));
  const cssFiles = assets.filter((file) => file.endsWith('.css'));
  
  console.log(`\nJavaScript files: ${jsFiles.length}`);
  jsFiles.forEach((file) => {
    const filePath = path.join(assetsDir, file);
    const stats = fs.statSync(filePath);
    const sizeKB = (stats.size / 1024).toFixed(2);
    console.log(`  - ${file}: ${sizeKB} KB`);
  });
  
  console.log(`\nCSS files: ${cssFiles.length}`);
  cssFiles.forEach((file) => {
    const filePath = path.join(assetsDir, file);
    const stats = fs.statSync(filePath);
    const sizeKB = (stats.size / 1024).toFixed(2);
    console.log(`  - ${file}: ${sizeKB} KB`);
  });
}

// Recommendations
console.log('\n💡 Optimization Recommendations:');
console.log('═══════════════════════════════════════');

if (totalSize > 5 * 1024 * 1024) {
  console.log('⚠️  Bundle size is large (>5MB). Consider:');
  console.log('   - Implementing more code splitting');
  console.log('   - Lazy loading heavy components');
  console.log('   - Removing unused dependencies');
} else if (totalSize > 3 * 1024 * 1024) {
  console.log('⚠️  Bundle size is moderate (>3MB). Consider:');
  console.log('   - Reviewing large dependencies');
  console.log('   - Optimizing images and assets');
} else {
  console.log('✅ Bundle size is good (<3MB)');
}

console.log('\n📈 View detailed analysis:');
console.log(`   Open: ${path.join(distDir, 'stats.html')}`);
console.log('\n');
