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
  review_tag: string;
  review_tags: string[];
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
  ai_contextual_fit?: AIContextualFit;
  ai_recruiter_explanation?: AIRecruiterExplanation;
  hidden_gem_candidate?: boolean;
  hidden_gem_reason?: string;
  hidden_gem_evidence?: string[];
  signal_fusion_summary?: SignalFusionSummary;
};

export type AIMetadata = {
  gemini_enabled: boolean;
  model_used: string;
  fallback_used: boolean;
  generated_at: string;
};

export type AIJDInsight = AIMetadata & {
  role_archetype: string;
  must_have_skills: string[];
  semantic_skill_synonyms: string[];
  strong_success_signals: string[];
  seniority_expectations: string[];
  domain_expectations: string[];
  negative_signals: string[];
  hiring_constraints: string[];
  interview_focus_areas: string[];
  confidence: number;
  missing_information: string[];
};

export type AIContextualFit = AIMetadata & {
  contextual_fit_score: number;
  semantic_fit_reason: string;
  hidden_strengths: string[];
  weak_context_signals: string[];
  evidence_supported: string[];
  evidence_missing: string[];
  risk_notes: string[];
  recommended_interview_checks: string[];
};

export type AIRecruiterExplanation = AIMetadata & {
  executive_summary: string;
  why_shortlisted: string[];
  strongest_evidence: string[];
  hidden_strengths: string[];
  concerns: string[];
  missing_proof: string[];
  interview_questions: string[];
  final_recruiter_note: string;
};

export type SignalFusionSummary = {
  role_fit: string;
  proof_strength: string;
  contextual_relevance: string;
  activity_or_behavioral_signal: string;
  hireability: string;
  risk: string;
  summary: string;
};

export type RoleRequirementMatrix = {
  role_title?: string;
  must_have_skills?: string[];
  strong_signal_skills?: string[];
  good_to_have_skills?: string[];
  seniority_expectations?: string;
  domain_expectations?: string;
  production_expectations?: string;
  leadership_expectations?: string;
  location_requirements?: string;
  availability_requirements?: string;
  risk_blockers?: string[];
};

export type RankingPayload = {
  metadata: {
    project: string;
    candidate_count: number;
    top_n: number;
    runtime_seconds: number;
    job_supplied: boolean;
    ranking_uses_role_relevant_evidence_only: boolean;
    input_pipeline?: {
      candidate_file?: string;
      candidate_file_type?: string;
      candidate_records_loaded?: number;
      job_source?: string;
      top_n_requested?: number;
      top_n_emitted?: number;
      supported_candidate_inputs?: string[];
      supported_job_inputs?: string[];
    };
  };
  role_requirements: RoleRequirementMatrix;
  rankings: RankingRow[];
  ai_jd_insight?: AIJDInsight;
};

export type TrustAuditPayload = {
  total_candidates: number;
  shortlisted_candidates: number;
  average_confidence: number;
  average_proof_score: number;
  high_risk_candidate_count: number;
  candidates_with_missing_evidence: number;
  keyword_stuffing_or_weak_proof_count: number;
  location_or_availability_risk_count: number;
  low_confidence_count: number;
  proxy_evaluation_warning: string;
  score_distribution: Record<string, number>;
  risk_severity_counts: Record<string, number>;
  missing_evidence_categories: Record<string, number>;
  proof_vs_claim_summary: Record<string, number>;
  ai_summary?: AIMetadata & {
    summary: string;
    verification_priorities: string[];
  };
};

export type ComparisonCandidate = {
  candidate_id: string;
  final_score: number;
  fit_score: number;
  proof_score: number;
  confidence_score: number;
  hireability_score: number;
  risk_score: number;
};

export type ComparisonPayload = {
  candidate_a: ComparisonCandidate;
  candidate_b: ComparisonCandidate;
  why_a_ranks_above_b: string;
  where_b_is_stronger: string[];
  score_component_differences: Record<string, number>;
  evidence_differences: {
    a_unique_evidence: string[];
    b_unique_evidence: string[];
    shared_evidence: string[];
    a_missing: string[];
    b_missing: string[];
  };
  risks_for_a: RiskItem[];
  risks_for_b: RiskItem[];
  what_to_verify: string[];
  ai_semantic_comparison?: AIMetadata & {
    summary: string;
    hidden_strengths_difference: string[];
    risk_difference: string[];
    interview_checks: string[];
  };
};
