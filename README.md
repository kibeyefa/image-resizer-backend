# PixelPerfect Resizer - Backend

Django REST API for image processing with resizing, format conversion, and cropping capabilities.

## Features

- Image resizing with quality control
- Format conversion (JPEG, PNG, WEBP, AVIF)
- Smart cropping (center crop, custom crop)
- Metadata stripping option
- Smart sharpening
- Rate limiting (100 requests/hour per IP)
- File size validation (50MB max)
- Health check endpoint for monitoring

## Requirements

- Python 3.11+
- See `requirements.txt` for dependencies

## Local Development

### Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run migrations (if needed)
python manage.py migrate

# Run development server
python manage.py runserver
```

### Environment Variables

Create a `.env` file with:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health/` | GET | Health check (unlimited) |
| `/api/v1/resize/` | POST | Resize image |
| `/api/v1/docs/` | GET | Swagger UI documentation |
| `/api/v1/redoc/` | GET | ReDoc documentation |

## Deployment on Render

### Option 1: Using render.yaml (Recommended)

1. Push this repository to GitHub
2. Go to [render.com](https://render.com) and sign up/login
3. Click "New" → "Blueprint"
4. Connect your GitHub repository
5. Render will auto-detect `render.yaml` and deploy

### Option 2: Manual Setup

1. Go to [render.com](https://render.com) and sign up/login
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: pixelperfect-backend
   - **Environment**: Python 3
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn pixelperfect.wsgi:application -c gunicorn.conf.py`
5. Add environment variables:
   - `SECRET_KEY`: Generate a random string
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `your-app.onrender.com`

## Keep-Alive Setup (UptimeRobot)

To prevent cold starts on Render's free tier:

1. Go to [uptimerobot.com](https://uptimerobot.com) and create a free account
2. Click "Add New Monitor"
3. Configure:
   - **Monitor Type**: HTTP(s)
   - **Friendly Name**: PixelPerfect Backend
   - **URL**: `https://your-app.onrender.com/api/v1/health/`
   - **Monitoring Interval**: 10 minutes
4. Save the monitor

This will ping your backend every 10 minutes to keep it awake.

## Rate Limiting

- **Default**: 100 requests/hour per IP address
- **Health endpoint**: Unlimited (doesn't count against limit)
- Response headers include:
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Seconds until limit resets

## File Validation

- **Max file size**: 50MB
- **Allowed formats**: JPEG, PNG, WEBP, AVIF, GIF
- **Max dimensions**: 10,000 x 10,000 pixels

## Security Features

- CORS restricted to Netlify/Vercel domains
- Rate limiting per IP
- File size validation
- File type validation
- Secure headers in production
- No sensitive data in error responses

## License

MIT License
