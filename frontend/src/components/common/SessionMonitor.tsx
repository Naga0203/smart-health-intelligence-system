// ============================================================================
// Session Monitor Component
// ============================================================================
// Requirements: 11.3
// - Monitor token expiration time
// - Display notification 5 minutes before expiration
// - Offer option to extend session

import { useSessionMonitor } from '@/hooks/useSessionMonitor';

/**
 * Component that monitors session expiration and displays warnings.
 * This component doesn't render anything visible - it just runs the monitoring logic.
 */
export const SessionMonitor: React.FC = () => {
  useSessionMonitor();
  return null;
};
