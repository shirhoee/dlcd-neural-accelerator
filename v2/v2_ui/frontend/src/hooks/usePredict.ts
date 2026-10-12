import { useState, useCallback } from 'react';
import type { PredictResponse } from '../types/api.ts';

const API_BASE_URL = 'http://127.0.0.1:8000';

export function usePredict() {
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const runPrediction = useCallback(async (image: number[][]) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image }),
      });
      if (!res.ok) {
        throw new Error(`Server returned HTTP ${res.status}`);
      }
      const data: PredictResponse = await res.json();
      setResult(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Unknown error';
      setError(msg);
      alert('Backend error: ' + msg);
    } finally {
      setLoading(false);
    }
  }, []);

  const clearResult = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return {
    result,
    loading,
    error,
    runPrediction,
    clearResult,
  };
}
