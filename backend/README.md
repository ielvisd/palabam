# Palabam Backend

FastAPI backend for the Palabam vocabulary learning platform.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download spaCy language model:
```bash
python -m spacy download en_core_web_sm
```

4. Download NLTK data:
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

5. Set up environment variables (create `.env` file):
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1
```

6. Run the server:
```bash
pnpm dev
# or
uvicorn main:app --reload
```

