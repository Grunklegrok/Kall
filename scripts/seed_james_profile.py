from pathlib import Path
import yaml
from sqlmodel import Session
from kall.db import create_db_and_tables, engine
from kall.models import CandidateProfile, CareerProfile, Education, Skill, User


def main() -> None:
    create_db_and_tables()
    data = yaml.safe_load(Path("data/james_kall_profile.yaml").read_text(encoding="utf-8"))
    with Session(engine) as session:
        user = User(**data["user"])
        session.add(user)
        session.commit()
        session.refresh(user)

        session.add(CandidateProfile(user_id=user.id, **data["candidate_profile"]))
        for item in data["career_profiles"]:
            session.add(CareerProfile(user_id=user.id, **item))
        for item in data.get("education", []):
            session.add(Education(user_id=user.id, **item))
        for item in data.get("skills", []):
            session.add(Skill(user_id=user.id, **item))
        session.commit()
        print(f"Seeded Kall profile for {user.full_name} (user_id={user.id})")


if __name__ == "__main__":
    main()
