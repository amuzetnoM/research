import React, { Fragment, ReactNode } from 'react';
import Button from './Button';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  footer?: ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  closeOnClickOutside?: boolean;
  variant?: 'glass' | 'neumorph';
}

const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  footer,
  size = 'md',
  closeOnClickOutside = true,
  variant = 'glass',
}) => {
  if (!isOpen) return null;

  const handleBackdropClick = () => {
    if (closeOnClickOutside) {
      onClose();
    }
  };

  const handleContentClick = (e: React.MouseEvent) => {
    e.stopPropagation();
  };

  const sizeClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    full: 'max-w-full',
  };

  const variantClasses = {
    glass: 'glass border-thin border-white/30 backdrop-blur-md bg-white/10',
    neumorph: 'neumorph border-thin border-white/30 bg-background',
  };

  return (
    <Fragment>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-50 bg-black/30 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in"
        onClick={handleBackdropClick}
      >
        {/* Modal Content */}
        <div
          className={`${variantClasses[variant]} w-full ${sizeClasses[size]} max-h-[90vh] flex flex-col rounded-2xl overflow-hidden shadow-lg animate-in zoom-in-50 duration-200`}
          onClick={handleContentClick}
        >
          {/* Header */}
          {title && (
            <div className={`p-5 flex justify-between items-center ${variant === 'glass' ? 'border-b border-white/10' : 'border-b border-gray-100 dark:border-gray-800'}`}>
              <h3 className={`text-lg font-medium ${variant === 'glass' ? 'gradient-text' : 'text-foreground'}`}>
                {title}
              </h3>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-primary-500 focus:outline-none"
                aria-label="Close"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
          )}

          {/* Body */}
          <div className="flex-1 p-5 overflow-y-auto scrollbar">
            {children}
          </div>

          {/* Footer */}
          {footer && (
            <div className={`p-5 flex justify-end gap-2 ${variant === 'glass' ? 'border-t border-white/10' : 'border-t border-gray-100 dark:border-gray-800'}`}>
              {footer}
            </div>
          )}
        </div>
      </div>
    </Fragment>
  );
};

export default Modal;

// Also export a convenience component for common modal usage patterns
export const ConfirmationModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  confirmVariant?: 'primary' | 'danger' | 'success';
  variant?: 'glass' | 'neumorph';
  isLoading?: boolean;
}> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  confirmVariant = 'primary',
  variant = 'glass',
  isLoading = false,
}) => {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      variant={variant}
      footer={
        <>
          <Button variant="ghost" onClick={onClose} disabled={isLoading} size="sm">
            {cancelText}
          </Button>
          <Button
            variant={confirmVariant}
            onClick={onConfirm}
            loading={isLoading}
            size="sm"
          >
            {confirmText}
          </Button>
        </>
      }
    >
      <p className="text-foreground/80">
        {message}
      </p>
    </Modal>
  );
};