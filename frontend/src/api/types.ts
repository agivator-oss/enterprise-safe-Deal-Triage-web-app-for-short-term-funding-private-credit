export type DealOut = {
  id: string;
  name: string;
  created_at: string;
};

export type DocumentOut = {
  id: number;
  deal_id: string;
  filename: string;
  sha256: string;
  created_at: string;
};

export type ExtractedTerms = {
  loan_amount: number | null;
  currency: string;
  term_months: number | null;
  interest_rate_pct: number | null;
  fees: { type: string; pct_or_amount: string }[];
  collateral_type: string;
  collateral_value_appraised: number | null;
  collateral_value_as_is: number | null;
  collateral_value_stressed: number | null;
  lien_position: 'first' | 'second' | 'unsecured' | 'unknown';
  jurisdiction: string | null;
  enforcement_timeline_months: number | null;
  repayment_source: string | null;
  repayment_timeline_months: number | null;
  key_conditions: string[];
  notes: string | null;
  citations: Record<string, string[] | null>;
};

export type AnalysisResponse = {
  metrics: Record<string, number | null>;
  overall_triage: 'Strong' | 'Borderline' | 'Weak';
  risk_flags: { rule_id: string; severity: string; message: string }[];
  diligence_questions: string[];
};

export type ICDraft = {
  banner: string;
  ic_summary_3_lines: string;
  top_risks_ranked: string[];
  mitigants_or_conditions: string[];
  diligence_questions: string[];
  what_changes_my_mind: string;
};

export type DealDetail = {
  deal: DealOut;
  documents: DocumentOut[];
  terms: ExtractedTerms | null;
  citations: Record<string, string[] | null> | null;
  confirmed_fields: Record<string, boolean> | null;
  analysis: AnalysisResponse | null;
  draft: ICDraft | null;
};
