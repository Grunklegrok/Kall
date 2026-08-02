from urllib.parse import quote_plus

from sqlmodel import Session, select

from kall.models import (
    CareerGoal,
    CareerGrowthPlan,
    GrowthMilestone,
    GrowthResource,
    GrowthSearchQuery,
    Skill,
)


def _queries(role: str, industry: str | None) -> list[tuple[str, str, str]]:
    context = f" {industry}" if industry else ""
    items = [
        ("career_path", f"how to become a {role}{context}", "Understand common entry paths and role expectations."),
        ("skills", f"{role}{context} required skills portfolio", "Find recurring skills and portfolio evidence requested by the field."),
        ("education", f"best courses certificates for {role}{context}", "Compare structured learning options and credentials."),
        ("portfolio", f"{role}{context} portfolio examples breakdown", "Study strong work samples and presentation patterns."),
        ("community", f"{role}{context} professional communities mentorship", "Find peers, mentors, events, and feedback communities."),
        ("market", f"entry level {role}{context} job descriptions", "Use current postings to validate skills and terminology."),
    ]
    return items


def build_growth_plan(session: Session, goal: CareerGoal) -> CareerGrowthPlan:
    skills = list(session.exec(select(Skill).where(Skill.user_id == goal.user_id)))
    current = [skill.name for skill in skills if skill.is_primary][:8]
    role = goal.target_role.strip()
    industry = goal.target_industry
    lower = f"{role} {industry or ''}".lower()

    if "game" in lower and any(word in lower for word in ("artist", "art", "3d", "concept")):
        gaps = ["Visual fundamentals", "Game-engine workflow", "Production-ready portfolio", "Art feedback and iteration", "Studio pipeline familiarity"]
        projects = [
            ("Foundation", "Map the role", "Compare concept, environment, character, technical, UI, and VFX art paths.", "research", 4),
            ("Skills", "Build production fundamentals", "Choose a focused toolchain and practice composition, form, color, materials, lighting, and optimization.", "education", 60),
            ("Portfolio", "Create three targeted pieces", "Produce role-specific work with process notes, iterations, and in-engine presentation.", "portfolio", 120),
            ("Community", "Establish a critique loop", "Join artist communities, request structured feedback, and revise each portfolio piece.", "networking", 20),
            ("Market", "Reverse-engineer studio requirements", "Review current game-art postings and track repeated tools, styles, and portfolio expectations.", "market_research", 12),
            ("Launch", "Apply through a focused campaign", "Tailor the portfolio and resume to selected studio types, then track applications and feedback.", "job_search", 24),
        ]
        roles = ["Concept Artist", "Environment Artist", "Character Artist", "Technical Artist", "UI Artist", "VFX Artist"]
    else:
        gaps = ["Role-specific technical skills", "Demonstrable work samples", "Industry vocabulary", "Professional network", "Interview readiness"]
        projects = [
            ("Foundation", "Map the target role", "Study responsibilities, seniority levels, adjacent roles, and common entry paths.", "research", 5),
            ("Skills", "Close the highest-value skill gaps", "Prioritize recurring requirements from current role descriptions.", "education", 50),
            ("Evidence", "Build proof of capability", "Create projects, case studies, or work samples that demonstrate the target competencies.", "portfolio", 80),
            ("Community", "Build field relationships", "Join professional groups, attend events, and schedule informational conversations.", "networking", 16),
            ("Market", "Validate against current demand", "Review postings regularly and update the plan when requirements shift.", "market_research", 10),
            ("Launch", "Prepare and pursue opportunities", "Align the resume, portfolio, interview stories, and application strategy.", "job_search", 24),
        ]
        roles = [role]

    plan = CareerGrowthPlan(
        user_id=goal.user_id,
        career_goal_id=goal.id,
        summary=f"A staged path toward {role}" + (f" in {industry}" if industry else "") + ", balancing learning, evidence, community, and market validation.",
        current_strengths=current,
        skill_gaps=gaps,
        recommended_roles=roles,
    )
    session.add(plan)
    session.commit()
    session.refresh(plan)

    for sequence, (phase, title, description, category, hours) in enumerate(projects, start=1):
        session.add(GrowthMilestone(user_id=goal.user_id, growth_plan_id=plan.id, sequence=sequence, phase=phase, title=title, description=description, category=category, estimated_hours=hours))

    for category, query, rationale in _queries(role, industry):
        session.add(GrowthSearchQuery(user_id=goal.user_id, growth_plan_id=plan.id, category=category, query=query, search_url=f"https://www.google.com/search?q={quote_plus(query)}", rationale=rationale))

    resource_queries = [
        ("course_search", f"{role} course curriculum", "Search for courses with project-based outcomes."),
        ("portfolio_reference", f"{role} portfolio", "Review current portfolios and presentation standards."),
        ("community_search", f"{role} community discord association", "Find communities for critique and mentorship."),
    ]
    for resource_type, query, description in resource_queries:
        session.add(GrowthResource(user_id=goal.user_id, growth_plan_id=plan.id, resource_type=resource_type, title=query.title(), provider="web search", url=f"https://www.google.com/search?q={quote_plus(query)}", description=description, cost_type="varies"))

    session.commit()
    return plan
