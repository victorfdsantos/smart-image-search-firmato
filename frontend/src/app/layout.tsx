import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Firmato — Buscador de Imagens",
  description: "Buscador de imagens do catálogo de produtos Firmato Móveis",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
