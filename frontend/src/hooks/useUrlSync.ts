"use client";
import { useCallback } from "react";
import { buildSearchUrl } from "@/lib/utils";
import type { FilterMap } from "@/types";

export function useUrlSync() {
  const pushUrl = useCallback(
    (opts: {
      q?: string;
      page?: number;
      img?: string;
      filters?: FilterMap;
    }) => {
      const url = buildSearchUrl(opts);
      window.history.replaceState(null, "", url);
    },
    []
  );
  return { pushUrl };
}
