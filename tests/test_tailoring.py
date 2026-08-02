import pytest
from sqlmodel import Session, SQLModel, create_engine

from kall.models import TailoringChange, TailoringProposal
from kall.services.tailoring import finalize_proposal, preserves_immutable_facts, review_change


def test_immutable_metrics_and_dates_are_preserved() -> None:
    original = "Improved uptime to 99% in 2024 and saved $250,000."
    assert preserves_immutable_facts(original, "In 2024, improved uptime to 99% and saved $250,000.")
    assert not preserves_immutable_facts(original, "Improved uptime to 100% in 2025 and saved $500,000.")


def test_review_rejects_metric_mutation() -> None:
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        proposal = TailoringProposal(user_id=1, job_id=1, resume_id=1, professional_profile_id=1)
        session.add(proposal)
        session.commit()
        session.refresh(proposal)
        change = TailoringChange(
            proposal_id=proposal.id,
            section="achievement",
            original_text="Raised automation to 80% in 2023.",
            proposed_text="Raised automation to 80% in 2023.",
            reason="Aligned evidence",
        )
        session.add(change)
        session.commit()
        session.refresh(change)
        with pytest.raises(ValueError):
            review_change(session, change, "edited", "Raised automation to 95% in 2024.")


def test_finalize_requires_every_change_reviewed() -> None:
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        proposal = TailoringProposal(user_id=1, job_id=1, resume_id=1, professional_profile_id=1)
        session.add(proposal)
        session.commit()
        session.refresh(proposal)
        session.add(TailoringChange(proposal_id=proposal.id, section="summary", original_text="A", proposed_text="A", reason="Test"))
        session.commit()
        with pytest.raises(ValueError):
            finalize_proposal(session, proposal)
