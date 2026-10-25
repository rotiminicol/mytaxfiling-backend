# MyTaxFiling Backend API

Python FastAPI backend for the MyTaxFiling tax management and compliance platform.

## Features

- **Authentication**: JWT-based authentication with Supabase integration
- **User Management**: Profile management and user data
- **Document Tracking**: Compliance document management with expiry tracking
- **Document Reminders**: Configurable reminder preferences
- **E-Invoicing**: Full invoice management with clients, templates, and activities
- **Rent Receipts**: Digital rent receipt generation and certification
- **Admin Panel**: Role-based access control (RBAC) with audit logging
- **API Documentation**: Auto-generated Swagger/OpenAPI documentation

## Tech Stack

- **Framework**: FastAPI
- **Database**: Supabase (PostgreSQL)
- **Authentication**: JWT (Supabase Auth)
- **Validation**: Pydantic
- **Server**: Uvicorn

## Project Structure

```
mytaxfiling backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── admin.py          # Admin endpoints
│   │       │   ├── documents.py      # Document & reminder endpoints
│   │       │   ├── invoices.py       # Invoice, client, template endpoints
│   │       │   ├── profiles.py       # User profile endpoints
│   │       │   └── receipts.py       # Rent receipt endpoints
│   │       └── __init__.py
│   ├── core/
│   │   ├── config.py                 # Configuration settings
│   │   ├── rbac.py                   # Role-based access control
│   │   ├── security.py               # JWT authentication
│   │   └── supabase_client.py        # Supabase client setup
│   ├── models/
│   │   ├── document.py               # Document models
│   │   ├── invoice.py                # Invoice models
│   │   ├── profile.py                # Profile models
│   │   ├── receipt.py                # Receipt models
│   │   └── subscription.py           # Subscription & role models
│   └── __init__.py
├── main.py                           # Application entry point
├── requirements.txt                  # Python dependencies
├── .env.example                      # Environment variables template
└── README.md                         # This file
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- Supabase project with database schema set up
- Supabase Service Role Key (from project settings)

### 2. Installation

```bash
# Navigate to the backend directory
cd "mytaxfiling backend"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` with your Supabase credentials:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key
JWT_SECRET=your-jwt-secret-key
FRONTEND_URL=http://localhost:5173
```

**Important**: Get your keys from:
- Supabase URL: Project Settings > API > Project URL
- Service Role Key: Project Settings > API > service_role (secret)
- Anon Key: Project Settings > API > anon (public)
- JWT Secret: Project Settings > API > JWT Secret

### 4. Running the Server

```bash
# Development mode with auto-reload
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## API Endpoints

### Authentication

All endpoints (except `/health` and `/`) require JWT authentication in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

Get the JWT token from Supabase Auth in your frontend.

### Profiles

- `GET /api/v1/profiles/me` - Get current user's profile
- `PUT /api/v1/profiles/me` - Update current user's profile
- `GET /api/v1/profiles/{profile_id}` - Get specific profile (admin or own)

### Documents

#### Compliance Documents
- `GET /api/v1/documents/compliance` - Get all documents
- `POST /api/v1/documents/compliance` - Create document
- `GET /api/v1/documents/compliance/{id}` - Get document
- `PUT /api/v1/documents/compliance/{id}` - Update document
- `DELETE /api/v1/documents/compliance/{id}` - Delete document
- `PATCH /api/v1/documents/compliance/{id}/renewal` - Submit renewal

#### Document Reminders
- `GET /api/v1/documents/reminders` - Get reminder preferences
- `PUT /api/v1/documents/reminders` - Update reminder preferences

### Invoices

#### Invoices
- `GET /api/v1/invoices` - Get all invoices
- `POST /api/v1/invoices` - Create invoice
- `GET /api/v1/invoices/{id}` - Get invoice
- `PUT /api/v1/invoices/{id}` - Update invoice
- `DELETE /api/v1/invoices/{id}` - Delete invoice
- `PATCH /api/v1/invoices/{id}/send` - Mark as sent
- `PATCH /api/v1/invoices/{id}/pay` - Mark as paid

#### Clients
- `GET /api/v1/invoices/clients` - Get all clients
- `POST /api/v1/invoices/clients` - Create client
- `GET /api/v1/invoices/clients/{id}` - Get client
- `PUT /api/v1/invoices/clients/{id}` - Update client
- `DELETE /api/v1/invoices/clients/{id}` - Delete client

#### Templates
- `GET /api/v1/invoices/templates` - Get all templates
- `POST /api/v1/invoices/templates` - Create template
- `GET /api/v1/invoices/templates/{id}` - Get template
- `PUT /api/v1/invoices/templates/{id}` - Update template
- `DELETE /api/v1/invoices/templates/{id}` - Delete template
- `PATCH /api/v1/invoices/templates/{id}/use` - Increment usage count

#### Activities
- `GET /api/v1/invoices/activities` - Get recent activities

### Receipts

- `GET /api/v1/receipts` - Get all receipts
- `POST /api/v1/receipts` - Create receipt
- `GET /api/v1/receipts/{id}` - Get receipt
- `PUT /api/v1/receipts/{id}` - Update receipt
- `DELETE /api/v1/receipts/{id}` - Delete receipt
- `PATCH /api/v1/receipts/{id}/certify` - Certify receipt

### Admin (Admin Only)

- `GET /api/v1/admin/users` - Get all users
- `GET /api/v1/admin/users/{user_id}` - Get specific user
- `PUT /api/v1/admin/users/{user_id}/role` - Update user role
- `DELETE /api/v1/admin/users/{user_id}/role/{role}` - Remove user role
- `GET /api/v1/admin/audit-log` - Get audit log
- `GET /api/v1/admin/audit-log/user/{user_id}` - Get user audit log
- `GET /api/v1/admin/documents/all` - Get all documents
- `GET /api/v1/admin/invoices/all` - Get all invoices
- `GET /api/v1/admin/receipts/all` - Get all receipts

## Role-Based Access Control (RBAC)

The API supports three roles:
- **user**: Regular user access (own data only)
- **moderator**: Elevated access (moderator features)
- **admin**: Full access to all data and admin features

Admin endpoints require the `admin` role. User roles are managed through the Supabase `user_roles` table.

## Database Schema

The backend uses the existing Supabase database schema with these tables:
- `profiles` - User profiles
- `compliance_documents` - Document tracking
- `document_reminders` - Reminder preferences
- `invoice_clients` - Invoice clients
- `invoices` - Invoices
- `invoice_templates` - Invoice templates
- `invoice_activities` - Activity tracking
- `receipts` - Rent receipts
- `subscriptions` - User subscriptions
- `user_roles` - User roles
- `admin_audit_log` - Admin action logging

## Security Notes

1. **Service Role Key**: The backend uses the Supabase service role key which bypasses Row Level Security (RLS). This is necessary for admin operations. Keep this key secret and never expose it in client-side code.

2. **JWT Validation**: The backend validates JWT tokens from Supabase Auth. Ensure your JWT_SECRET matches your Supabase project's JWT secret.

3. **CORS**: Configure `FRONTEND_URLS` in your `.env` to only allow requests from your frontend domain.

4. **Admin Access**: Admin actions are logged in the `admin_audit_log` table for audit purposes.

## Development

### Adding New Endpoints

1. Create a new file in `app/api/v1/endpoints/`
2. Define your router and endpoints
3. Import and include the router in `app/api/v1/__init__.py`
4. Add Pydantic models in `app/models/` if needed

### Adding New Models

1. Create a new file in `app/models/`
2. Define Base, Create, Update, and Response models using Pydantic
3. Import models in your endpoint files

## Testing

You can test the API using:
- Swagger UI at http://localhost:8000/api/docs
- ReDoc at http://localhost:8000/api/redoc
- curl or Postman with JWT authentication

Example curl request:

```bash
curl -X GET http://localhost:8000/api/v1/profiles/me \
  -H "Authorization: Bearer <your-jwt-token>"
```

## Frontend Integration

To integrate with your frontend:

1. Get the JWT token from Supabase Auth in your frontend
2. Include it in the Authorization header for all API requests
3. The backend will validate the token and extract the user_id
4. All data operations are scoped to the authenticated user

Example frontend fetch:

```javascript
const token = await supabase.auth.getSession();
const response = await fetch('http://localhost:8000/api/v1/profiles/me', {
  headers: {
    'Authorization': `Bearer ${token.data.session.access_token}`
  }
});
```

## Deployment

### Production Deployment

1. Set environment variables in your hosting platform
2. Use a production ASGI server (Gunicorn + Uvicorn workers)
3. Enable HTTPS
4. Configure CORS for your production frontend URL
7. Monitor logs and set up alerts

Example production command:

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Troubleshooting

### JWT Validation Errors

If you get "Could not validate credentials":
- Ensure JWT_SECRET matches your Supabase project JWT secret
- Check that the token is not expired
- Verify the token format (should be from Supabase Auth)

### Supabase Connection Errors

If you get connection errors:
- Verify SUPABASE_URL is correct
- Check that your service role key is valid
- Ensure your Supabase project is active

### CORS Errors

If you get CORS errors:
- Add your frontend URL to FRONTEND_URLS in .env
- Ensure the backend is running before making requests from frontend

## License

This backend is part of the MyTaxFiling project.
