// ============================================================================
// Vite Plugin for Content Security Policy
// ============================================================================

/**
 * Content Security Policy configuration
 */
const CSP_DIRECTIVES = {
  'default-src': ["'self'"],
  'script-src': ["'self'", "'unsafe-inline'", 'https://apis.google.com', 'https://www.gstatic.com', 'https://www.googleapis.com', 'https://*.firebaseapp.com'],
  'style-src': ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com'],
  'font-src': ["'self'", 'https://fonts.gstatic.com'],
  'img-src': ["'self'", 'data:', 'https:', 'blob:', 'https://lh3.googleusercontent.com'], // Allow Google profile images
  'connect-src': ["'self'", 'https://identitytoolkit.googleapis.com', 'https://securetoken.googleapis.com', 'https://*.googleapis.com', 'https://*.firebaseio.com'],
  'frame-src': ["'self'", 'https://*.firebaseapp.com', 'https://*.google.com'],
  'base-uri': ["'self'"],
  'form-action': ["'self'"],
  'object-src': ["'none'"],
};

/**
 * Build CSP header value from directives
 */
function buildCspHeader(directives) {
  return Object.entries(directives)
    .map(([key, values]) => `${key} ${values.join(' ')}`)
    .join('; ');
}

/**
 * Vite plugin to add CSP meta tag to HTML
 */
export function cspPlugin() {
  const cspHeader = buildCspHeader(CSP_DIRECTIVES);

  return {
    name: 'vite-plugin-csp',
    transformIndexHtml(html) {
      // Add CSP meta tag to HTML
      return html.replace(
        '<head>',
        `<head>\n    <meta http-equiv="Content-Security-Policy" content="${cspHeader}">`
      );
    },
    configureServer(server) {
      // Add CSP header to dev server responses
      server.middlewares.use((req, res, next) => {
        res.setHeader('Content-Security-Policy', cspHeader);
        next();
      });
    },
  };
}

/**
 * Export CSP configuration for documentation
 */
export const CSP_CONFIG = {
  directives: CSP_DIRECTIVES,
  header: buildCspHeader(CSP_DIRECTIVES),
};
