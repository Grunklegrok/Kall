'use client';

import { FormEvent, useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Score = { resume_id:number; total_score:number; explanation:string[]; gaps:string[] };

type Result = { scores:Score[]; coverage:Record<string,{covered:number;total:number}>; achievement_matches:Array<{achievement_id:number;score:number;explanation:string[]}>; selection?:{selected_resume_id?:number;recommended_resume_id?:number} };

export default function JobIntelligencePage(){
  const [result,setResult]=useState<Result|null>(null);
  const [message,setMessage]=useState('');
  async function build(e:FormEvent<HTMLFormElement>){
    e.preventDefault();
    const token=localStorage.getItem('kall_token');
    const form=new FormData(e.currentTarget);
    const jobId=form.get('job_id');
    const profileId=form.get('profile_id');
    const run=await fetch(`${API}/api/jobs/${jobId}/intelligence/${profileId}`,{method:'POST',headers:{Authorization:`Bearer ${token}`}});
    if(!run.ok){const d=await run.json();setMessage(d.detail||'Unable to build intelligence');return;}
    const response=await fetch(`${API}/api/jobs/${jobId}/intelligence/${profileId}`,{headers:{Authorization:`Bearer ${token}`}});
    setResult(await response.json());
    setMessage('Analysis complete.');
  }
  async function selectResume(resumeId:number){
    const token=localStorage.getItem('kall_token');
    const job=(document.querySelector('[name=job_id]') as HTMLInputElement).value;
    const profile=(document.querySelector('[name=profile_id]') as HTMLInputElement).value;
    await fetch(`${API}/api/jobs/${job}/intelligence/${profile}/selection`,{method:'PUT',headers:{Authorization:`Bearer ${token}`,'Content-Type':'application/json'},body:JSON.stringify({resume_id:resumeId})});
    setMessage(`Resume ${resumeId} selected.`);
  }
  return <main className='shell'>
    <header className='topbar'><div className='brand'>Kall Job Intelligence</div><nav><a href='/search'>Search</a><a href='/resume-intelligence'>Resume Intelligence</a></nav></header>
    <section className='card'><h1>Compare every resume to a job</h1><form className='form' onSubmit={build}><div className='two'><input className='input' name='job_id' placeholder='Job ID' required/><input className='input' name='profile_id' placeholder='Professional profile ID' required/></div><button className='button'>Build match intelligence</button></form><p>{message}</p></section>
    {result&&<><section className='grid' style={{marginTop:16}}>{Object.entries(result.coverage||{}).map(([key,value])=><article className='card' key={key}><h3>{key.replaceAll('_',' ')}</h3><strong>{value.covered} of {value.total}</strong></article>)}</section>
    <section style={{marginTop:16}}>{result.scores.map((score,index)=><article className='card' key={score.resume_id} style={{marginBottom:12}}><span className='pill'>{index===0?'Recommended':'Candidate'}</span><h2>Resume {score.resume_id}: {score.total_score}%</h2><p>{score.explanation.join(' · ')||'No positive evidence yet.'}</p><p><strong>Gaps:</strong> {score.gaps.join(', ')||'None detected'}</p><button className='button' onClick={()=>selectResume(score.resume_id)}>Use this resume</button></article>)}</section>
    <section className='card'><h2>Verified achievement matches</h2><p>{result.achievement_matches.length} verified achievements are relevant to this job. Rejected achievements are excluded.</p></section></>}
  </main>;
}
