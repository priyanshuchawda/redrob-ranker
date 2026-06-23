import type { RankingPayload } from "./types";

export const demoPayload: RankingPayload = {
  metadata: {
    project: "EvidenceGraph Ranker",
    candidate_count: 4,
    top_n: 4,
    runtime_seconds: 0,
    job_supplied: true,
    ranking_uses_role_relevant_evidence_only: true
  },
  role_requirements: {
    role_title: "Senior AI Engineer"
  },
  rankings: [
    {
      rank: 1,
      candidate_id: "CAND_DEMO_001",
      final_score: 100,
      fit_score: 84,
      proof_score: 82,
      confidence_score: 91,
      hireability_score: 74,
      risk_score: 0,
      main_reason: "Senior AI Engineer has role-relevant evidence in dual encoder retrieval, reranking, and ranking metrics.",
      reasons: {
        why_shortlisted: "Career-backed production search and ranking evidence.",
        best_evidence: ["Owned and shipped production semantic search, two-tower candidate matching, cross encoder reranking, NDCG evaluation."],
        main_concern: "No major concern from supplied fields.",
        why_not_ranked_higher: "Already near the top; ranking depends on fine-grained evidence strength.",
        interview_focus: ["Validate retrieval architecture and ranking metrics."],
        hiring_feasibility_summary: "Bangalore, India; strong availability signals; good logistics fit",
        risk_summary: "No structured risk flags from supplied fields."
      },
      risks: [],
      missing_evidence: [],
      interview_focus: ["Validate retrieval architecture and ranking metrics."],
      evidence_ledger: {
        positive_evidence: [
          {
            evidence_type: "career_evidence",
            concept: "semantic search",
            source_field: "career_history[0].description",
            snippet: "Owned and shipped production semantic search, two-tower candidate matching, cross encoder reranking, NDCG evaluation.",
            strength: "high",
            confidence: 0.85,
            polarity: "positive",
            claim_or_proof: "strong_proof",
            score_impact: 2.5
          }
        ],
        negative_evidence: [],
        missing_evidence: [],
        risk_flags: []
      },
      components: { role: 29, retrieval: 24, ranking: 20, evaluation: 12, skills: 18, risk: 0 }
    },
    {
      rank: 2,
      candidate_id: "CAND_DEMO_002",
      final_score: 64,
      fit_score: 42,
      proof_score: 35,
      confidence_score: 54,
      hireability_score: 67,
      risk_score: 10,
      main_reason: "ML Platform Engineer has strong production backend proof but weaker ranking evidence.",
      reasons: {
        why_shortlisted: "Useful adjacent ML platform and FastAPI production experience.",
        best_evidence: ["Built Python APIs, Kubernetes deployments, model serving, monitoring, and data pipelines."],
        main_concern: "Missing evidence: career-backed ranking proof",
        why_not_ranked_higher: "Could rank higher with clearer retrieval/ranking evidence.",
        interview_focus: ["Ask whether platform work included ranking or retrieval ownership."],
        hiring_feasibility_summary: "Pune, India; good logistics fit",
        risk_summary: "missing important evidence (low)"
      },
      risks: [{ risk_type: "missing important evidence", severity: "low", evidence: "ranking proof unclear", score_impact: -2, explanation: "Ranking ownership is not explicit." }],
      missing_evidence: ["career-backed ranking proof"],
      interview_focus: ["Ask whether platform work included ranking or retrieval ownership."],
      evidence_ledger: { positive_evidence: [], negative_evidence: [], missing_evidence: ["career-backed ranking proof"], risk_flags: [] },
      components: { role: 7, retrieval: 0, ranking: 0, evaluation: 0, skills: 14, production: 10, risk: 5 }
    },
    {
      rank: 3,
      candidate_id: "CAND_DEMO_004",
      final_score: 58,
      fit_score: 70,
      proof_score: 72,
      confidence_score: 80,
      hireability_score: 32,
      risk_score: 84,
      main_reason: "Strong search relevance evidence but target-location risk.",
      reasons: {
        why_shortlisted: "Search relevance evidence is strong.",
        best_evidence: ["Shipped hybrid search, ranking model evaluation, A/B testing, and retrieval quality dashboards."],
        main_concern: "location mismatch: Location does not match the target geography.",
        why_not_ranked_higher: "Risk pressure from location mismatch reduces rank confidence.",
        interview_focus: ["Clarify relocation feasibility."],
        hiring_feasibility_summary: "London; logistics risk",
        risk_summary: "location mismatch (high)"
      },
      risks: [{ risk_type: "location mismatch", severity: "high", evidence: "outside India", score_impact: -12, explanation: "Location does not match the target geography." }],
      missing_evidence: [],
      interview_focus: ["Clarify relocation feasibility."],
      evidence_ledger: { positive_evidence: [], negative_evidence: [], missing_evidence: [], risk_flags: [] },
      components: { role: 29, retrieval: 18, ranking: 17, evaluation: 10, logistics: 0, risk: 42 }
    },
    {
      rank: 4,
      candidate_id: "CAND_DEMO_003",
      final_score: 28,
      fit_score: 20,
      proof_score: 8,
      confidence_score: 21,
      hireability_score: 36,
      risk_score: 62,
      main_reason: "AI claims are demo-heavy and production retrieval proof is weak.",
      reasons: {
        why_shortlisted: "Relevant AI keywords appear, but proof is weak.",
        best_evidence: ["Candidate lists Python in skills."],
        main_concern: "weak proof behind strong claims: AI claims appear demo-heavy.",
        why_not_ranked_higher: "Risk pressure from weak proof behind strong claims reduces rank confidence.",
        interview_focus: ["Ask for shipped production examples."],
        hiring_feasibility_summary: "Bangalore, India",
        risk_summary: "weak proof behind strong claims (high)"
      },
      risks: [{ risk_type: "weak proof behind strong claims", severity: "high", evidence: "generic AI without shipped retrieval evidence", score_impact: -12, explanation: "AI claims appear demo-heavy." }],
      missing_evidence: ["career-backed retrieval proof", "career-backed ranking proof"],
      interview_focus: ["Ask for shipped production examples."],
      evidence_ledger: { positive_evidence: [], negative_evidence: [], missing_evidence: ["career-backed retrieval proof"], risk_flags: [] },
      components: { role: 0, retrieval: 0, ranking: 0, evaluation: 0, skills: 2, risk: 31 }
    }
  ]
};
