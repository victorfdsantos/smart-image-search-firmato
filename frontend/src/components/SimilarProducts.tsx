"use client";
import { useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";
import type { ProductSummary } from "@/types";

interface SimilarProductsProps {
  products: ProductSummary[];
  onSelect: (product: ProductSummary) => void;
  visible: boolean;
}

export function SimilarProducts({ products, onSelect, visible }: SimilarProductsProps) {
  const [hovered, setHovered] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    if (visible) {
      // Stagger mount for animation
      const t = setTimeout(() => setMounted(true), 50);
      return () => clearTimeout(t);
    } else {
      setMounted(false);
    }
  }, [visible]);

  if (!visible || products.length === 0) return null;

  return (
    <div
      className={cn(
        "absolute right-0 top-0 h-full z-20",
        "flex flex-col justify-center",
        "pointer-events-none",
      )}
      style={{ width: "72px" }}
    >
      {/* Subtle fade label */}
      <div
        className={cn(
          "absolute top-4 right-0 writing-mode-vertical",
          "font-lato text-[9px] uppercase tracking-[0.2em] text-firmato-muted/50",
          "transition-opacity duration-500",
          mounted ? "opacity-100" : "opacity-0"
        )}
        style={{
          writingMode: "vertical-rl",
          textOrientation: "mixed",
          transform: "rotate(180deg)",
          right: "6px",
          top: "12px",
          letterSpacing: "0.25em",
        }}
      >
        similares
      </div>

      {/* Thumbnails */}
      <div className="flex flex-col gap-2 items-end pr-2 pointer-events-auto">
        {products.slice(0, 6).map((product, i) => (
          <button
            key={product.id_produto}
            onClick={() => onSelect(product)}
            onMouseEnter={() => setHovered(String(product.id_produto))}
            onMouseLeave={() => setHovered(null)}
            className={cn(
              "relative group block",
              "transition-all duration-300 ease-out",
              mounted ? "opacity-100 translate-x-0" : "opacity-0 translate-x-4"
            )}
            style={{
              transitionDelay: mounted ? `${i * 60}ms` : "0ms",
            }}
            title={product.nome_produto}
          >
            {/* Tooltip on hover */}
            {hovered === String(product.id_produto) && (
              <div
                className={cn(
                  "absolute right-full mr-2 top-1/2 -translate-y-1/2",
                  "bg-firmato-text/90 text-white",
                  "font-lato text-[10px] whitespace-nowrap",
                  "px-2 py-1 pointer-events-none z-30",
                  "animate-slide-down"
                )}
                style={{ borderRadius: "2px" }}
              >
                <p className="font-semibold leading-tight max-w-[140px] truncate">
                  {product.nome_produto}
                </p>
                {product.marca && (
                  <p className="text-white/70 mt-0.5">{product.marca}</p>
                )}
              </div>
            )}

            {/* Thumbnail image */}
            <div
              className={cn(
                "overflow-hidden border transition-all duration-200",
                hovered === String(product.id_produto)
                  ? "border-firmato-accent w-14 h-14 shadow-lg"
                  : "border-firmato-border/60 w-11 h-11",
              )}
              style={{ borderRadius: "2px" }}
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={product.imagem_url}
                alt={product.nome_produto}
                className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
              />
            </div>

            {/* Active indicator dot */}
            <div
              className={cn(
                "absolute -left-1.5 top-1/2 -translate-y-1/2 w-1 h-1 rounded-full",
                "transition-all duration-200",
                hovered === String(product.id_produto)
                  ? "bg-firmato-accent scale-100"
                  : "bg-transparent scale-0"
              )}
            />
          </button>
        ))}
      </div>
    </div>
  );
}