import { useState, useCallback } from 'react';
import type { PredictResponse, V1PredictResponse, ComparePredictResponse } from '../types/api';

const API_BASE_URL = 'http://127.0.0.1:8000';

export function usePredict() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const predictV2 = useCallback(async (image: number[][]): Promise<PredictResponse> => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image }),
      });
      if (!res.ok) {
        throw new Error(`V2 Server error: HTTP ${res.status}`);
      }
      return await res.json();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Unknown error';
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const predictV1 = useCallback(async (image: number[][]): Promise<V1PredictResponse> => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/predict/v1`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image }),
      });
      if (!res.ok) {
        throw new Error(`V1 Server error: HTTP ${res.status}`);
      }
      return await res.json();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Unknown error';
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const predictCompare = useCallback(async (image: number[][]): Promise<ComparePredictResponse> => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/predict/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image }),
      });
      if (!res.ok) {
        throw new Error(`Compare Server error: HTTP ${res.status}`);
      }
      return await res.json();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Unknown error';
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    predictV2,
    predictV1,
    predictCompare,
  };
}
