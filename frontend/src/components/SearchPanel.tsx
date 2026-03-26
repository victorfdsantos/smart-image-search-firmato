"use client";
import { useEffect, useRef, useState } from "react";
import { Search, Upload, X, Plus, Clock, ArrowUpRight } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { FilterDropdown } from "@/components/FilterDropdown";
import { AppliedFilters } from "@/components/AppliedFilters";
import type { FilterMap } from "@/types";
import { cn } from "@/lib/utils";

const HISTORY_KEY = "firmato_search_history";
const MAX_HISTORY = 8;

function getHistory(): string[] {
  if (typeof window === "undefined") return [];
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY) ?? "[]");
  } catch {
    return [];
  }
}

function saveHistory(term: string) {
  if (!term.trim()) return;
  const current = getHistory().filter((h) => h !== term);
  const updated = [term, ...current].slice(0, MAX_HISTORY);
  localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
}

function clearHistory() {
  localStorage.removeItem(HISTORY_KEY);
}

interface SearchPanelProps {
  searchText: string;
  onSearchChange: (text: string) => void;
  uploadedImage: string;
  onImageUpload: (file: File) => void;
  onImageClear: () => void;
  filters: FilterMap;
  onFilterToggle: (field: string, value: string) => void;
  onFilterRemove: (field: string, value: string) => void;
  onFilterClearAll: () => void;
  onClearAll: () => void;
  /** Called when a search is committed (Enter or selecting from history) */
  onSearchCommit?: (text: string) => void;
}

export function SearchPanel({
  searchText,
  onSearchChange,
  uploadedImage,
  onImageUpload,
  onImageClear,
  filters,
  onFilterToggle,
  onFilterRemove,
  onFilterClearAll,
  onClearAll,
  onSearchCommit,
}: SearchPanelProps) {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [history, setHistory] = useState<string[]>([]);
  const fileRef = useRef<HTMLInputElement>(null);
  const dropRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const historyRef = useRef<HTMLDivElement>(null);
  const [dragging, setDragging] = useState(false);

  // Load history on mount
  useEffect(() => {
    setHistory(getHistory());
  }, []);

  // Close history dropdown on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (
        historyRef.current &&
        !historyRef.current.contains(e.target as Node) &&
        !inputRef.current?.contains(e.target as Node)
      ) {
        setHistoryOpen(false);
      }
    };
    if (historyOpen) document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [historyOpen]);

  const handleFilePick = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onImageUpload(file);
    e.target.value = "";
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith("image/")) onImageUpload(file);
  };

  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && searchText.trim()) {
      saveHistory(searchText.trim());
      setHistory(getHistory());
      setHistoryOpen(false);
      onSearchCommit?.(searchText.trim());
    }
    if (e.key === "Escape") {
      setHistoryOpen(false);
    }
  };

  const handleHistorySelect = (term: string) => {
    onSearchChange(term);
    saveHistory(term);
    setHistory(getHistory());
    setHistoryOpen(false);
    onSearchCommit?.(term);
  };

  const handleHistoryClear = () => {
    clearHistory();
    setHistory([]);
    setHistoryOpen(false);
  };

  const filteredHistory = history.filter((h) =>
    searchText.trim() ? h.toLowerCase().includes(searchText.toLowerCase()) : true
  );

  return (
    <div className="space-y-4">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Search size={18} className="text-firmato-accent" />
          <h2 className="font-lato text-xl font-light text-firmato-text tracking-tight">
            Buscar Imagens
          </h2>
        </div>
        <p className="font-lato text-sm text-firmato-muted">
          Faça upload de uma imagem ou busque por texto
        </p>
      </div>

      {/* Image upload area */}
      <div
        ref={dropRef}
        onClick={() => !uploadedImage && fileRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        className={cn(
          "border rounded-sm transition-all duration-200",
          dragging
            ? "border-firmato-accent bg-firmato-accent/5"
            : "border-dashed border-firmato-border-dark bg-firmato-bg hover:border-firmato-accent hover:bg-firmato-accent/5",
          !uploadedImage && "cursor-pointer"
        )}
      >
        {uploadedImage ? (
          <div className="relative p-2">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={uploadedImage}
              alt="Uploaded"
              className="w-full h-28 object-contain"
            />
            <button
              onClick={(e) => { e.stopPropagation(); onImageClear(); }}
              className="absolute top-2 right-2 bg-black/40 hover:bg-black/60 text-white rounded-full p-0.5 transition-colors"
            >
              <X size={14} />
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2 py-5 px-4">
            <Upload size={28} className="text-firmato-border-dark" />
            <p className="font-lato text-sm font-medium text-firmato-text">
              Escolher imagem
            </p>
            <p className="font-lato text-xs text-firmato-muted">
              ou arraste e solte
            </p>
          </div>
        )}
      </div>
      <input
        ref={fileRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className="hidden"
        onChange={handleFilePick}
      />

      {/* Text search with history dropdown */}
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          placeholder="Digite sua busca..."
          value={searchText}
          onChange={(e) => {
            onSearchChange(e.target.value);
            if (e.target.value.trim() || history.length > 0) {
              setHistoryOpen(true);
            }
          }}
          onFocus={() => {
            if (history.length > 0) setHistoryOpen(true);
          }}
          onKeyDown={handleInputKeyDown}
          className="w-full border border-firmato-border-dark rounded-sm bg-firmato-surface font-lato text-sm text-firmato-text px-4 py-2.5 focus:outline-none focus:border-firmato-accent transition-colors placeholder:text-firmato-muted pr-10"
        />

        {/* Clock icon hint */}
        {history.length > 0 && !searchText && (
          <button
            onClick={() => setHistoryOpen((o) => !o)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-firmato-muted hover:text-firmato-accent transition-colors"
          >
            <Clock size={14} />
          </button>
        )}

        {/* History dropdown */}
        {historyOpen && filteredHistory.length > 0 && (
          <div
            ref={historyRef}
            className="absolute top-[calc(100%+3px)] left-0 right-0 bg-firmato-surface border border-firmato-border-dark z-50 shadow-md animate-slide-down"
            style={{ borderRadius: "2px" }}
          >
            {/* Header */}
            <div className="flex items-center justify-between px-3 py-1.5 border-b border-firmato-border">
              <div className="flex items-center gap-1.5 text-firmato-muted">
                <Clock size={11} />
                <span className="font-lato text-[10px] uppercase tracking-wider">
                  Recentes
                </span>
              </div>
              <button
                onClick={handleHistoryClear}
                className="font-lato text-[10px] text-firmato-muted hover:text-firmato-accent transition-colors"
              >
                Limpar
              </button>
            </div>

            {/* Items */}
            {filteredHistory.map((term, i) => (
              <button
                key={i}
                onClick={() => handleHistorySelect(term)}
                className="w-full flex items-center justify-between px-3 py-2 text-left hover:bg-firmato-bg transition-colors group"
              >
                <div className="flex items-center gap-2 min-w-0">
                  <Clock
                    size={11}
                    className="text-firmato-muted/50 shrink-0"
                  />
                  <span className="font-lato text-sm text-firmato-text truncate">
                    {term}
                  </span>
                </div>
                <ArrowUpRight
                  size={12}
                  className="text-firmato-muted opacity-0 group-hover:opacity-100 transition-opacity shrink-0 ml-2"
                />
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Filter button + dropdown */}
      <div className="relative">
        <Button
          variant="outline"
          className="w-full"
          onClick={() => setDropdownOpen((o) => !o)}
        >
          <Plus size={14} />
          Adicionar filtro
        </Button>
        <FilterDropdown
          open={dropdownOpen}
          onClose={() => setDropdownOpen(false)}
          applied={filters}
          onToggle={(field, value) => {
            onFilterToggle(field, value);
          }}
        />
      </div>

      {/* Applied filter chips */}
      <AppliedFilters
        filters={filters}
        onRemove={onFilterRemove}
        onClearAll={onFilterClearAll}
      />

      {/* Clear all */}
      <Button variant="outline" className="w-full" onClick={onClearAll}>
        <X size={16} />
        Limpar tudo
      </Button>
    </div>
  );
}