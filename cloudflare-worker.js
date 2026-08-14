addEventListener('fetch', event => event.respondWith(handle(event.request)))

async function handle(request) {
  const url = new URL(request.url)

  // Only proxy requests under /api/*
  if (url.pathname.startsWith('/api/')) {
    // Build upstream URL
    const upstreamPath = url.pathname.replace(/^\/api/, '')
    const upstreamUrl = 'https://api.mail.tm' + upstreamPath + url.search

    // Prepare init
    const init = {
      method: request.method,
      headers: new Headers(request.headers),
      redirect: 'follow'
    }

    if (request.method !== 'GET' && request.method !== 'HEAD') {
      init.body = await request.arrayBuffer()
    }

    // Handle preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization, Accept',
          'Access-Control-Max-Age': '86400'
        }
      })
    }

    // Fetch upstream
    const resp = await fetch(upstreamUrl, init)

    // Copy response body and headers, then add CORS
    const body = await resp.arrayBuffer()
    const headers = new Headers(resp.headers)
    headers.set('Access-Control-Allow-Origin', '*')
    headers.set('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization, Accept')

    return new Response(body, { status: resp.status, headers })
  }

  // Not an API call: let the request go through (useful when combining with Pages + Worker)
  return fetch(request)
}
