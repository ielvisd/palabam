#!/usr/bin/env python3
"""
Seed Words Database
Populates the words table with data from our frequency datasets
"""
import json
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.words import create_word
from db.supabase_client import get_supabase_client
from nlp.dataset_loader import get_dataset_loader

async def seed_words_from_datasets(limit: int = 1000):
    """
    Seed words table from COCA/Lexile datasets
    
    Args:
        limit: Maximum number of words to seed (default 1000)
    """
    print(f"Seeding words database (limit: {limit})...")
    
    dataset_loader = get_dataset_loader()
    coca_data = dataset_loader.coca_data
    lexile_data = dataset_loader.lexile_data
    
    if not coca_data:
        print("No COCA data available. Run generate_datasets.py first.")
        return
    
    # Get word definitions (simplified - in production, use a dictionary API)
    # For now, we'll create basic definitions
    word_definitions = {
        'resilient': 'able to recover quickly from difficulties',
        'perseverance': 'persistence in doing something despite difficulty',
        'curious': 'eager to know or learn something',
        'adventure': 'an exciting or dangerous experience',
        'challenge': 'a task or situation that tests ability',
        'accomplish': 'to achieve or complete successfully',
        'discover': 'to find something for the first time'
    }
    
    seeded_count = 0
    skipped_count = 0
    
    # Sort words by frequency (most common first)
    sorted_words = sorted(coca_data.items(), key=lambda x: x[1], reverse=True)
    
    for word, frequency in sorted_words[:limit]:
        try:
            # Calculate difficulty and relic type
            difficulty, relic_type = dataset_loader.calculate_difficulty_score(word)
            
            # Get Lexile score if available
            lexile = lexile_data.get(word)
            
            # Get definition (or create a simple one)
            definition = word_definitions.get(word, f"A word meaning {word}")
            
            # Create word in database
            await create_word(
                word=word,
                definition=definition,
                relic_type=relic_type,
                difficulty_score=difficulty,
                coca_frequency=frequency,
                lexile_score=lexile
            )
            
            seeded_count += 1
            
            if seeded_count % 100 == 0:
                print(f"Seeded {seeded_count} words...")
                
        except Exception as e:
            # Word might already exist, skip
            skipped_count += 1
            if skipped_count <= 10:  # Only log first 10 errors
                print(f"Warning: Could not seed '{word}': {e}")
    
    print(f"\nSeeding complete!")
    print(f"  - Seeded: {seeded_count} words")
    print(f"  - Skipped: {skipped_count} words")

async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Seed words database from datasets')
    parser.add_argument(
        '--limit',
        type=int,
        default=1000,
        help='Maximum number of words to seed (default: 1000)'
    )
    
    args = parser.parse_args()
    
    try:
        # Test Supabase connection
        client = get_supabase_client()
        print("✓ Supabase connection successful")
        
        await seed_words_from_datasets(limit=args.limit)
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure:")
        print("  1. Supabase credentials are set in .env file")
        print("  2. Database migrations have been applied")
        print("  3. Words table exists")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())

