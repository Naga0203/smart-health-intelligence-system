// ============================================================================
// Network Status Hook
// ============================================================================
// Detects online/offline status and connection quality

import { useState, useEffect } from 'react';

export interface NetworkStatus {
  isOnline: boolean;
  isSlow: boolean;
  effectiveType: 'slow-2g' | '2g' | '3g' | '4g' | 'unknown';
  downlink: number; // Mbps
  rtt: number; // Round-trip time in ms
}

/**
 * Hook to monitor network status and connection quality
 * 
 * @returns NetworkStatus object with connection information
 * 
 * @example
 * const { isOnline, isSlow } = useNetworkStatus();
 * if (!isOnline) {
 *   return <OfflineIndicator />;
 * }
 */
export function useNetworkStatus(): NetworkStatus {
  const [networkStatus, setNetworkStatus] = useState<NetworkStatus>(() => {
    const connection = getNetworkConnection();
    return {
      isOnline: navigator.onLine,
      isSlow: connection ? isSlowConnection(connection) : false,
      effectiveType: connection?.effectiveType || 'unknown',
      downlink: connection?.downlink || 0,
      rtt: connection?.rtt || 0,
    };
  });

  useEffect(() => {
    const updateNetworkStatus = () => {
      const connection = getNetworkConnection();
      setNetworkStatus({
        isOnline: navigator.onLine,
        isSlow: connection ? isSlowConnection(connection) : false,
        effectiveType: connection?.effectiveType || 'unknown',
        downlink: connection?.downlink || 0,
        rtt: connection?.rtt || 0,
      });
    };

    // Listen for online/offline events
    window.addEventListener('online', updateNetworkStatus);
    window.addEventListener('offline', updateNetworkStatus);

    // Listen for connection changes
    const connection = getNetworkConnection();
    if (connection) {
      connection.addEventListener('change', updateNetworkStatus);
    }

    return () => {
      window.removeEventListener('online', updateNetworkStatus);
      window.removeEventListener('offline', updateNetworkStatus);
      if (connection) {
        connection.removeEventListener('change', updateNetworkStatus);
      }
    };
  }, []);

  return networkStatus;
}

/**
 * Get the network connection object
 */
function getNetworkConnection(): any {
  return (
    (navigator as any).connection ||
    (navigator as any).mozConnection ||
    (navigator as any).webkitConnection
  );
}

/**
 * Determine if connection is slow
 */
function isSlowConnection(connection: any): boolean {
  if (!connection) return false;

  // Check effective type
  if (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
    return true;
  }

  // Check RTT (round-trip time)
  if (connection.rtt && connection.rtt > 500) {
    return true;
  }

  // Check downlink speed (Mbps)
  if (connection.downlink && connection.downlink < 1) {
    return true;
  }

  return false;
}
