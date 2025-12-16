import React, { useEffect, useState } from 'react';
import { DealDetailPage } from './DealDetailPage';
import { DealsListPage } from './DealsListPage';

export function App() {
  const [dealId, setDealId] = useState<string | null>(null);

  useEffect(() => {
    const url = new URL(window.location.href);
    const id = url.searchParams.get('deal');
    if (id) setDealId(id);
  }, []);

  if (dealId) {
    return <DealDetailPage dealId={dealId} onBack={() => (window.location.href = '/')} />;
  }

  return <DealsListPage onOpenDeal={(id) => (window.location.href = `/?deal=${encodeURIComponent(id)}`)} />;
}
