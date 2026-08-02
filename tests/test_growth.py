from sqlmodel import Session, SQLModel, create_engine, select

from kall.models import CareerGoal, GrowthMilestone, GrowthSearchQuery, User
from kall.services.growth import build_growth_plan


def test_game_artist_goal_generates_portfolio_and_market_path() -> None:
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        user = User(email="artist@example.com", full_name="Artist")
        session.add(user)
        session.commit()
        session.refresh(user)
        goal = CareerGoal(
            user_id=user.id,
            title="Move into game art",
            target_role="Game industry artist",
            target_industry="Video games",
            time_per_week_hours=8,
        )
        session.add(goal)
        session.commit()
        session.refresh(goal)
        plan = build_growth_plan(session, goal)
        milestones = list(session.exec(select(GrowthMilestone).where(GrowthMilestone.growth_plan_id == plan.id)))
        searches = list(session.exec(select(GrowthSearchQuery).where(GrowthSearchQuery.growth_plan_id == plan.id)))
        assert any(item.category == "portfolio" for item in milestones)
        assert any("portfolio" in item.query.lower() for item in searches)
        assert "Technical Artist" in plan.recommended_roles


def test_growth_searches_are_transparent_user_opened_urls() -> None:
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        user = User(email="dev@example.com", full_name="Developer")
        session.add(user)
        session.commit()
        session.refresh(user)
        goal = CareerGoal(user_id=user.id, title="Advance", target_role="Security Engineer")
        session.add(goal)
        session.commit()
        session.refresh(goal)
        plan = build_growth_plan(session, goal)
        searches = list(session.exec(select(GrowthSearchQuery).where(GrowthSearchQuery.growth_plan_id == plan.id)))
        assert searches
        assert all(item.search_url.startswith("https://www.google.com/search?q=") for item in searches)
