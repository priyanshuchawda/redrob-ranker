"use client";

import { useEffect, useState } from "react";
import { fetchRanking } from "@/lib/api";
import type { RankingPayload } from "@/lib/types";

export function useRankingData() {
  const [payload, setPayload] = useState<RankingPayload | null>(null);
  const [source, setSource] = useState<"api" | "demo">("demo");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    fetchRanking()
      .then((result) => {
        if (!mounted) return;
        setPayload(result.payload);
        setSource(result.source);
      })
      .catch((err: Error) => {
        if (!mounted) return;
        setError(err.message);
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, []);

  return { payload, source, loading, error, setPayload };
}
