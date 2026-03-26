"use client";
import type { ProductSummary } from "@/types";

interface ImageCardProps {
  product: ProductSummary;
  onClick: () => void;
}

export function ImageCard({ product, onClick }: ImageCardProps) {
  const hasDims = !!(product.altura_cm || product.largura_cm);

  return (
    <article
      onClick={onClick}
      className="group relative overflow-hidden rounded-sm border border-firmato-border bg-firmato-surface cursor-pointer transition-all duration-300 hover:border-firmato-accent hover:-translate-y-1 hover:shadow-[0_12px_24px_-8px_rgba(0,0,0,0.15)]"
    >
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={product.imagem_url}
        alt={product.nome_produto}
        loading="lazy"
        className="w-full h-60 object-cover transition-opacity duration-300 group-hover:opacity-70"
      />

      {/* Gradient overlay — always visible */}
      <div className="absolute inset-x-0 bottom-0 p-3 bg-gradient-to-t from-black/80 via-black/50 to-transparent">
        <p className="font-lato text-[13px] font-semibold text-white line-clamp-2 leading-snug">
          {product.nome_produto}
        </p>
        {product.marca && (
          <p className="font-lato text-[11px] text-white/80 mt-0.5">
            {product.marca}
          </p>
        )}
        {product.categoria_principal && (
          <p className="font-lato text-[11px] text-white/70">
            {product.categoria_principal}
          </p>
        )}
        {product.faixa_preco && (
          <p className="font-lato text-[11px] font-semibold text-firmato-accent-light mt-0.5">
            {product.faixa_preco}
          </p>
        )}
        {hasDims && (
          <p className="font-lato text-[10px] text-white/60 mt-0.5">
            {[product.altura_cm, product.largura_cm, product.profundidade_cm]
              .filter(Boolean)
              .join(" × ")}{" "}
            cm
          </p>
        )}
      </div>
    </article>
  );
}
