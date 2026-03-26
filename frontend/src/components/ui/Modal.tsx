"use client";
import { useEffect, ReactNode } from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  className?: string;
}

export function Modal({ open, onClose, title, children, className }: ModalProps) {
  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/45"
      onClick={onClose}
    >
      <div
        className={cn(
          "bg-firmato-surface border border-firmato-border p-7 w-[480px] max-w-[90vw] animate-slide-down",
          className
        )}
        onClick={(e) => e.stopPropagation()}
      >
        {title && (
          <>
            <div className="flex items-center justify-between mb-5">
              <h2 className="font-lato text-lg font-light text-firmato-text tracking-tight">
                {title}
              </h2>
              <button
                onClick={onClose}
                className="text-firmato-muted hover:text-firmato-text transition-colors"
              >
                <X size={16} />
              </button>
            </div>
            <div className="border-t border-firmato-border mb-5" />
          </>
        )}
        {children}
      </div>
    </div>
  );
}
