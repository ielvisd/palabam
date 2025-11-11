"""
Supabase Client Setup
Creates and manages the Supabase client instance
"""
import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Global Supabase client instance
_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """
    Get or create Supabase client instance
    Uses environment variables for configuration
    """
    global _supabase_client
    
    if _supabase_client is None:
        supabase_url = os.getenv("SUPABASE_URL")
        # Prioritize SUPABASE_SERVICE_ROLE_KEY, then SUPABASE_KEY
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError(
                "Supabase credentials not found. "
                "Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_KEY) "
                "in your .env file"
            )
        
        # Verify it's a service role key (should be long JWT, 200+ chars)
        if len(supabase_key) < 200 or not supabase_key.startswith("eyJ"):
            logger.warning(
                "WARNING: SUPABASE_KEY might not be a service role key. "
                "Service role keys are long JWT tokens (200+ chars). "
                "Get it from: Supabase Dashboard > Settings > API > service_role key"
            )
        
        _supabase_client = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized with service role key")
    
    return _supabase_client

def reset_client():
    """Reset the client (useful for testing)"""
    global _supabase_client
    _supabase_client = None

