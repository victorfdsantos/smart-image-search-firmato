"use client";
import { X } from "lucide-react";
import { FILTER_FIELDS } from "@/lib/constants";
import type { FilterMap } from "@/types";
import { Button } from "@/components/ui/Button";

interface AppliedFiltersProps {
  filters: FilterMap;
  onRemove: (field: string, value: string) => void;
  onClearAll: () => void;
}

export function AppliedFilters({ filters, onRemove, onClearAll }: AppliedFiltersProps) {
  const hasAny = Object.values(filters).some((v) => v.length > 0);
  if (!hasAny) return null;

  return (
    <div className="space-y-2 pt-2">
      {FILTER_FIELDS.map(({ key, label }) => {
        const vals = filters[key];
        if (!vals?.length) return null;
        return (
          <div key={key} className="flex flex-wrap items-center gap-1.5">
            <span className="font-lato text-[11px] font-semibold text-firmato-muted">
              {label}:
            </span>
            {vals.map((v) => (
              <span
                key={v}
                className="inline-flex items-center gap-1 px-2 py-0.5 rounded-sm bg-firmato-accent-light/20 border border-firmato-accent-light font-lato text-[11px] text-firmato-accent"
              >
                {v}
                <button
                  onClick={() => onRemove(key, v)}
                  className="text-firmato-muted hover:text-firmato-accent transition-colors"
                >
                  <X size={10} />
                </button>
              </span>
            ))}
          </div>
        );
      })}
      <Button
        variant="ghost"
        size="sm"
        onClick={onClearAll}
        className="text-firmato-muted text-[11px] px-1.5"
      >
        <X size={12} />
        Limpar filtros
      </Button>
    </div>
  );
}
