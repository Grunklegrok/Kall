from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import Session, select
from kall.auth import create_session, get_current_user, password_hash, verify_password
from kall.db import get_session
from kall.models import Application, CandidateProfile, CareerProfile, Job, JobMatch, ResumeDocument, User, UserCredential
from kall.schemas import ApproveApplicationRequest, AuthResponse, IdentityProfileUpdate, JobCreate, LoginRequest, PrepareApplicationRequest, ProfessionalProfileCreate, RegisterRequest
from kall.security import encrypt_sensitive
from kall.services.applications import approve_application, prepare_application
from kall.services.billing import create_checkout_url
from kall.services.matching import deterministic_match
from kall.services.resume import extract_resume_text
router=APIRouter()

@router.get('/health')
def health(): return {'status':'ok','product':'Kall'}

@router.post('/auth/register',response_model=AuthResponse)
def register(payload:RegisterRequest,session:Session=Depends(get_session)):
    if session.exec(select(User).where(User.email==payload.email)).first(): raise HTTPException(409,'Email already registered')
    user=User(email=payload.email,full_name=payload.full_name,country=payload.country,state_region=payload.state_region)
    session.add(user);session.commit();session.refresh(user)
    session.add(UserCredential(user_id=user.id,password_hash=password_hash(payload.password)))
    session.add(CandidateProfile(user_id=user.id,country=payload.country,state_region=payload.state_region));session.commit()
    return AuthResponse(user_id=user.id,access_token=create_session(session,user.id))

@router.post('/auth/login',response_model=AuthResponse)
def login(payload:LoginRequest,session:Session=Depends(get_session)):
    user=session.exec(select(User).where(User.email==payload.email)).first()
    if not user: raise HTTPException(401,'Invalid credentials')
    cred=session.exec(select(UserCredential).where(UserCredential.user_id==user.id)).first()
    if not cred or not verify_password(payload.password,cred.password_hash): raise HTTPException(401,'Invalid credentials')
    return AuthResponse(user_id=user.id,access_token=create_session(session,user.id))

@router.get('/me',response_model=User)
def me(current_user:User=Depends(get_current_user)): return current_user

@router.put('/me/identity',response_model=CandidateProfile)
def update_identity(payload:IdentityProfileUpdate,current_user:User=Depends(get_current_user),session:Session=Depends(get_session)):
    profile=session.exec(select(CandidateProfile).where(CandidateProfile.user_id==current_user.id)).first() or CandidateProfile(user_id=current_user.id)
    d=payload.model_dump(); profile.preferred_name=d['preferred_name']; profile.phone_encrypted=encrypt_sensitive(d['phone']); profile.address_encrypted=encrypt_sensitive(d['address']); profile.city=d['city']; profile.state_region=d['state_region']; profile.postal_code_encrypted=encrypt_sensitive(d['postal_code']); profile.country=d['country']; profile.timezone=d['timezone']; profile.linkedin_url=d['linkedin_url']; profile.github_url=d['github_url']; profile.portfolio_urls=d['portfolio_urls']; profile.website_urls=d['website_urls']; profile.professional_summary=d['professional_summary']
    session.add(profile);session.commit();session.refresh(profile);return profile

@router.post('/me/professional-profiles',response_model=CareerProfile)
def create_profile(payload:ProfessionalProfileCreate,current_user:User=Depends(get_current_user),session:Session=Depends(get_session)):
    row=CareerProfile(user_id=current_user.id,**payload.model_dump(mode='json'));session.add(row);session.commit();session.refresh(row);return row

@router.get('/me/professional-profiles',response_model=list[CareerProfile])
def list_profiles(current_user:User=Depends(get_current_user),session:Session=Depends(get_session)):
    return list(session.exec(select(CareerProfile).where(CareerProfile.user_id==current_user.id)))

@router.post('/me/resumes',response_model=ResumeDocument)
async def upload_resume(file:UploadFile=File(...),current_user:User=Depends(get_current_user),session:Session=Depends(get_session)):
    folder=Path('uploads')/str(current_user.id);folder.mkdir(parents=True,exist_ok=True);path=folder/file.filename;path.write_bytes(await file.read())
    mime=file.content_type or 'application/octet-stream';text=extract_resume_text(str(path),mime)
    row=ResumeDocument(user_id=current_user.id,name=file.filename,file_path=str(path),mime_type=mime,extracted_text=text);session.add(row);session.commit();session.refresh(row);return row

@router.get('/me/resumes',response_model=list[ResumeDocument])
def list_resumes(current_user:User=Depends(get_current_user),session:Session=Depends(get_session)):
    return list(session.exec(select(ResumeDocument).where(ResumeDocument.user_id==current_user.id)))

@router.post('/jobs',response_model=Job)
def create_job(payload:JobCreate,session:Session=Depends(get_session)):
    row=Job(**payload.model_dump());session.add(row);session.commit();session.refresh(row);return row

@router.post('/jobs/{job_id}/match/{professional_profile_id}',response_model=JobMatch)
def match_job(job_id:int,professional_profile_id:int,current_user:User=Depends(get_current_user),session:Session=Depends(get_session)):
    job=session.get(Job,job_id);profile=session.get(CareerProfile,professional_profile_id)
    if not job or not profile or profile.user_id!=current_user.id: raise HTTPException(404,'Job or professional profile not found')
    score,strengths,gaps=deterministic_match(job,profile)
    row=JobMatch(user_id=current_user.id,career_profile_id=profile.id,job_id=job.id,score=score,strengths=strengths,gaps=gaps,recommendation='apply' if score>=75 else 'review' if score>=55 else 'pass')
    session.add(row);session.commit();session.refresh(row);return row

@router.post('/applications/prepare',response_model=Application)
def prepare(payload:PrepareApplicationRequest,current_user:User=Depends(get_current_user),session:Session=Depends(get_session)):
    job=session.get(Job,payload.job_id);profile=session.get(CareerProfile,payload.professional_profile_id);resume=session.get(ResumeDocument,payload.resume_id) if payload.resume_id else None
    if not job or not profile or profile.user_id!=current_user.id: raise HTTPException(404,'Required record not found')
    return prepare_application(session,current_user,job,profile,resume)

@router.post('/applications/{application_id}/approve',response_model=Application)
def approve(application_id:int,payload:ApproveApplicationRequest,current_user:User=Depends(get_current_user),session:Session=Depends(get_session)):
    app=session.get(Application,application_id)
    if not app or app.user_id!=current_user.id: raise HTTPException(404,'Application not found')
    try:return approve_application(session,app,payload.confirmed_sensitive_fields,payload.confirmed_answers)
    except ValueError as exc:raise HTTPException(422,str(exc)) from exc

@router.post('/billing/checkout')
def checkout(current_user:User=Depends(get_current_user)): return {'url':create_checkout_url(current_user.id)}
