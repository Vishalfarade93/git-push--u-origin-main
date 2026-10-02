# Deployment Guide — The Personal Signal Broadsheet

This guide provides instructions to deploy **The Personal Signal** application to the cloud so you can access your personal news aggregator from anywhere.

---

## Architecture Overview
- **Backend**: FastAPI (Python 3.10+) serving REST APIs and static files.
- **Database**: SQLite (`news_vault.db`), self-contained and zero-configuration.
- **Frontend**: Clean Modern Broadsheet single-page newspaper UI (HTML5, Vanilla CSS, JS).
- **AI Engine**: Google Gemini API integration (optional for automated strategic summaries and business opportunity detection).

---

## Option 1: Render.com (Recommended — 100% Free & Automatic)

Render provides free hosting for web services with automated SSL/HTTPS and GitHub integration.

### Steps:
1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Deploy Personal Signal"
   git branch -M main
   git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
   git push -u origin main
   ```

2. **Deploy on Render**:
   - Go to [dashboard.render.com](https://dashboard.render.com/).
   - Click **New +** > **Web Service**.
   - Connect your GitHub repository.
   - Configure the service settings:
     - **Name**: `personal-signal`
     - **Runtime**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn backend.server:app --host 0.0.0.0 --port $PORT`
     - **Instance Type**: `Free`
   - Under **Environment Variables**:
     - `GEMINI_API_KEY`: *(Optional)* Your Gemini API key.
   - Click **Create Web Service**.

Render will automatically build and assign a public URL like `https://personal-signal.onrender.com`.

---

## Option 2: Railway.app (Fast & Modern)

1. Go to [railway.app](https://railway.app/).
2. Click **New Project** > **Deploy from GitHub repo**.
3. Select your repository.
4. Railway automatically detects `Dockerfile` or `Procfile` and deploys.
5. In **Settings** > **Networking**, click **Generate Domain** to get a public URL.

---

## Option 3: Docker Deployment (Self-Hosted / Any Cloud)

A production-ready `Dockerfile` is included in the project root.

### Build and Run locally or on any server:
```bash
# 1. Build the Docker image
docker build -t personal-signal .

# 2. Run the container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/news_vault.db:/app/news_vault.db \
  -e GEMINI_API_KEY="your-gemini-api-key" \
  --name personal-news \
  personal-signal
```

Now open `http://localhost:8000` (or `http://YOUR_SERVER_IP:8000`).

---

## Option 4: Linux VPS (Ubuntu / Debian / EC2 / DigitalOcean)

### 1. Clone & Set Up Virtual Environment:
```bash
sudo apt update && sudo apt install -y python3-pip python3-venv git
git clone <YOUR_REPO_URL> /var/www/personal-signal
cd /var/www/personal-signal
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Systemd Service (`/etc/systemd/system/personal-signal.service`):
```ini
[Unit]
Description=The Personal Signal Broadsheet Service
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/personal-signal
ExecStart=/var/www/personal-signal/venv/bin/uvicorn backend.server:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl start personal-signal
sudo systemctl enable personal-signal
```

### 3. Setup Nginx Reverse Proxy with SSL:
```nginx
server {
    server_name news.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo certbot --nginx -d news.yourdomain.com
```

---

## Environment Variables Reference

| Variable | Default | Purpose |
|---|---|---|
| `PORT` | `8000` | Port for the HTTP server to listen on. |
| `HOST` | `127.0.0.1` | Binding interface (`0.0.0.0` for containers/cloud). |
| `GEMINI_API_KEY` | *(None)* | Optional Gemini API key for automated AI opportunity synthesis. Can also be set directly in the UI Settings modal. |
