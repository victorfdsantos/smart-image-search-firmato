"use client";
import { Eye, Copy, Download, ImageIcon } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { ProductDetailPanel } from "@/components/ProductDetailPanel";
import { SimilarProducts } from "@/components/SimilarProducts";
import type { ProductDetail, ProductSummary } from "@/types";
import { Spinner } from "@/components/ui/Spinner";

interface PreviewPanelProps {
  selectedImage: string;
  selectedProduct: ProductDetail | null;
  loadingDetail: boolean;
  similarProducts?: ProductSummary[];
  onSelectSimilar?: (product: ProductSummary) => void;
}

export function PreviewPanel({
  selectedImage,
  selectedProduct,
  loadingDetail,
  similarProducts = [],
  onSelectSimilar,
}: PreviewPanelProps) {
  const copyImage = async () => {
    try {
      const res = await fetch(selectedImage, { mode: "cors" });
      const blob = await res.blob();
      await navigator.clipboard.write([
        new ClipboardItem({ "image/jpeg": blob }),
      ]);
    } catch (e) {
      console.error("Copy failed:", e);
    }
  };

  const downloadImage = async () => {
    try {
      const res = await fetch(selectedImage, { mode: "cors" });
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = selectedImage.split("/").pop() ?? "image.jpg";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error("Download failed:", e);
    }
  };

  return (
    <div className="bg-firmato-surface border border-firmato-border p-7 space-y-4">
      <div className="flex items-center gap-2">
        <Eye size={18} className="text-firmato-accent" />
        <h2 className="font-lato text-xl font-light text-firmato-text tracking-tight">
          Pré-visualização
        </h2>
      </div>
      <div className="border-t border-firmato-border" />

      {selectedImage ? (
        <>
          {/* Image container with floating similar products */}
          <div className="relative border border-firmato-border p-1">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={selectedImage}
              alt="Preview"
              className="w-full max-h-[600px] object-contain rounded-sm"
            />

            {/* Floating similar products — vertical strip on right edge */}
            <SimilarProducts
              products={similarProducts}
              onSelect={onSelectSimilar ?? (() => {})}
              visible={similarProducts.length > 0}
            />
          </div>

          <div className="flex gap-3">
            <Button variant="outline" className="flex-1" onClick={copyImage}>
              <Copy size={15} />
              Copiar imagem
            </Button>
            <Button variant="solid" className="flex-1" onClick={downloadImage}>
              <Download size={15} />
              Download
            </Button>
          </div>

          {loadingDetail ? (
            <div className="flex justify-center py-6">
              <Spinner />
            </div>
          ) : (
            selectedProduct && <ProductDetailPanel product={selectedProduct} />
          )}
        </>
      ) : (
        <div className="flex flex-col items-center justify-center gap-3 h-[600px] border-2 border-dashed border-firmato-border bg-firmato-bg rounded-sm">
          <ImageIcon size={64} className="text-firmato-border" />
          <p className="font-lato text-base text-firmato-muted">
            Selecione uma imagem
          </p>
          <p className="font-lato text-sm text-firmato-muted">
            Clique em qualquer imagem para visualizar
          </p>
        </div>
      )}
    </div>
  );
}