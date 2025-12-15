import type { AnalysisResponse, DealDetail, DealOut, ExtractedTerms, ICDraft } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      ...(init?.headers || {}),
      'x-dev-actor': 'dev.user@local'
    }
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  listDeals: () => http<DealOut[]>('/deals'),
  createDeal: (name: string) => http<DealOut>('/deals', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ name }) }),
  dealDetail: (dealId: string) => http<DealDetail>(`/deals/${encodeURIComponent(dealId)}`),

  uploadDocument: async (dealId: string, file: File) => {
    const fd = new FormData();
    fd.append('file', file);
    return http<{ document_id: number; filename: string; sha256: string }>(`/deals/${encodeURIComponent(dealId)}/documents`, { method: 'POST', body: fd });
  },

  extractTerms: (dealId: string) => http<ExtractedTerms>(`/deals/${encodeURIComponent(dealId)}/extract`, { method: 'POST' }),
  updateTerms: (dealId: string, terms: ExtractedTerms, confirmed_fields: Record<string, boolean>) =>
    http<{ status: string }>(`/deals/${encodeURIComponent(dealId)}/terms`, {
      method: 'PUT',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ terms, confirmed_fields })
    }),
  analyze: (dealId: string) => http<AnalysisResponse>(`/deals/${encodeURIComponent(dealId)}/analyze`, { method: 'POST' }),
  draft: (dealId: string) => http<ICDraft>(`/deals/${encodeURIComponent(dealId)}/draft`, { method: 'POST' }),
  exportPdf: async (dealId: string) => {
    const res = await fetch(`${API_BASE_URL}/deals/${encodeURIComponent(dealId)}/export`, { headers: { 'x-dev-actor': 'dev.user@local' } });
    if (!res.ok) throw new Error('Export failed');
    return await res.blob();
  }
};
