Deploying the API proxy (Cloudflare Worker)

Why
- GitHub Pages serves only static files and cannot run a proxy. To call https://api.mail.tm from a github.io page you need a same-origin proxy that adds CORS headers.

Recommended: Cloudflare Workers (fast, free tier)

Steps (quick):
1. Create a Cloudflare account and a Workers service.
2. In Cloudflare dashboard, create a new Worker and paste the contents of `cloudflare-worker.js` from this repo.
3. Save and deploy the Worker. You will get a URL like `https://your-name.your-subdomain.workers.dev`.
4. Edit `index.html` in the repo and set the meta tag `<meta name="mail-proxy" content="https://your-name.your-subdomain.workers.dev">` in the <head> section.
5. Commit and push to GitHub. Enable GitHub Pages for the repository (e.g., the `main` branch or `gh-pages` branch).
6. Open your github.io site — the frontend will call the Worker proxy which forwards requests to api.mail.tm and returns CORS-enabled responses.

Alternative hosting: Vercel serverless functions, Render, Heroku, Cloudflare Pages + Functions. The important point is: you need a public HTTP endpoint that proxies /api/* to https://api.mail.tm and sets Access-Control-Allow-Origin: * (or your domain).

Notes & security
- The proxy simply forwards Authorization headers from the browser when present. Do not expose credentials publicly.
- If you plan to publish the site for public use, consider rate limits and anti-abuse (the Worker can implement rate-limiting or require a server-side API key).

If you want, I can:
- deploy the Worker for you (requires Cloudflare account credentials), or
- prepare a GitHub Actions workflow that deploys to Cloudflare using `wrangler` (you must add your CF credentials as secrets).