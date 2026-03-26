import { cn } from "@/lib/utils";
import { ButtonHTMLAttributes, forwardRef } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "solid" | "outline" | "ghost";
  size?: "sm" | "md";
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "outline", size = "md", children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center gap-2 rounded-sm font-lato text-xs uppercase tracking-wider transition-all duration-200 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed",
          size === "md" && "px-6 py-2.5",
          size === "sm" && "px-3 py-1.5",
          variant === "solid" &&
            "bg-firmato-accent border border-firmato-accent text-white hover:bg-firmato-accent-light hover:border-firmato-accent-light",
          variant === "outline" &&
            "bg-transparent border border-firmato-border-dark text-firmato-text hover:bg-firmato-bg hover:border-firmato-accent hover:text-firmato-accent",
          variant === "ghost" &&
            "bg-transparent border-none text-firmato-muted hover:text-firmato-text px-2",
          className
        )}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";
