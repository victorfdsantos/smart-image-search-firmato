"use client";
import { useState } from "react";
import { ClipboardCheck, Clipboard } from "lucide-react";
import type { ProductDetail } from "@/types";
import { Button } from "@/components/ui/Button";

interface DetailFieldProps {
  label: string;
  value?: string | number | null;
}

function DetailField({ label, value }: DetailFieldProps) {
  if (!value) return null;
  return (
    <div className="flex py-1.5 border-b border-firmato-border last:border-b-0">
      <span className="font-lato text-xs text-firmato-muted min-w-[140px] shrink-0">
        {label}
      </span>
      <span className="font-lato text-xs text-firmato-text flex-1">{value}</span>
    </div>
  );
}

interface SectionProps {
  title: string;
  children: React.ReactNode;
}

function Section({ title, children }: SectionProps) {
  return (
    <div className="space-y-0">
      <p className="font-lato text-[11px] font-bold text-firmato-accent uppercase tracking-widest pt-2 pb-1">
        {title}
      </p>
      {children}
    </div>
  );
}

interface ProductDetailPanelProps {
  product: ProductDetail;
}

function buildFicha(product: ProductDetail): string {
  const lines: string[] = [];

  if (product.nome_produto) lines.push(`${product.nome_produto}`);
  if (product.marca) lines.push(`Marca: ${product.marca}`);
  if (product.categoria_principal) lines.push(`Categoria: ${product.categoria_principal}`);
  if (product.subcategoria) lines.push(`Subcategoria: ${product.subcategoria}`);
  if (product.faixa_preco) lines.push(`Faixa de preço: ${product.faixa_preco}`);

  const dims = [product.altura_cm, product.largura_cm, product.profundidade_cm]
    .filter(Boolean)
    .join(" × ");
  if (dims) lines.push(`Dimensões (A × L × P): ${dims} cm`);

  if (product.material_principal) lines.push(`Material: ${product.material_principal}`);
  if (product.ambiente) lines.push(`Ambiente: ${product.ambiente}`);
  if (product.status) lines.push(`Status: ${product.status}`);
  if (product.id_produto) lines.push(`ID: ${product.id_produto}`);

  return lines.join("\n");
}

export function ProductDetailPanel({ product }: ProductDetailPanelProps) {
  const [copied, setCopied] = useState(false);

  const handleCopyFicha = async () => {
    const text = buildFicha(product);
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // fallback
      const el = document.createElement("textarea");
      el.value = text;
      document.body.appendChild(el);
      el.select();
      document.execCommand("copy");
      document.body.removeChild(el);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="mt-3 p-5 bg-firmato-bg border border-firmato-border space-y-1">
      {/* Header with copy button */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-lato text-[15px] font-light text-firmato-text tracking-tight">
          Informações do Produto
        </h3>
        <Button
          variant={copied ? "solid" : "outline"}
          size="sm"
          onClick={handleCopyFicha}
          className={
            copied
              ? "text-white border-green-500 bg-green-500 hover:bg-green-500"
              : ""
          }
        >
          {copied ? (
            <>
              <ClipboardCheck size={13} />
              Copiado!
            </>
          ) : (
            <>
              <Clipboard size={13} />
              Copiar ficha
            </>
          )}
        </Button>
      </div>

      <div className="border-t border-firmato-border" />

      <div className="space-y-2 pt-1">
        <Section title="Identificação">
          <DetailField label="ID" value={String(product.id_produto)} />
          <DetailField label="Nome" value={product.nome_produto} />
          <DetailField label="Marca" value={product.marca} />
          <DetailField label="Status" value={product.status} />
          <DetailField label="Categoria" value={product.categoria_principal} />
          <DetailField label="Subcategoria" value={product.subcategoria} />
          <DetailField label="Faixa de Preço" value={product.faixa_preco} />
        </Section>

        <Section title="Características">
          <DetailField label="Ambiente" value={product.ambiente} />
          <DetailField label="Forma" value={product.forma} />
          <DetailField label="Material Principal" value={product.material_principal} />
          <DetailField label="Material Estrutura" value={product.material_estrutura} />
          <DetailField label="Material Revestimento" value={product.material_revestimento} />
        </Section>

        <Section title="Dimensões">
          <DetailField label="Altura (cm)" value={product.altura_cm} />
          <DetailField label="Largura (cm)" value={product.largura_cm} />
          <DetailField label="Profundidade (cm)" value={product.profundidade_cm} />
        </Section>

        {product.descricao_tecnica && (
          <Section title="Descrição Técnica">
            <p className="font-lato text-xs text-firmato-muted py-1.5 whitespace-pre-wrap leading-relaxed">
              {product.descricao_tecnica}
            </p>
          </Section>
        )}
      </div>
    </div>
  );
}