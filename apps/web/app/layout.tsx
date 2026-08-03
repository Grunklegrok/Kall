import type { Metadata } from 'next';
import OpportunitiesAtsSearch from './components/OpportunitiesAtsSearch';
import SiteFooter from './components/SiteFooter';
import './globals.css';

export const metadata: Metadata = {
  title: {
    default: 'Kall — The Career Operating System',
    template: '%s — Kall',
  },
  description:
    'A calm, private workspace for building a meaningful career over time.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
          <div style={{ flex: 1 }}>
            {children}
            <OpportunitiesAtsSearch />
          </div>
          <SiteFooter />
        </div>
      </body>
    </html>
  );
}
