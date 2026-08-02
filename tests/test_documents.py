from pathlib import Path

import pytest
from sqlmodel import Session, SQLModel, create_engine

from kall.models import Job, TailoringChange, TailoringProposal, User
from kall.services.documents import finalized_resume_content, generate_resume_documents


def test_finalized_content_excludes_rejected_changes() -> None:
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        user = User(email="docs@example.com", full_name="Docs User")
        session.add(user)
        session.commit()
        session.refresh(user)
        job = Job(source="test", company="North", title="Director", description="Lead quality", url="https://example.com/docs")
        session.add(job)
        session.commit()
        session.refresh(job)
        proposal = TailoringProposal(
            user_id=user.id,
            job_id=job.id,
            resume_id=1,
            professional_profile_id=1,
            status="finalized",
            finalized_at=job.created_at,
        )
        session.add(proposal)
        session.commit()
        session.refresh(proposal)
        session.add(TailoringChange(proposal_id=proposal.id, section="summary", original_text="Old", proposed_text="Accepted", reason="match", status="accepted"))
        session.add(TailoringChange(proposal_id=proposal.id, section="achievement", original_text="Old", proposed_text="Rejected", reason="match", status="rejected"))
        session.commit()
        content = finalized_resume_content(session, proposal)
        assert content == [{"section": "summary", "text": "Accepted"}]


def test_document_generation_writes_readable_artifacts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        user = User(email="files@example.com", full_name="Files User")
        session.add(user)
        session.commit()
        session.refresh(user)
        job = Job(source="test", company="North", title="Director", description="Lead quality", url="https://example.com/files")
        session.add(job)
        session.commit()
        session.refresh(job)
        proposal = TailoringProposal(user_id=user.id, job_id=job.id, resume_id=1, professional_profile_id=1, status="finalized", finalized_at=job.created_at)
        session.add(proposal)
        session.commit()
        session.refresh(proposal)
        session.add(TailoringChange(proposal_id=proposal.id, section="summary", original_text="Led releases", proposed_text="Led releases with 99% uptime", reason="verified", immutable_tokens=["99%"], status="accepted"))
        session.commit()
        generated = generate_resume_documents(session, proposal)
        output = tmp_path / "generated" / str(user.id) / f"document-{generated.id}"
        assert (output / "resume.docx").stat().st_size > 0
        assert (output / "resume.pdf").read_bytes().startswith(b"%PDF")
        assert "99%" in (output / "resume.txt").read_text()
