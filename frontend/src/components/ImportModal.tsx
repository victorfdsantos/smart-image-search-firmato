"use client";
import { useRef, useState } from "react";
import { Upload, FileSpreadsheet, FileUp, CheckCircle, Brain, FileText } from "lucide-react";
import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import { registerCatalog } from "@/lib/api";
import type { UploadStats } from "@/types";

interface ImportModalProps {
  open: boolean;
  onClose: () => void;
}

type State =
  | { kind: "idle" }
  | { kind: "uploading" }
  | { kind: "retraining" }
  | { kind: "success"; stats?: UploadStats }
  | { kind: "error"; message: string };

function StatRow({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-center justify-between py-1 border-b border-firmato-border last:border-b-0">
      <span className="font-lato text-sm text-firmato-muted">{label}</span>
      <span className="font-lato text-sm font-semibold text-firmato-text">
        {value}
      </span>
    </div>
  );
}

export function ImportModal({ open, onClose }: ImportModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [state, setState] = useState<State>({ kind: "idle" });
  const [dragging, setDragging] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const reset = () => {
    setFile(null);
    setState({ kind: "idle" });
    setDragging(false);
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  const handleFile = (f: File) => {
    if (!f.name.match(/\.(xlsx|xlsm)$/i)) {
      setState({ kind: "error", message: "Apenas arquivos .xlsx e .xlsm são aceitos." });
      return;
    }
    setFile(f);
    setState({ kind: "idle" });
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files?.[0];
    if (f) handleFile(f);
  };

  const doUpload = async () => {
    if (!file) {
      setState({ kind: "error", message: "Selecione um arquivo antes de continuar." });
      return;
    }
    setState({ kind: "uploading" });
    const result = await registerCatalog(file);
    if (!result || result.detail) {
      setState({ kind: "error", message: result?.detail ?? "Erro inesperado no servidor." });
      return;
    }
    setState({ kind: "success", stats: result.stats as unknown as UploadStats });
  };

  const doRetrain = async () => {
    setState({ kind: "retraining" });
    try {
      const res = await fetch("/api/catalog/retrain", { method: "POST" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setState({ kind: "success" });
    } catch (e) {
      setState({ kind: "error", message: `Erro no retreinamento: ${e}` });
    }
  };

  const isLoading = state.kind === "uploading" || state.kind === "retraining";

  return (
    <Modal open={open} onClose={handleClose} title="Importar Dados">
      {isLoading ? (
        <div className="flex flex-col items-center gap-3 py-10">
          <Spinner className="w-8 h-8" />
          <p className="font-lato text-sm font-medium text-firmato-text">
            {state.kind === "retraining" ? "Retreinando modelo..." : "Processando planilha..."}
          </p>
          <p className="font-lato text-xs text-firmato-muted text-center">
            {state.kind === "retraining"
              ? "Reconstruindo thumbnails e recarregando embeddings."
              : "Isso pode levar alguns minutos."}
          </p>
        </div>
      ) : state.kind === "success" ? (
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <CheckCircle size={22} className="text-green-500" />
            <p className="font-lato text-[15px] font-semibold text-firmato-text">
              {state.stats ? "Processamento concluído" : "Retreinamento concluído"}
            </p>
          </div>
          <div className="border-t border-firmato-border" />
          {state.stats ? (
            <div>
              <StatRow label="Total de linhas" value={state.stats.total} />
              <StatRow label="Novos produtos" value={state.stats.novos} />
              <StatRow label="Imagens atualizadas" value={state.stats.imagem_principal_atualizada} />
              <StatRow label="Secundárias processadas" value={state.stats.secundarias_processadas} />
              <StatRow label="Secundárias deletadas" value={state.stats.secundarias_deletadas} />
              <StatRow label="Pastas movidas no NAS" value={state.stats.pasta_nas_movida} />
              <StatRow label="Dados atualizados" value={state.stats.dados_atualizados} />
              <StatRow label="Ignorados (sem mudança)" value={state.stats.ignorados} />
              <StatRow label="Erros" value={state.stats.erros} />
              <StatRow label="Arquivos limpos da landing" value={state.stats.arquivos_limpos} />
            </div>
          ) : (
            <p className="font-lato text-sm text-firmato-muted">
              Thumbnails e embeddings foram recarregados com sucesso.
            </p>
          )}
          <div className="flex gap-3 pt-2">
            {state.stats && (
              <Button
                variant="outline"
                className="flex-1"
                onClick={() => window.open("/api/catalog/latest-log", "_blank")}
              >
                <FileText size={14} />
                Baixar Log
              </Button>
            )}
            <Button variant="solid" className="flex-1" onClick={handleClose}>
              Fechar
            </Button>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Drop zone */}
          <div
            onClick={() => fileRef.current?.click()}
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
            className={`border rounded-sm cursor-pointer transition-colors ${
              dragging
                ? "border-firmato-accent bg-firmato-accent/5"
                : "border-dashed border-firmato-border-dark bg-firmato-bg hover:border-firmato-accent"
            }`}
          >
            <div className="flex flex-col items-center gap-2 py-7 px-4">
              {file ? (
                <>
                  <FileSpreadsheet size={30} className="text-firmato-accent" />
                  <p className="font-lato text-sm font-medium text-firmato-text">
                    {file.name}
                  </p>
                  <p className="font-lato text-xs text-firmato-muted">
                    Clique para trocar o arquivo
                  </p>
                </>
              ) : (
                <>
                  <FileUp size={30} className="text-firmato-border-dark" />
                  <p className="font-lato text-sm font-medium text-firmato-text">
                    Arraste ou clique para selecionar
                  </p>
                  <p className="font-lato text-xs text-firmato-muted">
                    Aceita .xlsx e .xlsm
                  </p>
                </>
              )}
            </div>
          </div>
          <input
            ref={fileRef}
            type="file"
            accept=".xlsx,.xlsm"
            className="hidden"
            onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); e.target.value = ""; }}
          />

          {state.kind === "error" && (
            <p className="font-lato text-xs text-red-600">{state.message}</p>
          )}

          <div className="flex gap-3">
            <Button variant="solid" className="flex-1" onClick={doUpload}>
              <Upload size={14} />
              Realizar Upload
            </Button>
            <Button variant="outline" className="flex-1" onClick={doRetrain}>
              <Brain size={14} />
              Retreinar Modelo
            </Button>
          </div>
        </div>
      )}
    </Modal>
  );
}
