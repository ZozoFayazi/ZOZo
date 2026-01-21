# Environment Variables - Complete Reference

## Backend Environment Variables

**File:** `/app/backend/.env`

### Database
```bash
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"
```
- `MONGO_URL`: Pre-configured MongoDB connection
- `DB_NAME`: Database name (zozo_burger collection)
- ⚠️ **DO NOT CHANGE** - These are managed by the platform

### API Configuration
```bash
CORS_ORIGINS="*"
APP_URL="https://foodorder-fix.preview.emergentagent.com"
```
- `CORS_ORIGINS`: CORS policy ("*" allows all origins)
- `APP_URL`: Application base URL for callbacks and emails
- ℹ️ `APP_URL` can be updated if preview URL changes

### Email Service (Resend)
```bash
RESEND_API_KEY=re_KS2rud3s_GSvEJZHwnpLdJm9TU5WuK18g
SENDER_EMAIL=noreply@zozo-burger.de
RESEND_USE_TEST_DOMAIN=false
POS_ALERT_EMAIL=info@zozo-burger.de
INCLUDE_ORDER_DETAILS_IN_ALERT_EMAIL=false
```
- `RESEND_API_KEY`: API key for Resend email service
- `SENDER_EMAIL`: From address for transactional emails
- `RESEND_USE_TEST_DOMAIN`: Use Resend test domain (false = production)
- `POS_ALERT_EMAIL`: Email for POS failure alerts
- `INCLUDE_ORDER_DETAILS_IN_ALERT_EMAIL`: Include order details in alert emails

### Security (JWT)
```bash
JWT_SECRET=uKoRwC3BpBOQmf_XfTD5QdtU3fTuxTgBjvbPnTGAngjAReUUIDJirlPLcwxGwgNync49zQly0-_1Md_oknHvJw
ADMIN_JWT_SECRET=eGOlbffRwRjsTGcKja83e6Bt5yJdrF0Wg_6jat3Q6TPj5hGWuVKewbamL4RUV2DDuP0l-_DJ49LGHEk7Lv9fag
```
- `JWT_SECRET`: Secret for customer JWT tokens
- `ADMIN_JWT_SECRET`: Secret for admin JWT tokens
- ⚠️ **Rotated on:** 06.01.2026
- ⚠️ **DO NOT CHANGE** unless rotating secrets intentionally

### AI Integration
```bash
EMERGENT_LLM_KEY=sk-emergent-5882954D84fC35cB4D
```
- `EMERGENT_LLM_KEY`: Universal key for LLM services
- ℹ️ Used if AI features are enabled

---

## Frontend Environment Variables

**File:** `/app/frontend/.env`

```bash
REACT_APP_BACKEND_URL=https://foodorder-fix.preview.emergentagent.com
WDS_SOCKET_PORT=443
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
```

### Critical Variables
- `REACT_APP_BACKEND_URL`: Backend API URL
  - ⚠️ **DO NOT CHANGE** - Ingress routing depends on this
  - Must match the preview URL
  - All API calls use this with `/api` prefix

### Development Variables
- `WDS_SOCKET_PORT`: WebSocket port for hot reload (443 for HTTPS)
- `REACT_APP_ENABLE_VISUAL_EDITS`: Enable visual editing features
- `ENABLE_HEALTH_CHECK`: Enable health check endpoint

---

## Database Configuration (Not in .env)

### PayPal Credentials
**Stored in:** `locations` collection, per location

#### Rellingen
```json
{
  "paypal_client_id": "Ac94dFnQk1qbwEndBfUOAODPMQBhskka3iMusznawOaezGYjzSUpKoyPk5EBgLzKNAgwKEK_UHcUdRB7",
  "paypal_secret_key": "EKX-jMnXB6jQkIl5tw1XakUfHIguAKeQimrMfyD9P9bBN_tnCxcRsAyJ88j2F-nSnVCyMDHzc669exAB",
  "paypal_sandbox_mode": false,
  "paypal_enabled": true
}
```

#### Henstedt-Ulzburg
```json
{
  "paypal_client_id": "AR7Brjjwwg432MxkzLiRMMeZdtynccfZyUZtpFCTllt2NfKNlIa3ftX6jLH_iDssVdrDMRB8YUmcY9kz",
  "paypal_secret_key": "EHTM6aK5qDXaWn_dXWhEPa32PVJjcByO4xoHLb1r3K-v2TMv0MVQ-KmwwTf5KvMCyja7gSi2a7n8wv8J",
  "paypal_sandbox_mode": false,
  "paypal_enabled": true
}
```

### ExpertOrder POS Configuration
**Stored in:** `locations` collection, per location, in `pos_config` field

#### Rellingen
```json
{
  "pos_config": {
    "provider": "expertorder",
    "enabled": true,
    "api_key": "4bbc443c82674f93e910399ca7931b37b45e55ba",
    "base_url": "https://zozo.eocloud.de",
    "broker_name": "zozo-burger.de",
    "test_mode": false
  }
}
```

#### Henstedt-Ulzburg
```json
{
  "pos_config": {
    "provider": "expertorder",
    "enabled": true,
    "api_key": "90dd43e5c58b7c2a8ddd1eb4916ae8196d8e1073",
    "base_url": "https://zozo.eocloud.de",
    "broker_name": "zozo-burger.de",
    "test_mode": false
  }
}
```

---

## How to Access in Code

### Backend (Python)
```python
import os

# From .env file
mongo_url = os.environ.get('MONGO_URL')
app_url = os.environ.get('APP_URL')
jwt_secret = os.environ.get('JWT_SECRET')

# From database
async def get_paypal_config(location_id):
    location = await db.locations.find_one({"id": location_id})
    return {
        "client_id": location.get('paypal_client_id'),
        "secret": location.get('paypal_secret_key'),
        "sandbox": location.get('paypal_sandbox_mode', True)
    }
```

### Frontend (JavaScript)
```javascript
// From .env file
const backendUrl = process.env.REACT_APP_BACKEND_URL;
// OR
const backendUrl = import.meta.env.REACT_APP_BACKEND_URL;

// Example API call
fetch(`${backendUrl}/api/locations`)
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## Environment Variable Update Process

### When to restart services:
1. ✅ After changing ANY variable in `.env` files
2. ✅ After updating `package.json` or `requirements.txt`
3. ❌ NOT needed for database config changes (PayPal, POS)

### How to restart:
```bash
# Restart backend
supervisorctl restart backend

# Restart frontend
supervisorctl restart frontend

# Restart both
supervisorctl restart all

# Check status
supervisorctl status
```

---

## Security Best Practices

### ✅ DO:
- Keep secrets in environment variables or database
- Use strong, randomly generated JWT secrets
- Rotate secrets periodically
- Use LIVE mode for PayPal in production
- Use non-test mode for ExpertOrder in production

### ❌ DON'T:
- Hardcode secrets in code
- Commit `.env` files to git (use `.env.example` instead)
- Share secrets in plain text
- Use test/sandbox mode in production
- Expose secrets in logs or error messages

---

## Troubleshooting

### "PayPal authentication failed"
1. Check if `paypal_client_id` and `paypal_secret_key` are set in database for the location
2. Verify `paypal_sandbox_mode` matches your credentials (false for LIVE, true for SANDBOX)
3. Test credentials in PayPal Developer Dashboard

### "POS connection failed"
1. Check if `pos_config.enabled` is true
2. Verify `pos_config.api_key` is correct
3. Check `pos_config.base_url` is https://zozo.eocloud.de
4. Test with curl: `curl -H "API_KEY: <your_key>" https://zozo.eocloud.de/api/v1/osp`

### "Backend not responding"
1. Check backend logs: `tail -f /var/log/supervisor/backend.*.log`
2. Verify `MONGO_URL` is correct
3. Restart backend: `supervisorctl restart backend`

### "Frontend can't reach backend"
1. Check `REACT_APP_BACKEND_URL` matches preview URL
2. Check CORS is configured: `CORS_ORIGINS="*"` in backend `.env`
3. Verify backend is running: `supervisorctl status backend`
4. Test backend: `curl https://foodorder-fix.preview.emergentagent.com/api/`

---

## Backup & Restore

See `/app/CONFIG_LOCKED_FINAL.md` for complete backup and restore instructions.

**Quick Restore:**
```bash
cd /app
python3 restore_all_configs_final.py
```
