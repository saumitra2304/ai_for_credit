# Deploy: Vercel frontend + EC2 Docker backend

The browser runs on Vercel. The API (FastAPI + Probe search + nginx) runs in one Docker container on EC2. Secrets stay on the server in a gitignored `.env` file.

You need:

- This repo on GitHub (`demo-site` branch until you merge)
- An AWS account
- A domain name (for `https://api.yourdomain.com`)
- A [Vercel](https://vercel.com) account linked to GitHub

---

## A. Push the code

On your laptop, from the repo root (`ai_for_credit/`):

```bash
git checkout demo-site
git add -A
git status
# confirm .env is NOT listed
git commit -m "Web deploy: Vercel frontend and EC2 Docker backend"
git push -u origin demo-site
```

Never commit `.env`.

---

## B. Backend on AWS EC2

### 1. Create the instance

1. AWS Console → **EC2** → **Launch instance**.
2. Name: `kuber-api`.
3. AMI: **Ubuntu Server 24.04 LTS**.
4. Type: **t3.medium** (2 vCPU / 4 GB). The first Docker image compiles Rust; smaller instances often run out of memory.
5. Storage: **30 GB** gp3.
6. Key pair: create or select one (you need the `.pem` to SSH).
7. **Network / security group** — inbound:
   - SSH `22` from your IP
   - HTTP `80` from `0.0.0.0/0`
   - HTTPS `443` from `0.0.0.0/0`
8. Launch.

### 2. Give it a stable public IP

1. EC2 → **Elastic IPs** → Allocate → Associate with this instance.
2. In your DNS (Route 53 or wherever the domain is):
   - `A` record: `api.yourdomain.com` → the Elastic IP.

Wait until `ping api.yourdomain.com` (or an `nslookup`) shows that IP.

### 3. SSH in and install Docker

```bash
ssh -i your-key.pem ubuntu@api.yourdomain.com
```

Then:

```bash
sudo apt-get update
sudo apt-get install -y git ca-certificates curl
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker ubuntu
newgrp docker
docker --version
docker compose version
```

### 4. Clone the repo

```bash
cd ~
git clone -b demo-site https://github.com/saumitra2304/ai_for_credit.git
cd ai_for_credit
```

If the GitHub repo is private, use a [personal access token](https://github.com/settings/tokens) or SSH:

```bash
git clone -b demo-site git@github.com:saumitra2304/ai_for_credit.git
```

### 5. Create `.env` on the server

```bash
cp deploy/env.example .env
nano .env
```

Set at least:

```
probe_api_key=...
INSTA_API_KEY=...
OPENAI_API_KEY=...
OPENAI_MODEL_NAME=gpt-5.4-nano

INTERNAL_TOKEN=<long random string>
DOMAIN=api.yourdomain.com
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:5173
CORS_ORIGIN_REGEX=https://.*\.vercel\.app

AUTH_ALLOW_REGISTER=true
AUTH_BOOTSTRAP_EMAIL=you@yourdomain.com
AUTH_BOOTSTRAP_PASSWORD=<strong password>
AUTH_BOOTSTRAP_NAME=Admin
```

Generate `INTERNAL_TOKEN` with:

```bash
openssl rand -hex 32
```

You can put a placeholder in `CORS_ORIGINS` and update it after Vercel gives you a URL.

### 6. First start (HTTP on port 80)

```bash
cd ~/ai_for_credit/deploy
docker compose up -d --build
```

The first build takes several minutes. Then:

```bash
curl http://127.0.0.1/health
# expect: {"ok":true}
curl http://api.yourdomain.com/health
```

### 7. HTTPS certificate

With the container running (it already serves ACME on port 80):

```bash
sudo apt-get install -y certbot
sudo certbot certonly --webroot \
  -w ~/ai_for_credit/deploy/certbot-www \
  --config-dir ~/ai_for_credit/deploy/certs \
  --work-dir /tmp/certbot-work \
  --logs-dir /tmp/certbot-logs \
  -d api.yourdomain.com
```

Restart so nginx picks up TLS:

```bash
cd ~/ai_for_credit/deploy
docker compose restart
curl https://api.yourdomain.com/health
```

Renew later with the same `certbot certonly` command, then `docker compose restart`.

### 8. Later updates from git

```bash
cd ~/ai_for_credit
git pull origin demo-site
cd deploy
docker compose up -d --build
```

SQLite lives in the Docker volume `kuber-data`. Pulls do not wipe chats or users.

---

## C. Frontend on Vercel

1. Open [vercel.com](https://vercel.com) → **Add New** → **Project** → import `saumitra2304/ai_for_credit`.
2. **Root Directory**: leave as the repository root (do not set it to `credit_ai_frontend`). The root `vercel.json` already runs:

   - install: `npm install --prefix credit_ai_frontend`
   - build: `npm run build --prefix credit_ai_frontend`
   - output: `credit_ai_frontend/dist`

3. **Environment variables** (Production and Preview):

   | Name | Value |
   |---|---|
   | `VITE_API_URL` | `https://api.yourdomain.com` |

   No trailing slash. Use `https://`.

4. Production branch: `demo-site` (Project → Settings → Git) until you merge to `main`.
5. Deploy.

You will get a URL like `https://ai-for-credit-xxxx.vercel.app`.

### Point CORS at that URL

On EC2, edit `.env`:

```bash
nano ~/ai_for_credit/.env
```

Set:

```
CORS_ORIGINS=https://ai-for-credit-xxxx.vercel.app
```

Then:

```bash
cd ~/ai_for_credit/deploy
docker compose up -d
```

A recreate is enough; you do not need to rebuild the image for CORS.

Optional: add a custom domain in Vercel (Settings → Domains) and add that origin to `CORS_ORIGINS` as well.

---

## D. First login

1. Open the Vercel URL.
2. Sign in with `AUTH_BOOTSTRAP_EMAIL` / `AUTH_BOOTSTRAP_PASSWORD`.
3. That account is admin. After you have it, set `AUTH_ALLOW_REGISTER=false` on EC2 and `docker compose up -d` so strangers cannot sign up.

---

## Checklist if something fails

| Symptom | Check |
|---|---|
| Vercel build works, login says it cannot reach the server | `VITE_API_URL` and a Vercel **redeploy** after changing it |
| Browser CORS error | `CORS_ORIGINS` matches the exact `https://…vercel.app` origin, then recreate the container |
| `curl /health` fails on EC2 | `docker compose logs -f` in `deploy/` |
| Docker build killed / OOM | use **t3.medium** or larger |
| HTTPS not serving | `DOMAIN` matches the cert folder name; `deploy/certs/live/api.yourdomain.com/fullchain.pem` exists; `docker compose restart` |
| Company search 401 | you are logged in; `INTERNAL_TOKEN` is set the same in `.env` |
| Probe 403 | the key is sandbox vs production; this app uses the Probe sandbox URL |

Do not open port `8001` or `3000` on the security group. Only nginx on 80/443 should be public.
