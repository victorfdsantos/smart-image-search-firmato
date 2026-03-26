"use client";
import { useEffect, useRef, useState } from "react";
import { ChevronRight, ArrowLeft, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { FILTER_FIELDS } from "@/lib/constants";
import { getFilterOptions } from "@/lib/api";
import type { FilterMap } from "@/types";
import { Spinner } from "@/components/ui/Spinner";

interface FilterDropdownProps {
  open: boolean;
  onClose: () => void;
  applied: FilterMap;
  onToggle: (field: string, value: string) => void;
}

type Mode = "fields" | "tags";

export function FilterDropdown({
  open,
  onClose,
  applied,
  onToggle,
}: FilterDropdownProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [mode, setMode] = useState<Mode>("fields");
  const [activeField, setActiveField] = useState("");
  const [activeLabel, setActiveLabel] = useState("");
  const [options, setOptions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");

  useEffect(() => {
    if (!open) {
      setMode("fields");
      setActiveField("");
      setActiveLabel("");
      setOptions([]);
      setSearch("");
    }
  }, [open]);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) onClose();
    };
    if (open) document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open, onClose]);

  const selectField = async (field: string, label: string) => {
    setActiveField(field);
    setActiveLabel(label);
    setMode("tags");
    setSearch("");
    setLoading(true);
    const data = await getFilterOptions(applied);
    setOptions(data.options[field] ?? []);
    setLoading(false);
  };

  const filtered = search
    ? options.filter((v) => v.toLowerCase().includes(search.toLowerCase()))
    : options;

  const selected = applied[activeField] ?? [];

  if (!open) return null;

  return (
    <div
      ref={ref}
      className="absolute top-[calc(100%+4px)] left-0 right-0 bg-firmato-surface border border-firmato-border-dark shadow-lg z-50 max-h-80 overflow-y-auto animate-slide-down"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-firmato-border">
        {mode === "tags" ? (
          <button
            onClick={() => setMode("fields")}
            className="flex items-center gap-2 text-firmato-muted hover:text-firmato-text transition-colors"
          >
            <ArrowLeft size={14} />
            <span className="font-lato text-xs font-semibold text-firmato-accent">
              {activeLabel}
            </span>
          </button>
        ) : (
          <span className="font-lato text-xs font-semibold text-firmato-muted uppercase tracking-wider">
            Selecionar campo
          </span>
        )}
        <button
          onClick={onClose}
          className="text-firmato-muted hover:text-firmato-text transition-colors"
        >
          <X size={14} />
        </button>
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex justify-center py-4">
          <Spinner />
        </div>
      ) : mode === "fields" ? (
        <div>
          {FILTER_FIELDS.map(({ key, label }) => (
            <button
              key={key}
              onClick={() => selectField(key, label)}
              className="w-full flex items-center justify-between px-3 py-2 text-left hover:bg-firmato-bg transition-colors"
            >
              <span className="font-lato text-sm text-firmato-text">{label}</span>
              <ChevronRight size={14} className="text-firmato-muted" />
            </button>
          ))}
        </div>
      ) : (
        <div className="p-3 space-y-3">
          <input
            autoFocus
            placeholder="Buscar..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full border border-firmato-border-dark rounded-sm bg-firmato-bg font-lato text-sm px-2.5 py-1.5 text-firmato-text focus:outline-none focus:border-firmato-accent"
          />
          {filtered.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {filtered.map((v) => {
                const isSel = selected.includes(v);
                return (
                  <button
                    key={v}
                    onClick={() => onToggle(activeField, v)}
                    className={cn(
                      "font-lato text-xs px-2.5 py-1 rounded-sm border transition-all",
                      isSel
                        ? "bg-firmato-accent-light border-firmato-accent-light text-white"
                        : "bg-firmato-bg border-firmato-border-dark text-firmato-text hover:border-firmato-accent-light"
                    )}
                  >
                    {v}
                  </button>
                );
              })}
            </div>
          ) : (
            <p className="font-lato text-xs text-firmato-muted">Nenhum resultado</p>
          )}
        </div>
      )}
    </div>
  );
}
