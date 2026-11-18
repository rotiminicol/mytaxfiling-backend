# MyTaxFiling Backend Deployment Guide

## Local Development

### Prerequisites
- Python 3.9+
- Virtual environment

### Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

The backend will run on `http://localhost:8000`

## Vercel Production Deployment

### Environment Variables (Required)

Add these in your Vercel project settings (Settings > Environment Variables):

```env
SUPABASE_URL=SET_IN_VERCEL_ENVIRONMENT
SUPABASE_SERVICE_ROLE_KEY=SET_IN_VERCEL_ENVIRONMENT
SUPABASE_ANON_KEY=SET_IN_VERCEL_ENVIRONMENT
SUPABASE_PUBLISHABLE_KEY=SET_IN_VERCEL_ENVIRONMENT
SUPABASE_SECRET_KEY=SET_IN_VERCEL_ENVIRONMENT
SUPABASE_JWKS_URL=SET_IN_VERCEL_ENVIRONMENT
DATABASE_URL=SET_IN_VERCEL_ENVIRONMENT
JWT_SECRET=SET_IN_VERCEL_ENVIRONMENT
RESEND_API_KEY=SET_IN_VERCEL_ENVIRONMENT
```

### Deployment Steps

1. **Install Vercel CLI** (if not installed)
   ```bash
   npm install -g vercel
   ```

2. **Connect to Vercel** (if not already connected)
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel
   ```

4. **Set Environment Variables**
   - Go to Vercel Dashboard > your project > Settings > Environment Variables
   - Add all the variables listed above
   - Select "Production" environment
   - Click "Save"
   - Redeploy after adding variables

### Important: After Adding Environment Variables

After adding environment variables, you must **Redeploy**:
- Go to Vercel Dashboard > your project > Deployments
- Click the three dots on the latest deployment
- Select "Redeploy"

### API Endpoints

**Production URL:** https://mytaxfiling-backend.vercel.app

**Test Email Endpoint:**
```
POST https://mytaxfiling-backend.vercel.app/api/v1/test/test-email
Content-Type: application/json

{
  "email": "your-email@example.com",
  "test_type": "otp"
}
```

**Health Check:**
```
GET https://mytaxfiling-backend.vercel.app/health
```

**API Documentation:**
```
https://mytaxfiling-backend.vercel.app/api/docs
```

## Current Configuration

### Local
- Server: http://localhost:8000
- Frontend URLs: http://localhost:5173, http://localhost:3000

### Production (Vercel)
- Server: https://mytaxfiling-backend.vercel.app
- Frontend URLs: https://taxfiling.com.ng, https://www.taxfiling.com.ng

## Email Configuration

- **From:** noreply@mytaxfiling.com.ng
- **Provider:** Resend
- **Status:** ✅ Domain verified

## Database

- **Provider:** Supabase PostgreSQL
- **Connection:** Direct connection string configured
- **Status:** ✅ Connected

## Security Notes

⚠️ **Important:**
- Never commit `.env` file to git
- Keep service role keys secure
- Update JWT_SECRET for production
- Ensure database password is strong
