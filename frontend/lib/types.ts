export type RiskItem = {
  risk_type: string;
  severity: "high" | "medium" | "low" | string;
  evidence: string;
  score_impact: number;
  explanation: string;
};

export type EvidenceItem = {
  evidence_type: string;
  concept: string;
  source_field: string;
  snippet: string;
  strength: string;
  confidence: number;
  polarity: string;
  claim_or_proof: string;
  score_impact: number;
};

export type RankingRow = {
  rank: number;
  candidate_id: string;
  final_score: number;
  fit_score: number;
  proof_score: number;
  confidence_score: number;
  hireability_score: number;
  risk_score: number;
  main_reason: string;
  reasons: Record<string, string | string[]>;
  risks: RiskItem[];
  missing_evidence: string[];
  interview_focus: string[];
  evidence_ledger: {
    positive_evidence: EvidenceItem[];
    negative_evidence: EvidenceItem[];
    missing_evidence: string[];
    risk_flags: RiskItem[];
  };
  components: Record<string, number>;
};

export type RankingPayload = {
  metadata: {
    project: string;
    candidate_count: number;
    top_n: number;
    runtime_seconds: number;
    job_supplied: boolean;
    ranking_uses_role_relevant_evidence_only: boolean;
  };
  role_requirements: Record<string, unknown>;
  rankings: RankingRow[];
};
