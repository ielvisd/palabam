# Dependencies

## Production (`requirements.txt`)
Minimal dependencies for production deployment (Railway, App Runner, etc.):
- FastAPI, uvicorn - Web framework
- spacy, nltk, wordfreq - NLP/vocabulary analysis
- supabase - Database
- Essential utilities

Install: `pip install -r requirements.txt`

## Development (`requirements.dev.txt`)
Full dependencies including optional features and testing:
- All production dependencies
- pytest - Testing framework
- openai, anthropic - Chatbot features (optional)
- pdfplumber, python-docx - Document parsing (optional)
- boto3, scikit-learn - Additional features

Install: `pip install -r requirements.dev.txt`

## Why Two Files?

Production builds (Docker) need to be fast and lightweight. Development needs testing tools and optional features. The app code gracefully handles missing optional dependencies (chatbot, PDF parsing).

