# Fix Nginx Upload Limits for CloudFace Pro

## Problem
Nginx is blocking uploads of:
- More than 50 files at once
- Large file sizes
- Long upload times (timeouts)

## Solution

SSH to your server and run these commands:

```bash
ssh root@69.62.85.241

# Edit Nginx configuration
nano /etc/nginx/sites-available/cloudface-pro
```

Update the configuration to include these settings:

```nginx
server {
    listen 80;
    server_name cloudface-ai.pro www.cloudface-ai.pro;

    # Increase upload size limits
    client_max_body_size 2G;           # Max upload size (2GB for large batches)
    client_body_timeout 300s;          # 5 minutes for upload
    client_header_timeout 300s;        # 5 minutes for headers
    
    # Increase timeouts for processing
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;
    send_timeout 300s;
    
    # Buffer settings for large uploads
    client_body_buffer_size 128k;
    proxy_buffer_size 4k;
    proxy_buffers 8 32k;
    proxy_busy_buffers_size 64k;

    location / {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Disable request buffering for uploads
        proxy_request_buffering off;
    }
}
```

Then:

```bash
# Test Nginx configuration
nginx -t

# If OK, reload Nginx
systemctl reload nginx

# Check status
systemctl status nginx
```

## Additional Flask Timeout Fix

Also increase Flask's timeout by editing the systemd service:

```bash
nano /etc/systemd/system/cloudface-pro.service
```

Add timeout environment variable in the `[Service]` section:

```ini
[Service]
...
Environment="TIMEOUT=600"
Environment="HOME=/home/www-data"
Environment="MPLCONFIGDIR=/tmp/matplotlib"
```

Then:

```bash
systemctl daemon-reload
systemctl restart cloudface-pro
```

## Summary of Limits After Fix

| Plan | Upload Limit | Max Size | Timeout |
|------|--------------|----------|---------|
| Free | 50 photos | 2GB | 5 min |
| Personal | 100 photos | 2GB | 5 min |
| Professional | 200 photos | 2GB | 5 min |
| Business | 300 photos | 2GB | 5 min |
| Business Plus | 500 photos | 2GB | 5 min |

## Test After Fix

1. Login to cloudface-ai.pro
2. Create an event
3. Upload 100+ photos
4. Should work without timeout!

