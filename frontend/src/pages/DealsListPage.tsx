import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { DealOut } from '../api/types';

export function DealsListPage({ onOpenDeal }: { onOpenDeal: (id: string) => void }) {
  const [deals, setDeals] = useState<DealOut[]>([]);
  const [name, setName] = useState('');
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    setError(null);
    try {
      setDeals(await api.listDeals());
    } catch (e) {
      setError(String(e));
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  return (
    <div style={{ maxWidth: 980, margin: '24px auto', fontFamily: 'system-ui, sans-serif' }}>
      <h2>Deal Triage</h2>
      <p>Decision support only. Not investment advice.</p>

      <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="New deal name" style={{ flex: 1, padding: 10 }} />
        <button
          onClick={async () => {
            const created = await api.createDeal(name || 'Untitled deal');
            onOpenDeal(created.id);
          }}
          style={{ padding: '10px 14px' }}
        >
          Create
        </button>
        <button onClick={refresh} style={{ padding: '10px 14px' }}>
          Refresh
        </button>
      </div>

      {error ? <pre style={{ color: 'crimson' }}>{error}</pre> : null}

      <h3 style={{ marginTop: 24 }}>Deals</h3>
      <div style={{ display: 'grid', gap: 10 }}>
        {deals.map((d) => (
          <div key={d.id} style={{ border: '1px solid #ddd', padding: 12, borderRadius: 8 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12 }}>
              <div>
                <div style={{ fontWeight: 700 }}>{d.name}</div>
                <div style={{ fontSize: 12, opacity: 0.7 }}>{d.id}</div>
              </div>
              <button onClick={() => onOpenDeal(d.id)} style={{ padding: '8px 12px' }}>
                Open
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
