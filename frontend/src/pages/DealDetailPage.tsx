import React, { useEffect, useMemo, useState } from 'react';
import { api } from '../api/client';
import type { DealDetail, ExtractedTerms } from '../api/types';

const emptyTerms: ExtractedTerms = {
  loan_amount: null,
  currency: 'AUD',
  term_months: null,
  interest_rate_pct: null,
  fees: [],
  collateral_type: 'unknown',
  collateral_value_appraised: null,
  collateral_value_as_is: null,
  collateral_value_stressed: null,
  lien_position: 'unknown',
  jurisdiction: null,
  enforcement_timeline_months: null,
  repayment_source: null,
  repayment_timeline_months: null,
  key_conditions: [],
  notes: null,
  citations: {}
};

export function DealDetailPage({ dealId, onBack }: { dealId: string; onBack: () => void }) {
  const [detail, setDetail] = useState<DealDetail | null>(null);
  const [terms, setTerms] = useState<ExtractedTerms>(emptyTerms);
  const [confirmed, setConfirmed] = useState<Record<string, boolean>>({});
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  async function refresh() {
    setError(null);
    const d = await api.dealDetail(dealId);
    setDetail(d);
    setTerms(d.terms || emptyTerms);
    setConfirmed(d.confirmed_fields || {});
  }

  useEffect(() => {
    refresh().catch((e) => setError(String(e)));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dealId]);

  const requiredDraftReady = useMemo(() => {
    const okLoan = !!confirmed.loan_amount;
    const okLien = !!confirmed.lien_position;
    const okRepay = !!confirmed.repayment_source;
    const okColl = !!confirmed.collateral_value_stressed || !!confirmed.collateral_value_appraised;
    return okLoan && okLien && okRepay && okColl;
  }, [confirmed]);

  function updateField<K extends keyof ExtractedTerms>(k: K, v: ExtractedTerms[K]) {
    setTerms((t) => ({ ...t, [k]: v }));
  }

  if (!detail) {
    return <div style={{ padding: 24 }}>{error ? <pre style={{ color: 'crimson' }}>{error}</pre> : 'Loading...'}</div>;
  }

  return (
    <div style={{ maxWidth: 1100, margin: '24px auto', fontFamily: 'system-ui, sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12 }}>
        <div>
          <h2 style={{ margin: 0 }}>{detail.deal.name}</h2>
          <div style={{ fontSize: 12, opacity: 0.7 }}>{detail.deal.id}</div>
        </div>
        <button onClick={onBack} style={{ padding: '8px 12px' }}>
          Back
        </button>
      </div>

      {error ? <pre style={{ color: 'crimson' }}>{error}</pre> : null}
      {busy ? <div style={{ marginTop: 10, opacity: 0.7 }}>Working: {busy}</div> : null}

      <hr style={{ margin: '18px 0' }} />

      <h3>Documents</h3>
      <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
        <input
          type="file"
          accept=".pdf,.docx,.txt"
          onChange={async (e) => {
            const f = e.target.files?.[0];
            if (!f) return;
            try {
              setBusy('Uploading');
              await api.uploadDocument(dealId, f);
              await refresh();
            } catch (err) {
              setError(String(err));
            } finally {
              setBusy(null);
              e.currentTarget.value = '';
            }
          }}
        />
        <button
          onClick={async () => {
            try {
              setBusy('Extracting');
              await api.extractTerms(dealId);
              await refresh();
            } catch (err) {
              setError(String(err));
            } finally {
              setBusy(null);
            }
          }}
          style={{ padding: '8px 12px' }}
        >
          Extract
        </button>
        <button
          onClick={async () => {
            try {
              setBusy('Analyzing');
              await api.analyze(dealId);
              await refresh();
            } catch (err) {
              setError(String(err));
            } finally {
              setBusy(null);
            }
          }}
          style={{ padding: '8px 12px' }}
        >
          Analyze
        </button>
        <button
          disabled={!requiredDraftReady}
          onClick={async () => {
            try {
              setBusy('Drafting');
              await api.draft(dealId);
              await refresh();
            } catch (err) {
              setError(String(err));
            } finally {
              setBusy(null);
            }
          }}
          style={{ padding: '8px 12px' }}
        >
          Draft
        </button>
        <button
          onClick={async () => {
            try {
              setBusy('Exporting');
              const blob = await api.exportPdf(dealId);
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = `deal-${dealId}.pdf`;
              a.click();
              URL.revokeObjectURL(url);
            } catch (err) {
              setError(String(err));
            } finally {
              setBusy(null);
            }
          }}
          style={{ padding: '8px 12px' }}
        >
          Export PDF
        </button>
      </div>

      <div style={{ marginTop: 12, display: 'grid', gap: 8 }}>
        {detail.documents.map((doc) => (
          <div key={doc.id} style={{ border: '1px solid #eee', padding: 10, borderRadius: 8 }}>
            <div style={{ fontWeight: 700 }}>{doc.filename}</div>
            <div style={{ fontSize: 12, opacity: 0.7 }}>{doc.sha256}</div>
          </div>
        ))}
      </div>

      <hr style={{ margin: '18px 0' }} />

      <h3>Extracted Terms (editable)</h3>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        <Field label="Loan amount" value={terms.loan_amount ?? ''} onChange={(v) => updateField('loan_amount', v ? Number(v) : null)} />
        <Confirm label="Confirm" checked={!!confirmed.loan_amount} onChange={(c) => setConfirmed((x) => ({ ...x, loan_amount: c }))} />

        <Field label="Collateral (type)" value={terms.collateral_type || ''} onChange={(v) => updateField('collateral_type', v)} />
        <Field label="Lien position" value={terms.lien_position} onChange={(v) => updateField('lien_position', v as any)} />
        <Confirm label="Confirm lien" checked={!!confirmed.lien_position} onChange={(c) => setConfirmed((x) => ({ ...x, lien_position: c }))} />

        <Field
          label="Collateral value (appraised)"
          value={terms.collateral_value_appraised ?? ''}
          onChange={(v) => updateField('collateral_value_appraised', v ? Number(v) : null)}
        />
        <Confirm
          label="Confirm appraised"
          checked={!!confirmed.collateral_value_appraised}
          onChange={(c) => setConfirmed((x) => ({ ...x, collateral_value_appraised: c }))}
        />

        <Field
          label="Collateral value (stressed)"
          value={terms.collateral_value_stressed ?? ''}
          onChange={(v) => updateField('collateral_value_stressed', v ? Number(v) : null)}
        />
        <Confirm
          label="Confirm stressed"
          checked={!!confirmed.collateral_value_stressed}
          onChange={(c) => setConfirmed((x) => ({ ...x, collateral_value_stressed: c }))}
        />

        <Field label="Repayment source" value={terms.repayment_source ?? ''} onChange={(v) => updateField('repayment_source', v || null)} />
        <Confirm label="Confirm repay" checked={!!confirmed.repayment_source} onChange={(c) => setConfirmed((x) => ({ ...x, repayment_source: c }))} />
      </div>

      <div style={{ marginTop: 12, display: 'flex', gap: 10 }}>
        <button
          onClick={async () => {
            try {
              setBusy('Saving terms');
              await api.updateTerms(dealId, terms, confirmed);
              await refresh();
            } catch (err) {
              setError(String(err));
            } finally {
              setBusy(null);
            }
          }}
          style={{ padding: '10px 14px' }}
        >
          Save / Confirm
        </button>
        <div style={{ opacity: 0.7, alignSelf: 'center' }}>
          Draft ready: <b>{requiredDraftReady ? 'Yes' : 'No'}</b>
        </div>
      </div>

      <hr style={{ margin: '18px 0' }} />

      <h3>Analysis</h3>
      {detail.analysis ? (
        <div style={{ border: '1px solid #eee', padding: 12, borderRadius: 8 }}>
          <div>
            Overall triage: <b>{detail.analysis.overall_triage}</b>
          </div>
          <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(detail.analysis, null, 2)}</pre>
        </div>
      ) : (
        <div style={{ opacity: 0.7 }}>(none)</div>
      )}

      <hr style={{ margin: '18px 0' }} />

      <h3>IC Draft</h3>
      {detail.draft ? (
        <div style={{ border: '1px solid #eee', padding: 12, borderRadius: 8 }}>
          <div style={{ fontWeight: 700 }}>{detail.draft.banner}</div>
          <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(detail.draft, null, 2)}</pre>
        </div>
      ) : (
        <div style={{ opacity: 0.7 }}>(none)</div>
      )}
    </div>
  );
}

function Field({ label, value, onChange }: { label: string; value: string | number; onChange: (v: string) => void }) {
  return (
    <label style={{ display: 'grid', gap: 6 }}>
      <div style={{ fontSize: 12, opacity: 0.75 }}>{label}</div>
      <input value={value} onChange={(e) => onChange(e.target.value)} style={{ padding: 10, border: '1px solid #ccc', borderRadius: 8 }} />
    </label>
  );
}

function Confirm({ label, checked, onChange }: { label: string; checked: boolean; onChange: (c: boolean) => void }) {
  return (
    <label style={{ display: 'flex', gap: 8, alignItems: 'center', paddingTop: 22 }}>
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} />
      <span style={{ fontSize: 12, opacity: 0.75 }}>{label}</span>
    </label>
  );
}
