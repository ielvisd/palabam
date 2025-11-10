#!/usr/bin/env python3
"""
Seed Words Database using Supabase MCP
Populates the words table with data from our frequency datasets
Uses bulk SQL inserts for efficiency
"""
import json
import sys
from pathlib import Path
from typing import Dict, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def calculate_difficulty_score(word: str, frequency: int, lexile: int = None) -> Tuple[int, str]:
    """
    Calculate difficulty score and relic type for a word
    Returns: (difficulty_score, relic_type)
    """
    word_lower = word.lower()
    
    # Calculate base difficulty (0-100 scale)
    if lexile is not None:
        # Use Lexile score directly (typically 0-1600, we'll normalize)
        difficulty = min(100, max(0, int((lexile / 1600) * 100)))
    elif frequency > 0:
        # Use frequency as inverse difficulty
        if frequency >= 10000:
            difficulty = 10  # Very common
        elif frequency >= 1000:
            difficulty = 30
        elif frequency >= 100:
            difficulty = 50
        elif frequency >= 10:
            difficulty = 70
        else:
            difficulty = 90  # Rare words
    else:
        # Fallback: use word length
        difficulty = min(90, max(10, len(word) * 5))
    
    # Map to relic type
    if difficulty < 25:
        relic_type = 'whisper'
    elif difficulty < 50:
        relic_type = 'echo'
    elif difficulty < 75:
        relic_type = 'resonance'
    else:
        relic_type = 'thunder'
    
    return difficulty, relic_type

def generate_sql_inserts(coca_data: Dict[str, int], lexile_data: Dict[str, int], limit: int = 1000) -> str:
    """
    Generate SQL INSERT statements for words using bulk INSERT
    """
    # Sort words by frequency (most common first)
    sorted_words = sorted(coca_data.items(), key=lambda x: x[1], reverse=True)
    
    values = []
    word_definitions = {
        'resilient': 'able to recover quickly from difficulties',
        'perseverance': 'persistence in doing something despite difficulty',
        'curious': 'eager to know or learn something',
        'adventure': 'an exciting or dangerous experience',
        'challenge': 'a task or situation that tests ability',
        'accomplish': 'to achieve or complete successfully',
        'discover': 'to find something for the first time'
    }
    
    for word, frequency in sorted_words[:limit]:
        word_lower = word.lower()
        lexile = lexile_data.get(word_lower)
        difficulty, relic_type = calculate_difficulty_score(word_lower, frequency, lexile)
        
        # Get definition (or create a simple one)
        definition = word_definitions.get(word_lower, f"A word meaning {word_lower}")
        
        # Escape single quotes in strings
        word_escaped = word_lower.replace("'", "''")
        definition_escaped = definition.replace("'", "''")
        
        # Build VALUES clause
        lexile_val = str(lexile) if lexile else 'NULL'
        values.append(f"('{word_escaped}', '{definition_escaped}', '{relic_type}', {difficulty}, {frequency}, {lexile_val})")
    
    # Generate single bulk INSERT
    values_str = ',\n    '.join(values)
    sql = f"""INSERT INTO public.words (word, definition, relic_type, difficulty_score, coca_frequency, lexile_score)
VALUES
    {values_str}
ON CONFLICT (word) DO NOTHING;"""
    
    return sql

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate SQL for seeding words database')
    parser.add_argument(
        '--limit',
        type=int,
        default=1000,
        help='Maximum number of words to seed (default: 1000)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output SQL file (default: print to stdout)'
    )
    
    args = parser.parse_args()
    
    # Load datasets
    data_dir = Path(__file__).parent.parent / "data"
    coca_path = data_dir / "coca_frequency.json"
    lexile_path = data_dir / "lexile_scores.json"
    
    if not coca_path.exists():
        print(f"Error: COCA dataset not found at {coca_path}")
        sys.exit(1)
    
    print(f"Loading datasets...")
    with open(coca_path, 'r', encoding='utf-8') as f:
        coca_data = json.load(f)
    
    lexile_data = {}
    if lexile_path.exists():
        with open(lexile_path, 'r', encoding='utf-8') as f:
            lexile_data = json.load(f)
    
    print(f"Loaded {len(coca_data)} COCA words and {len(lexile_data)} Lexile scores")
    print(f"Generating SQL for {args.limit} words...")
    
    # Generate SQL
    sql = generate_sql_inserts(coca_data, lexile_data, limit=args.limit)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(sql)
        print(f"SQL written to {args.output}")
        print(f"\nTo apply this migration, use:")
        print(f"  mcp_supabase_apply_migration --name seed_words --query \"$(cat {args.output})\"")
    else:
        print("\n" + "="*80)
        print(sql)
        print("="*80)
        print(f"\nGenerated SQL for {args.limit} words")
        print("Use --output to save to a file")

if __name__ == '__main__':
    main()

