// ============================================================================
// Lazy Component Hook
// ============================================================================
// Hook for conditionally lazy loading components based on visibility or user interaction

import { useState, useEffect, useRef, ComponentType, lazy } from 'react';

interface UseLazyComponentOptions {
  /**
   * Delay in milliseconds before loading the component
   * Useful for deferring non-critical components
   */
  delay?: number;
  
  /**
   * Whether to load the component only when it becomes visible
   * Uses Intersection Observer API
   */
  loadOnVisible?: boolean;
  
  /**
   * Intersection Observer threshold (0-1)
   */
  threshold?: number;
  
  /**
   * Intersection Observer root margin
   */
  rootMargin?: string;
}

/**
 * Hook for lazy loading components with various strategies
 * 
 * @example
 * // Load after 1 second delay
 * const { Component, isLoaded } = useLazyComponent(
 *   () => import('./HeavyComponent'),
 *   { delay: 1000 }
 * );
 * 
 * @example
 * // Load when visible
 * const { Component, isLoaded, ref } = useLazyComponent(
 *   () => import('./HeavyComponent'),
 *   { loadOnVisible: true }
 * );
 * // Attach ref to container element
 * <div ref={ref}>{isLoaded && <Component />}</div>
 */
export function useLazyComponent<T extends ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>,
  options: UseLazyComponentOptions = {}
) {
  const {
    delay = 0,
    loadOnVisible = false,
    threshold = 0.01,
    rootMargin = '50px',
  } = options;

  const [Component, setComponent] = useState<T | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    let observer: IntersectionObserver;

    const loadComponent = () => {
      const LazyComponent = lazy(importFunc);
      setComponent(() => LazyComponent);
      setIsLoaded(true);
    };

    if (loadOnVisible) {
      // Load when visible using Intersection Observer
      if (!('IntersectionObserver' in window)) {
        // Fallback: load immediately
        loadComponent();
        return;
      }

      observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              if (delay > 0) {
                timeoutId = setTimeout(loadComponent, delay);
              } else {
                loadComponent();
              }
              if (containerRef.current) {
                observer.unobserve(containerRef.current);
              }
            }
          });
        },
        { threshold, rootMargin }
      );

      if (containerRef.current) {
        observer.observe(containerRef.current);
      }
    } else {
      // Load after delay
      timeoutId = setTimeout(loadComponent, delay);
    }

    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      if (observer && containerRef.current) {
        observer.unobserve(containerRef.current);
      }
    };
  }, [importFunc, delay, loadOnVisible, threshold, rootMargin]);

  return {
    Component,
    isLoaded,
    ref: containerRef,
  };
}
