import hashlib
import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select
from kall.auth import get_current_user
from kall.db import get_session
from kall.models import Application, ApplicationTestimonial, Testimonial, TestimonialRequest, User
from kall.security import encrypt_value

router = APIRouter(tags=["testimonials"])


class RequestCreate(BaseModel):
    recipient_name: str
    recipient_email: EmailStr
    relationship: str
    request_type: str = "testimonial"
    personal_message: str | None = None


class Submission(BaseModel):
    token: str
    author_name: str
    author_title: str | None = None
    author_company: str | None = None
    relationship: str
    body: str
    permission_granted: bool


class VisibilityUpdate(BaseModel):
    status: str
    include_on_profile: bool = False
    include_in_applications: bool = False


@router.post("/testimonials/requests")
def create_request(payload: RequestCreate, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    token = secrets.token_urlsafe(32)
    request = TestimonialRequest(
        user_id=user.id,
        recipient_name=payload.recipient_name,
        recipient_email_encrypted=encrypt_value(str(payload.recipient_email)),
        relationship=payload.relationship,
        request_type=payload.request_type,
        personal_message=payload.personal_message,
        token_hash=hashlib.sha256(token.encode()).hexdigest(),
        expires_at=datetime.utcnow() + timedelta(days=30),
    )
    session.add(request); session.commit(); session.refresh(request)
    return {"request": request, "invitation_token": token}


@router.post("/testimonials/submit", response_model=Testimonial)
def submit(payload: Submission, session: Session = Depends(get_session)):
    token_hash = hashlib.sha256(payload.token.encode()).hexdigest()
    request = session.exec(select(TestimonialRequest).where(TestimonialRequest.token_hash == token_hash)).first()
    if not request or request.status != "pending" or (request.expires_at and request.expires_at < datetime.utcnow()):
        raise HTTPException(404, "Invitation is invalid or expired")
    testimonial = Testimonial(user_id=request.user_id, request_id=request.id, author_name=payload.author_name,
        author_title=payload.author_title, author_company=payload.author_company, relationship=payload.relationship,
        body=payload.body, verified_via_request=True, permission_granted=payload.permission_granted)
    request.status = "completed"; request.completed_at = datetime.utcnow()
    session.add(testimonial); session.add(request); session.commit(); session.refresh(testimonial)
    return testimonial


@router.get("/testimonials")
def list_testimonials(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return list(session.exec(select(Testimonial).where(Testimonial.user_id == user.id)))


@router.put("/testimonials/{testimonial_id}", response_model=Testimonial)
def moderate(testimonial_id: int, payload: VisibilityUpdate, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    item = session.get(Testimonial, testimonial_id)
    if not item or item.user_id != user.id: raise HTTPException(404, "Testimonial not found")
    if payload.status not in {"approved", "rejected", "pending_review"}: raise HTTPException(422, "Invalid status")
    if (payload.include_on_profile or payload.include_in_applications) and not item.permission_granted:
        raise HTTPException(422, "Author permission is required")
    item.status = payload.status; item.include_on_profile = payload.include_on_profile; item.include_in_applications = payload.include_in_applications
    item.approved_at = datetime.utcnow() if payload.status == "approved" else None
    session.add(item); session.commit(); session.refresh(item); return item


@router.post("/applications/{application_id}/testimonials/{testimonial_id}")
def include_in_application(application_id: int, testimonial_id: int, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    application = session.get(Application, application_id); item = session.get(Testimonial, testimonial_id)
    if not application or application.user_id != user.id or not item or item.user_id != user.id: raise HTTPException(404, "Record not found")
    if item.status != "approved" or not item.include_in_applications or not item.permission_granted: raise HTTPException(422, "Testimonial is not approved for applications")
    link = ApplicationTestimonial(application_id=application_id, testimonial_id=testimonial_id, user_id=user.id)
    session.add(link); session.commit(); session.refresh(link); return link
