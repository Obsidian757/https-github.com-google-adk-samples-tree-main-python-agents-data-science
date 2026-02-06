#!/usr/bin/env bash
# ============================================================================
# 12th House AI — Deploy landing page to VPS
#
# Run from your LOCAL machine (not the VPS):
#   chmod +x deploy-vps.sh && ./deploy-vps.sh
#
# Or manually:
#   1. scp landing_page/index.html root@76.13.98.156:/var/www/12thhouseai/
#   2. scp nginx/12thhouseai.conf root@76.13.98.156:/etc/nginx/sites-available/12thhouseai
#   3. ssh root@76.13.98.156 'bash /root/setup-nginx.sh'
# ============================================================================
set -euo pipefail

VPS_IP="76.13.98.156"
VPS_USER="root"
VPS_HOST="${VPS_USER}@${VPS_IP}"

echo "======================================="
echo "  12th House AI — VPS Deploy"
echo "  Target: ${VPS_IP}"
echo "======================================="

# Step 1: Upload landing page
echo "[1/3] Uploading landing page..."
ssh ${VPS_HOST} 'mkdir -p /var/www/12thhouseai'
scp landing_page/index.html ${VPS_HOST}:/var/www/12thhouseai/index.html

# Step 2: Configure Nginx on VPS
echo "[2/3] Configuring Nginx..."
ssh ${VPS_HOST} << 'REMOTE_SCRIPT'
# Install nginx if needed
if ! command -v nginx &> /dev/null; then
    apt-get update -qq && apt-get install -y -qq nginx > /dev/null 2>&1
fi

# Write nginx config
cat > /etc/nginx/sites-available/12thhouseai << 'NGINX_CONF'
server {
    listen 80;
    listen [::]:80;
    server_name 76.13.98.156 srv1328250.hstgr.cloud 12thhouseai.com www.12thhouseai.com;

    root /var/www/12thhouseai;
    index index.html;

    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;

    location / {
        try_files $uri $uri/ =404;
    }
}
NGINX_CONF

# Enable site
ln -sf /etc/nginx/sites-available/12thhouseai /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and reload
nginx -t && systemctl reload nginx

# Firewall
ufw allow 'Nginx Full' > /dev/null 2>&1 || true
ufw allow OpenSSH > /dev/null 2>&1 || true
REMOTE_SCRIPT

# Step 3: Verify
echo "[3/3] Verifying..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://${VPS_IP}/")
if [ "$HTTP_CODE" = "200" ]; then
    echo ""
    echo "======================================="
    echo "  LIVE: http://${VPS_IP}"
    echo "======================================="
else
    echo "  Got HTTP ${HTTP_CODE} — check VPS logs"
fi
