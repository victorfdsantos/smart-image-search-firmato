"use client";
import { ImageIcon } from "lucide-react";
import { ImageCard } from "@/components/ImageCard";
import { Spinner } from "@/components/ui/Spinner";
import type { ProductSummary } from "@/types";

interface ProductGridProps {
  products: ProductSummary[];
  isLoading: boolean;
  onSelect: (product: ProductSummary) => void;
}

export function ProductGrid({ products, isLoading, onSelect }: ProductGridProps) {
  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-16">
        <Spinner className="w-8 h-8" />
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-16 text-firmato-muted">
        <ImageIcon size={48} className="text-firmato-border-dark" />
        <p className="font-lato text-base">Nenhum produto encontrado</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-3 gap-4">
      {products.map((p) => (
        <ImageCard
          key={p.id_produto}
          product={p}
          onClick={() => onSelect(p)}
        />
      ))}
    </div>
  );
}
