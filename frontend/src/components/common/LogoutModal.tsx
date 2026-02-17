import React, { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';

interface LogoutModalProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: () => Promise<void> | void;
}

export const LogoutModal: React.FC<LogoutModalProps> = ({
    isOpen,
    onClose,
    onConfirm,
}) => {
    const [isLoggingOut, setIsLoggingOut] = useState(false);
    const modalRef = useRef<HTMLDivElement>(null);
    const confirmBtnRef = useRef<HTMLButtonElement>(null);
    const previousFocusRef = useRef<HTMLElement | null>(null);

    // Handle focus management and keystrokes
    useEffect(() => {
        if (isOpen) {
            // Store currently focused element to restore later
            previousFocusRef.current = document.activeElement as HTMLElement;

            // Prevent scrolling on body
            document.body.style.overflow = 'hidden';

            // Focus confirm button after animation starts
            const timer = setTimeout(() => {
                if (confirmBtnRef.current) {
                    confirmBtnRef.current.focus();
                }
            }, 50);

            return () => {
                clearTimeout(timer);
                document.body.style.overflow = '';
                // Restore focus
                if (previousFocusRef.current) {
                    previousFocusRef.current.focus();
                }
            };
        }
    }, [isOpen]);

    // Handle Escape key
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (!isOpen) return;

            if (e.key === 'Escape') {
                onClose();
            }

            // Trap focus
            if (e.key === 'Tab' && modalRef.current) {
                const focusableElements = modalRef.current.querySelectorAll(
                    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                );
                const firstElement = focusableElements[0] as HTMLElement;
                const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

                if (e.shiftKey) {
                    if (document.activeElement === firstElement) {
                        e.preventDefault();
                        lastElement.focus();
                    }
                } else {
                    if (document.activeElement === lastElement) {
                        e.preventDefault();
                        firstElement.focus();
                    }
                }
            }
        };

        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [isOpen, onClose]);

    const handleConfirm = async () => {
        setIsLoggingOut(true);
        await onConfirm();
        // No need to set isLoggingOut(false) typically as we navigate away
    };

    // Render via portal to ensure it's on top of everything
    // Assuming there is a root element, but fallback to body if needed
    const mountPoint = document.getElementById('root') || document.body;

    if (!isOpen) return null;

    return createPortal(
        <div
            className={`modal ${isOpen ? 'active' : ''}`}
            aria-hidden={!isOpen}
            role="presentation"
        >
            <div className="modal-backdrop" onClick={onClose} />

            <div
                ref={modalRef}
                className="modal-content"
                role="dialog"
                aria-modal="true"
                aria-labelledby="logout-title"
                aria-describedby="logout-description"
            >
                <div className="modal-icon">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                        <path d="M16 17L21 12L16 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        <path d="M21 12H9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        <path d="M13 21H5C4.44772 21 4 20.5523 4 20V4C4 3.44772 4.44772 3 5 3H13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                </div>

                <h2 id="logout-title">Confirm Logout</h2>

                <p id="logout-description">
                    Are you sure you want to log out of your account?
                    You will need to sign in again to access your dashboard.
                </p>

                <div className="modal-actions">
                    <button
                        onClick={onClose}
                        className="btn-secondary"
                        disabled={isLoggingOut}
                    >
                        Cancel
                    </button>
                    <button
                        ref={confirmBtnRef}
                        onClick={handleConfirm}
                        className="btn-danger"
                        disabled={isLoggingOut}
                    >
                        {isLoggingOut ? 'Logging out...' : 'Log Out'}
                    </button>
                </div>
            </div>
        </div>,
        mountPoint
    );
};
