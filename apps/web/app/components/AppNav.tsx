import styles from './AppNav.module.css';

type AppNavProps={current?:'brief'|'opportunities'|'applications'|'documents'|'career'};
const items=[['brief','Brief','/morning-brief'],['opportunities','Opportunities','/search'],['applications','Applications','/applications'],['documents','Documents','/resume-intelligence'],['career','Career','/profiles']] as const;
export default function AppNav({current}:AppNavProps){return <header className={styles.header}><a className={styles.brand} href='/' aria-label='Kall home'>Kall</a><nav className={styles.nav} aria-label='Primary navigation'>{items.map(([key,label,href])=><a key={key} href={href} className={`${styles.link} ${current===key?styles.active:''}`} aria-current={current===key?'page':undefined}>{label}</a>)}</nav><a className={styles.account} href='/settings' aria-label='Open account settings'>JS</a></header>}
