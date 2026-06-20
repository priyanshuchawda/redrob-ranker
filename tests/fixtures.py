from __future__ import annotations

from copy import deepcopy


def base_candidate(candidate_id: str = "CAND_0000001") -> dict:
    return {
        "candidate_id": candidate_id,
        "profile": {
            "anonymized_name": "Test Candidate",
            "headline": "Applied ML Engineer",
            "summary": "Builds machine learning systems for product teams.",
            "location": "Pune, Maharashtra",
            "country": "India",
            "years_of_experience": 7.0,
            "current_title": "Applied ML Engineer",
            "current_company": "Freshworks",
            "current_company_size": "1001-5000",
            "current_industry": "SaaS",
        },
        "career_history": [
            {
                "company": "Freshworks",
                "title": "Applied ML Engineer",
                "start_date": "2022-01-01",
                "end_date": None,
                "duration_months": 52,
                "is_current": True,
                "industry": "SaaS",
                "company_size": "1001-5000",
                "description": (
                    "Shipped embeddings-based hybrid search and a recommendation "
                    "ranking system to recruiters. Owned offline NDCG/MRR evaluation "
                    "and A/B testing for retrieval quality."
                ),
            },
            {
                "company": "Zomato",
                "title": "Machine Learning Engineer",
                "start_date": "2019-01-01",
                "end_date": "2021-12-31",
                "duration_months": 36,
                "is_current": False,
                "industry": "Food Delivery",
                "company_size": "1001-5000",
                "description": (
                    "Built vector search features with FAISS and Python services for "
                    "restaurant recommendations."
                ),
            },
        ],
        "education": [
            {
                "institution": "IIT Bombay",
                "degree": "B.Tech",
                "field_of_study": "Computer Science",
                "start_year": 2013,
                "end_year": 2017,
                "grade": "8.4 CGPA",
                "tier": "tier_1",
            }
        ],
        "skills": [
            {"name": "Python", "proficiency": "expert", "endorsements": 42, "duration_months": 72},
            {"name": "Machine Learning", "proficiency": "expert", "endorsements": 38, "duration_months": 70},
            {"name": "Embeddings", "proficiency": "advanced", "endorsements": 31, "duration_months": 36},
            {"name": "Vector Search", "proficiency": "advanced", "endorsements": 28, "duration_months": 36},
            {"name": "FAISS", "proficiency": "advanced", "endorsements": 17, "duration_months": 30},
            {"name": "Recommendation Systems", "proficiency": "advanced", "endorsements": 22, "duration_months": 42},
            {"name": "Learning to Rank", "proficiency": "intermediate", "endorsements": 9, "duration_months": 20},
            {"name": "MLOps", "proficiency": "advanced", "endorsements": 21, "duration_months": 44},
        ],
        "certifications": [],
        "languages": [{"language": "English", "proficiency": "professional"}],
        "redrob_signals": {
            "profile_completeness_score": 92.0,
            "signup_date": "2025-06-01",
            "last_active_date": "2026-06-05",
            "open_to_work_flag": True,
            "profile_views_received_30d": 120,
            "applications_submitted_30d": 4,
            "recruiter_response_rate": 0.82,
            "avg_response_time_hours": 18.0,
            "skill_assessment_scores": {"Python": 91.0, "Machine Learning": 88.0},
            "connection_count": 410,
            "endorsements_received": 120,
            "notice_period_days": 15,
            "expected_salary_range_inr_lpa": {"min": 32.0, "max": 48.0},
            "preferred_work_mode": "hybrid",
            "willing_to_relocate": True,
            "github_activity_score": 76.0,
            "search_appearance_30d": 260,
            "saved_by_recruiters_30d": 24,
            "interview_completion_rate": 0.94,
            "offer_acceptance_rate": 0.72,
            "verified_email": True,
            "verified_phone": True,
            "linkedin_connected": True,
        },
    }


def keyword_stuffed_candidate(candidate_id: str = "CAND_0000002") -> dict:
    candidate = deepcopy(base_candidate(candidate_id))
    candidate["profile"].update(
        {
            "headline": "Marketing Manager | AI RAG LLM Pinecone",
            "summary": "Marketing leader listing many AI tools after recent online courses.",
            "location": "Bangalore, Karnataka",
            "years_of_experience": 7.2,
            "current_title": "Marketing Manager",
            "current_company": "Acme Corp",
            "current_industry": "Manufacturing",
        }
    )
    candidate["career_history"] = [
        {
            "company": "Acme Corp",
            "title": "Marketing Manager",
            "start_date": "2019-01-01",
            "end_date": None,
            "duration_months": 89,
            "is_current": True,
            "industry": "Manufacturing",
            "company_size": "5001-10000",
            "description": "Managed brand campaigns, social content, and vendor budgets.",
        }
    ]
    candidate["skills"] = [
        {"name": name, "proficiency": "expert", "endorsements": 0, "duration_months": 0}
        for name in [
            "LLMs",
            "RAG",
            "Pinecone",
            "FAISS",
            "Vector Search",
            "Embeddings",
            "Fine-tuning LLMs",
            "LoRA",
            "Machine Learning",
            "NLP",
        ]
    ]
    return candidate


def stale_candidate(candidate_id: str = "CAND_0000003") -> dict:
    candidate = deepcopy(base_candidate(candidate_id))
    candidate["redrob_signals"].update(
        {
            "last_active_date": "2025-12-01",
            "open_to_work_flag": False,
            "recruiter_response_rate": 0.05,
            "avg_response_time_hours": 240.0,
            "notice_period_days": 120,
            "saved_by_recruiters_30d": 1,
            "interview_completion_rate": 0.42,
            "offer_acceptance_rate": -1,
        }
    )
    return candidate


def plain_language_matching_candidate(candidate_id: str = "CAND_0000004") -> dict:
    candidate = deepcopy(base_candidate(candidate_id))
    candidate["profile"].update(
        {
            "headline": "Lead AI Engineer building relevance systems",
            "summary": (
                "Senior engineer building systems that connect users with relevant "
                "information at scale. Strong product judgment and evaluation habits."
            ),
            "current_title": "Lead AI Engineer",
            "current_company": "Sarvam AI",
            "current_industry": "AI/ML",
            "location": "Delhi, Delhi",
        }
    )
    candidate["career_history"] = [
        {
            "company": "Sarvam AI",
            "title": "Lead AI Engineer",
            "start_date": "2023-01-01",
            "end_date": None,
            "duration_months": 38,
            "is_current": True,
            "industry": "AI/ML",
            "company_size": "201-500",
            "description": (
                "Owned the search and discovery experience end-to-end. Built the "
                "matching layer that decides what to surface for each user intent, "
                "with evaluation methodology tied to online engagement."
            ),
        },
        {
            "company": "Verloop.io",
            "title": "Staff Machine Learning Engineer",
            "start_date": "2019-01-01",
            "end_date": "2022-12-31",
            "duration_months": 48,
            "is_current": False,
            "industry": "Conversational AI",
            "company_size": "201-500",
            "description": (
                "Overhauled the matching layer from hand-tuned heuristics to explicit "
                "modeling and evaluation, then grew the team around the system."
            ),
        },
    ]
    candidate["skills"].extend(
        [
            {"name": "Ranking Systems", "proficiency": "advanced", "endorsements": 24, "duration_months": 36},
            {"name": "Information Retrieval Systems", "proficiency": "advanced", "endorsements": 20, "duration_months": 39},
            {"name": "Search Backend", "proficiency": "advanced", "endorsements": 14, "duration_months": 32},
        ]
    )
    return candidate


def outside_india_candidate(candidate_id: str = "CAND_0000005") -> dict:
    candidate = deepcopy(base_candidate(candidate_id))
    candidate["profile"].update({"location": "London", "country": "UK"})
    candidate["redrob_signals"]["willing_to_relocate"] = False
    return candidate


def not_open_candidate(candidate_id: str = "CAND_0000006") -> dict:
    candidate = deepcopy(base_candidate(candidate_id))
    candidate["redrob_signals"].update({"open_to_work_flag": False})
    return candidate


def cv_speech_candidate(candidate_id: str = "CAND_0000007") -> dict:
    candidate = deepcopy(base_candidate(candidate_id))
    candidate["profile"].update(
        {
            "headline": "AI Research Engineer | Computer Vision and Speech",
            "summary": (
                "Research-focused AI engineer with most production experience in "
                "computer vision and speech recognition. Interested in moving into "
                "NLP and retrieval work."
            ),
            "current_title": "AI Research Engineer",
            "current_company": "Aganitha",
            "current_industry": "AI/ML",
        }
    )
    candidate["career_history"] = [
        {
            "company": "Aganitha",
            "title": "AI Research Engineer",
            "start_date": "2020-01-01",
            "end_date": None,
            "duration_months": 76,
            "is_current": True,
            "industry": "AI/ML",
            "company_size": "201-500",
            "description": (
                "Built computer vision models for image classification and object "
                "detection, plus speech recognition experiments. Production deployment "
                "was handled by a separate platform team; now interested in transitioning "
                "toward NLP and retrieval."
            ),
        }
    ]
    candidate["skills"] = [
        {"name": "Computer Vision", "proficiency": "expert", "endorsements": 44, "duration_months": 60},
        {"name": "Speech Recognition", "proficiency": "expert", "endorsements": 40, "duration_months": 58},
        {"name": "Object Detection", "proficiency": "advanced", "endorsements": 28, "duration_months": 48},
        {"name": "NLP", "proficiency": "intermediate", "endorsements": 8, "duration_months": 8},
        {"name": "LLMs", "proficiency": "intermediate", "endorsements": 7, "duration_months": 7},
    ]
    return candidate


def semantic_matching_candidate(candidate_id: str = "CAND_0000008") -> dict:
    candidate = deepcopy(base_candidate(candidate_id))
    candidate["profile"].update(
        {
            "current_title": "Senior AI Engineer",
            "headline": "Senior AI Engineer for candidate matching and search relevance",
            "summary": (
                "Built candidate matching, talent matching, job matching, and profile "
                "matching systems with candidate generation and reranking stages."
            ),
        }
    )
    candidate["career_history"][0]["description"] = (
        "Owned a two-tower candidate matching and candidate recommendation system for talent matching. "
        "Designed the candidate generation recall stage, cross encoder reranker, "
        "precision stage, retrieval evaluation, and search relevance dashboards."
    )
    candidate["career_history"][1]["description"] = (
        "Built entity matching and profile matching services for job matching workflows."
    )
    candidate["skills"].extend(
        [
            {"name": "Two-Tower Models", "proficiency": "advanced", "endorsements": 21, "duration_months": 32},
            {"name": "Cross Encoder", "proficiency": "advanced", "endorsements": 19, "duration_months": 28},
            {"name": "Reranking", "proficiency": "advanced", "endorsements": 24, "duration_months": 35},
        ]
    )
    return candidate


def generic_ai_keyword_candidate(candidate_id: str = "CAND_0000009") -> dict:
    candidate = deepcopy(base_candidate(candidate_id))
    candidate["profile"].update(
        {
            "current_title": "AI Specialist",
            "headline": "AI Specialist | LLM RAG OpenAI Pinecone LangChain",
            "summary": (
                "Built demos with LangChain, OpenAI, RAG, Pinecone, and prompt engineering. "
                "Most work is recent proof-of-concept automation and tutorials."
            ),
            "current_company": "Acme Corp",
            "current_industry": "Manufacturing",
        }
    )
    candidate["career_history"] = [
        {
            "company": "Acme Corp",
            "title": "AI Specialist",
            "start_date": "2025-01-01",
            "end_date": None,
            "duration_months": 17,
            "is_current": True,
            "industry": "Manufacturing",
            "company_size": "5001-10000",
            "description": (
                "Built internal demos using LangChain, OpenAI APIs, RAG templates, "
                "and prompt engineering. No production retrieval, ranking, or evaluation ownership."
            ),
        }
    ]
    candidate["skills"] = [
        {"name": "LLMs", "proficiency": "expert", "endorsements": 20, "duration_months": 8},
        {"name": "RAG", "proficiency": "expert", "endorsements": 18, "duration_months": 7},
        {"name": "Pinecone", "proficiency": "expert", "endorsements": 16, "duration_months": 6},
        {"name": "Fine-tuning LLMs", "proficiency": "intermediate", "endorsements": 10, "duration_months": 5},
        {"name": "LoRA", "proficiency": "intermediate", "endorsements": 7, "duration_months": 4},
        {"name": "Python", "proficiency": "intermediate", "endorsements": 8, "duration_months": 12},
    ]
    return candidate


def profile_only_evidence_candidate(candidate_id: str = "CAND_0000010") -> dict:
    candidate = deepcopy(base_candidate(candidate_id))
    candidate["profile"].update(
        {
            "headline": "Senior AI Engineer for hybrid search and ranking",
            "summary": (
                "Owned semantic search, candidate matching, learning-to-rank, "
                "cross encoder reranking, NDCG evaluation, and recruiter engagement metrics."
            ),
        }
    )
    candidate["career_history"][0]["description"] = "Built Python services for product teams."
    candidate["career_history"][1]["description"] = "Built data pipelines and model APIs."
    return candidate


def roadmap_candidate(candidate_id: str = "CAND_0000011") -> dict:
    candidate = deepcopy(base_candidate(candidate_id))
    candidate["profile"]["summary"] = "Owned the product roadmap for a platform team."
    candidate["career_history"][0]["description"] = (
        "Owned the product roadmap and stakeholder planning. No ranking metrics were used."
    )
    candidate["career_history"][1]["description"] = "Managed releases and documentation."
    candidate["skills"] = [{"name": "Python", "proficiency": "intermediate", "endorsements": 2, "duration_months": 8}]
    return candidate


def trusted_skill_candidate(candidate_id: str = "CAND_0000012") -> dict:
    candidate = deepcopy(base_candidate(candidate_id))
    candidate["skills"] = [
        {"name": "Python", "proficiency": "expert", "endorsements": 42, "duration_months": 72},
        {"name": "Vector Search", "proficiency": "advanced", "endorsements": 25, "duration_months": 30},
        {"name": "Learning to Rank", "proficiency": "advanced", "endorsements": 22, "duration_months": 28},
        {"name": "Cross Encoder", "proficiency": "advanced", "endorsements": 18, "duration_months": 18},
    ]
    candidate["redrob_signals"]["skill_assessment_scores"] = {
        "Python": 92.0,
        "Vector Search": 88.0,
        "Learning to Rank": 84.0,
    }
    return candidate
