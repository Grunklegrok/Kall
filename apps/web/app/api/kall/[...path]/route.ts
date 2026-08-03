import { NextRequest, NextResponse } from 'next/server';

function apiBaseUrl(): string | null {
  const configured = process.env.KALL_API_URL || process.env.NEXT_PUBLIC_API_URL;
  if (configured) return configured.replace(/\/$/, '');
  if (process.env.NODE_ENV !== 'production') return 'http://localhost:8000';
  return null;
}

async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const baseUrl = apiBaseUrl();
  if (!baseUrl) {
    return NextResponse.json(
      { detail: 'Kall API URL is not configured on the web service.' },
      { status: 503 },
    );
  }

  const { path } = await context.params;
  const target = new URL(`${baseUrl}/api/${path.join('/')}`);
  target.search = request.nextUrl.search;

  const headers = new Headers();
  const contentType = request.headers.get('content-type');
  const authorization = request.headers.get('authorization');
  if (contentType) headers.set('content-type', contentType);
  if (authorization) headers.set('authorization', authorization);

  const response = await fetch(target, {
    method: request.method,
    headers,
    body: ['GET', 'HEAD'].includes(request.method) ? undefined : await request.arrayBuffer(),
    cache: 'no-store',
    // OAuth start and callback endpoints intentionally return redirects. Those
    // redirects must reach the browser rather than being followed by the
    // Next.js server under the Kall origin.
    redirect: 'manual',
  });

  const responseHeaders = new Headers();
  const responseContentType = response.headers.get('content-type');
  const location = response.headers.get('location');
  if (responseContentType) responseHeaders.set('content-type', responseContentType);
  if (location) responseHeaders.set('location', location);

  return new NextResponse(response.body, {
    status: response.status,
    headers: responseHeaders,
  });
}

export const dynamic = 'force-dynamic';

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
