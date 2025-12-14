#!/usr/bin/env python3
"""
Script to identify crosslinking datasets from PRIDE projects and count their raw files.
Memory-optimized version using streaming JSON parsing.
"""

import argparse
import json
import logging
import os
import re
import sys
from collections import defaultdict
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def fix_json_string(s: str) -> str:
    """Fix JSON string by escaping unescaped newlines inside string values only."""
    result = []
    i = 0
    in_string = False
    escape_next = False
    
    while i < len(s):
        char = s[i]
        
        if escape_next:
            result.append(char)
            escape_next = False
            i += 1
            continue
        
        if char == '\\':
            result.append(char)
            escape_next = True
            i += 1
            continue
        
        if char == '"':
            in_string = not in_string
            result.append(char)
            i += 1
            continue
        
        if in_string:
            # Inside a string - escape control characters
            if char == '\n':
                result.append('\\n')
            elif char == '\r':
                result.append('\\r')
            elif char == '\t':
                result.append('\\t')
            elif ord(char) < 32 and char not in ['\n', '\r', '\t']:
                # Remove other control characters
                pass
            else:
                result.append(char)
        else:
            # Outside a string - keep as is (newlines are valid whitespace)
            result.append(char)
        
        i += 1
    
    return ''.join(result)

def load_json_file_robust(filepath: str):
    """Load JSON file with robust error handling."""
    logger.info(f"Loading JSON file: {filepath}")
    
    # Try to load with orjson first (faster)
    try:
        import orjson
        logger.info("Attempting to load with orjson (fast path)...")
        with open(filepath, 'rb') as f:
            content = f.read()
            logger.info(f"Read {len(content):,} bytes from file")
            # Clean control characters
            content_clean = re.sub(rb'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', b'', content)
            logger.info("Parsing JSON with orjson...")
            result = orjson.loads(content_clean)
            logger.info(f"Successfully loaded JSON with orjson (found {len(result) if isinstance(result, list) else 'object'} items)")
            return result
    except Exception as e:
        logger.info(f"orjson loading failed: {e}, falling back to standard json")
    
    # Fallback to standard json with cleaning
    logger.info("Using standard json library...")
    with open(filepath, 'rb') as f:
        content = f.read()
    logger.info(f"Read {len(content):,} bytes from file")
    
    # Decode and clean
    try:
        content_str = content.decode('utf-8')
    except UnicodeDecodeError:
        logger.warning("UTF-8 decode error, using error replacement")
        content_str = content.decode('utf-8', errors='replace')
    
    # Fix JSON by escaping control characters in strings
    logger.info("Fixing JSON string (escaping control characters)...")
    content_str = fix_json_string(content_str)
    
    # Try to parse
    try:
        logger.info("Parsing JSON...")
        result = json.loads(content_str)
        if isinstance(result, list):
            logger.info(f"Successfully loaded JSON (found list with {len(result)} items)")
        elif isinstance(result, dict):
            logger.info(f"Successfully loaded JSON (found dict with {len(result)} keys)")
        else:
            logger.info(f"Successfully loaded JSON (found {type(result).__name__})")
        return result
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        logger.error(f"Error at position {e.pos}")
        # Try to show context
        if e.pos:
            start = max(0, e.pos - 200)
            end = min(len(content_str), e.pos + 200)
            logger.error(f"Context: {repr(content_str[start:end])}")
        
        # Try to fix common issues: unescaped quotes in strings
        # This is a simplified fix - might not work for all cases
        logger.error("Attempting to fix JSON...")
        # Replace unescaped newlines in strings (but this is complex)
        # For now, let's try to use a more lenient approach
        raise

def is_crosslinking_dataset_llm(project: dict, model_name: str = 'llama3.2', temperature: float = 0.0, keywords: List[str] = None) -> bool:
    """Check if a project is a crosslinking dataset using LLM classification.
    
    Args:
        project: Project dictionary to analyze
        model_name: Name of the LLM model to use (default: 'llama3.2')
        temperature: Temperature for LLM generation (default: 0.0 for deterministic)
        keywords: Keywords list for fallback (optional)
    """
    # Prepare text to analyze
    text_parts = [
        project.get('title', ''),
        project.get('projectDescription', ''),
        project.get('sampleProtocol', ''),
        project.get('dataProtocol', ''),
        ' '.join(project.get('keywords', [])),
        ' '.join([tag.get('name', '') if isinstance(tag, dict) else str(tag) 
                 for tag in project.get('projectTags', [])])
    ]
    text_to_analyze = ' '.join([p for p in text_parts if p]).strip()
    
    if not text_to_analyze:
        return False
    
    # Truncate if too long (keep first 2000 chars for context)
    if len(text_to_analyze) > 2000:
        text_to_analyze = text_to_analyze[:2000] + "..."
    
    prompt = f"""Determine if this proteomics dataset is related to crosslinking mass spectrometry (XL-MS) or proximity labeling.

A crosslinking dataset typically involves:
- Chemical crosslinking (e.g., DSS, BS3, DSG, disuccinimidyl)
- Cross-link mass spectrometry (XL-MS, cross-linking MS)
- Proximity labeling (e.g., BioID, TurboID, APEX)
- Protein-protein interaction mapping via crosslinking
- Structural proteomics using crosslinkers

Dataset information:
{text_to_analyze}

Respond with ONLY "YES" if this is a crosslinking/proximity labeling dataset, or "NO" if it is not. Do not include any other text."""

    try:
        import ollama
        try:
            response = ollama.chat(
                model=model_name,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }],
                options={'temperature': temperature}
            )
        except Exception as e:
            # Try with :latest suffix if model not found
            if ':latest' not in model_name:
                logger.debug(f'Model {model_name} not found, trying {model_name}:latest')
                try:
                    response = ollama.chat(
                        model=f"{model_name}:latest",
                        messages=[{
                            'role': 'user',
                            'content': prompt
                        }],
                        options={'temperature': temperature}
                    )
                except Exception:
                    raise e
            else:
                raise e
        answer = response['message']['content'].strip().upper()
        return answer.startswith('YES')
    except ImportError:
        logger.warning("Ollama not available, falling back to keyword matching")
        return is_crosslinking_dataset_keywords(project, keywords=keywords)
    except Exception as e:
        logger.warning(f"LLM classification failed: {e}, falling back to keyword matching")
        return is_crosslinking_dataset_keywords(project, keywords=keywords)

# Default keywords for crosslinking detection
DEFAULT_CROSSLINKING_KEYWORDS = [
    'crosslink', 'cross-link', 'crosslinking', 'cross-linking',
    'xl-ms', 'xlms', 'xl ms', 'cross-link mass spectrometry',
    'chemical crosslinking', 'protein crosslinking',
    'disuccinimidyl', 'dss', 'bs3', 'dssd', 'dsg',
    'zero-length crosslink', 'photo-crosslink',
    'proximity-dependent', 'proximity labeling'
]

def is_crosslinking_dataset_keywords(project: dict, keywords: List[str] = None) -> bool:
    """Check if a project is a crosslinking dataset based on keywords."""
    # Use provided keywords or default
    if keywords is None:
        keywords = DEFAULT_CROSSLINKING_KEYWORDS
    
    # Fields to search in
    search_text = ' '.join([
        project.get('title', ''),
        project.get('projectDescription', ''),
        project.get('sampleProtocol', ''),
        project.get('dataProtocol', ''),
        ' '.join(project.get('keywords', [])),
        ' '.join([tag.get('name', '') if isinstance(tag, dict) else str(tag) 
                 for tag in project.get('projectTags', [])])
    ]).lower()
    
    # Check if any keyword is found
    return any(keyword.lower() in search_text for keyword in keywords)

def is_crosslinking_dataset(project: dict, use_llm: bool = True, keywords: List[str] = None, llm_model: str = 'llama3.2', llm_temperature: float = 0.0) -> bool:
    """Check if a project is a crosslinking dataset using LLM or keywords."""
    if use_llm:
        return is_crosslinking_dataset_llm(project, model_name=llm_model, temperature=llm_temperature, keywords=keywords)
    else:
        return is_crosslinking_dataset_keywords(project, keywords=keywords)

def count_raw_files_streaming(filepath: str) -> Dict[str, int]:
    """Count raw files per project accession using streaming JSON parsing."""
    logger.info(f"Counting raw files from {filepath} (streaming mode)...")
    raw_file_counts = defaultdict(int)
    raw_files_found = 0
    
    try:
        import ijson
        logger.info("Using ijson for streaming JSON parsing...")
        
        try:
            with open(filepath, 'rb') as f:
                parser = ijson.items(f, 'item')
                for idx, file_entry in enumerate(parser):
                    if (idx + 1) % 100000 == 0:
                        logger.info(f"  Processed {idx + 1:,} file entries (found {raw_files_found:,} raw files so far)...")
                    
                    file_category = file_entry.get('fileCategory', {})
                    if isinstance(file_category, dict):
                        category_value = file_category.get('value', '')
                        if category_value == 'RAW':
                            raw_files_found += 1
                            project_accessions = file_entry.get('projectAccessions', [])
                            for accession in project_accessions:
                                raw_file_counts[accession] += 1
            
            logger.info(f"Found {raw_files_found:,} raw files across {len(raw_file_counts):,} projects")
            return dict(raw_file_counts)
        except (ijson.common.JSONError, ijson.common.IncompleteJSONError) as e:
            logger.warning(f"Streaming JSON parsing failed: {e}")
            logger.warning("Falling back to robust JSON loader (may use more memory)")
            files_metadata = load_json_file_robust(filepath)
            return count_raw_files(files_metadata)
    except ImportError:
        logger.warning("ijson not available, falling back to loading entire file (may use more memory)")
        files_metadata = load_json_file_robust(filepath)
        return count_raw_files(files_metadata)

def count_raw_files(files_metadata: List[dict]) -> Dict[str, int]:
    """Count raw files per project accession (fallback method)."""
    logger.info(f"Counting raw files from {len(files_metadata):,} file entries...")
    raw_file_counts = defaultdict(int)
    raw_files_found = 0
    
    for idx, file_entry in enumerate(files_metadata):
        if (idx + 1) % 100000 == 0:
            logger.info(f"  Processed {idx + 1:,} / {len(files_metadata):,} file entries...")
        
        file_category = file_entry.get('fileCategory', {})
        if isinstance(file_category, dict):
            category_value = file_category.get('value', '')
            if category_value == 'RAW':
                raw_files_found += 1
                project_accessions = file_entry.get('projectAccessions', [])
                for accession in project_accessions:
                    raw_file_counts[accession] += 1
    
    logger.info(f"Found {raw_files_found:,} raw files across {len(raw_file_counts):,} projects")
    return dict(raw_file_counts)

def process_single_project(project: dict, raw_file_counts: Dict[str, int], use_llm: bool, keywords: List[str], llm_model: str, llm_temperature: float, stats: dict) -> Optional[dict]:
    """Process a single project and return project data if it's a crosslinking dataset.
    
    Args:
        project: Project dictionary to process
        raw_file_counts: Dictionary mapping accession to raw file counts
        use_llm: Whether to use LLM for classification
        keywords: List of keywords for keyword-based filtering
        llm_model: LLM model name
        llm_temperature: LLM temperature
        stats: Dictionary with keys "keyword_matches" and "llm_verified" (both int) to update with statistics
    
    Returns:
        Project dictionary if it's a crosslinking dataset, None otherwise
    """
    if use_llm:
        # First do fast keyword check
        if is_crosslinking_dataset_keywords(project, keywords):
            stats['keyword_matches'] += 1
            # Verify with LLM
            if is_crosslinking_dataset_llm(project, model_name=llm_model, temperature=llm_temperature, keywords=keywords):
                stats['llm_verified'] += 1
                accession = project.get('accession', '')
                submission_date = project.get('submissionDate', '')
                title = project.get('title', '')
                num_raw_files = raw_file_counts.get(accession, 0)
                
                logger.debug(f"LLM verified crosslinking dataset: {accession} - {title[:50]}... ({num_raw_files} raw files)")
                
                return {
                    'accession': accession,
                    'submissionDate': submission_date,
                    'title': title,
                    'numRawFiles': num_raw_files
                }
    else:
        # Just use keywords
        if is_crosslinking_dataset_keywords(project, keywords):
            accession = project.get('accession', '')
            submission_date = project.get('submissionDate', '')
            title = project.get('title', '')
            num_raw_files = raw_file_counts.get(accession, 0)
            
            logger.debug(f"Found crosslinking dataset: {accession} - {title[:50]}... ({num_raw_files} raw files)")
            
            return {
                'accession': accession,
                'submissionDate': submission_date,
                'title': title,
                'numRawFiles': num_raw_files
            }
    
    return None

def process_projects_streaming(filepath: str, raw_file_counts: Dict[str, int], use_llm: bool = True, keywords: List[str] = None, llm_model: str = 'llama3.2', llm_temperature: float = 0.0) -> List[dict]:
    """Process projects using streaming JSON parsing to reduce memory usage."""
    logger.info("Processing projects in streaming mode...")
    if use_llm:
        logger.info("Using LLM-based classification (with keyword pre-filtering)")
    else:
        logger.info("Using keyword-based classification")
    
    crosslinking_projects = []
    stats = {'keyword_matches': 0, 'llm_verified': 0}
    
    try:
        import ijson
        logger.info("Using ijson for streaming JSON parsing...")
        
        try:
            with open(filepath, 'rb') as f:
                parser = ijson.items(f, 'item')
                for idx, project in enumerate(parser):
                    if (idx + 1) % 10000 == 0:
                        logger.info(f"  Processed {idx + 1:,} projects (found {len(crosslinking_projects)} crosslinking datasets so far)...")
                    
                    result = process_single_project(project, raw_file_counts, use_llm, keywords, llm_model, llm_temperature, stats)
                    if result:
                        crosslinking_projects.append(result)
            
            if use_llm:
                logger.info(f"Keyword matches: {stats['keyword_matches']}, LLM verified: {stats['llm_verified']}")
            return crosslinking_projects
        except (ijson.common.JSONError, ijson.common.IncompleteJSONError) as e:
            logger.warning(f"Streaming JSON parsing failed: {e}")
            logger.warning("Falling back to robust JSON loader (may use more memory)")
            projects = load_json_file_robust(filepath)
            logger.info(f"Loaded {len(projects):,} projects")
            
            stats = {'keyword_matches': 0, 'llm_verified': 0}
            crosslinking_projects = []
            
            for idx, project in enumerate(projects):
                if (idx + 1) % 10000 == 0:
                    logger.info(f"  Processed {idx + 1:,} / {len(projects):,} projects (found {len(crosslinking_projects)} crosslinking datasets so far)...")
                
                result = process_single_project(project, raw_file_counts, use_llm, keywords, llm_model, llm_temperature, stats)
                if result:
                    crosslinking_projects.append(result)
            
            if use_llm:
                logger.info(f"Keyword matches: {stats['keyword_matches']}, LLM verified: {stats['llm_verified']}")
            return crosslinking_projects
    except ImportError:
        logger.warning("ijson not available, falling back to loading entire file (may use more memory)")
        projects = load_json_file_robust(filepath)
        logger.info(f"Loaded {len(projects):,} projects")
        
        stats = {'keyword_matches': 0, 'llm_verified': 0}
        crosslinking_projects = []
        
        for idx, project in enumerate(projects):
            if (idx + 1) % 10000 == 0:
                logger.info(f"  Processed {idx + 1:,} / {len(projects):,} projects (found {len(crosslinking_projects)} crosslinking datasets so far)...")
            
            result = process_single_project(project, raw_file_counts, use_llm, keywords, llm_model, llm_temperature, stats)
            if result:
                crosslinking_projects.append(result)
        
        if use_llm:
            logger.info(f"Keyword matches: {stats['keyword_matches']}, LLM verified: {stats['llm_verified']}")
        return crosslinking_projects

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Identify crosslinking datasets from PRIDE projects and count their raw files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --data-dir /path/to/data/
  %(prog)s --data-dir /path/to/data/ --no-llm
  %(prog)s --projects-file /path/to/projects.json --files-file /path/to/files.json
        """
    )
    
    parser.add_argument(
        '--data-dir',
        type=str,
        help='Directory containing all_pride_projects.json and all_pride_files_metadata.json files (required if --projects-file and --files-file not specified)'
    )
    parser.add_argument(
        '--projects-file',
        type=str,
        help='Path to all_pride_projects.json file (overrides --data-dir)'
    )
    parser.add_argument(
        '--files-file',
        type=str,
        help='Path to all_pride_files_metadata.json file (overrides --data-dir)'
    )
    parser.add_argument(
        '--no-llm',
        action='store_true',
        help='Disable LLM classification and use keyword-only matching (faster but less accurate). LLM is enabled by default.'
    )
    parser.add_argument(
        '--llm-model',
        type=str,
        default='llama3.2',
        help='LLM model name to use for classification (default: llama3.2). Must be available in Ollama.'
    )
    parser.add_argument(
        '--llm-temperature',
        type=float,
        default=0.0,
        help='Temperature for LLM generation (default: 0.0 for deterministic results). Range: 0.0-1.0'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='crosslinking_datasets_list.json',
        help='Output JSON file path (default: crosslinking_datasets_list.json)'
    )
    parser.add_argument(
        '--keywords',
        type=str,
        help='Comma-separated list of keywords to search for (default: built-in crosslinking keywords). Example: "crosslink,xl-ms,proximity labeling"'
    )
    parser.add_argument(
        '--keywords-file',
        type=str,
        help='Path to a text file with one keyword per line (overrides --keywords)'
    )
    
    args = parser.parse_args()
    
    # Load keywords
    if args.keywords_file:
        if not os.path.exists(args.keywords_file):
            logger.error(f"Keywords file not found: {args.keywords_file}")
            sys.exit(1)
        with open(args.keywords_file, 'r', encoding='utf-8') as f:
            keywords = [line.strip() for line in f if line.strip()]
        logger.info(f"Loaded {len(keywords)} keywords from file: {args.keywords_file}")
    elif args.keywords:
        keywords = [k.strip() for k in args.keywords.split(',') if k.strip()]
        logger.info(f"Using {len(keywords)} custom keywords from command line")
    else:
        keywords = DEFAULT_CROSSLINKING_KEYWORDS
        logger.info(f"Using {len(keywords)} default crosslinking keywords")
    
    # Determine file paths
    if args.projects_file and args.files_file:
        projects_file = args.projects_file
        files_metadata_file = args.files_file
    elif args.data_dir:
        data_dir = args.data_dir.rstrip('/')
        projects_file = os.path.join(data_dir, 'all_pride_projects.json')
        files_metadata_file = os.path.join(data_dir, 'all_pride_files_metadata.json')
    else:
        logger.error("Please specify either --data-dir or both --projects-file and --files-file")
        parser.print_help()
        sys.exit(1)
    
    # Validate files exist
    if not os.path.exists(projects_file):
        logger.error(f"Projects file not found: {projects_file}")
        sys.exit(1)
    if not os.path.exists(files_metadata_file):
        logger.error(f"Files metadata file not found: {files_metadata_file}")
        sys.exit(1)
    
    logger.info("="*80)
    logger.info("Starting crosslinking datasets identification script (memory-optimized)")
    logger.info("="*80)
    logger.info(f"Projects file: {projects_file}")
    logger.info(f"Files metadata file: {files_metadata_file}")
    
    # Count raw files using streaming (memory efficient)
    raw_file_counts = count_raw_files_streaming(files_metadata_file)
    logger.info(f"Found raw files for {len(raw_file_counts):,} projects")
    
    # Identify crosslinking datasets using streaming (memory efficient)
    # Use LLM for more accurate classification (set to False to use keyword-only)
    # Note: LLM classification will be slower but more accurate
    # The script uses a hybrid approach: keyword filtering first, then LLM verification
    use_llm = not args.no_llm
    llm_model = args.llm_model
    llm_temperature = args.llm_temperature
    
    # Validate temperature range
    if llm_temperature < 0.0 or llm_temperature > 1.0:
        logger.warning(f"Temperature {llm_temperature} is outside recommended range (0.0-1.0), using as-is")
    
    logger.info("Identifying crosslinking datasets...")
    if use_llm:
        logger.info("Using LLM-based classification (keyword pre-filtering + LLM verification)")
        logger.info(f"  LLM Model: {llm_model}")
        logger.info(f"  LLM Temperature: {llm_temperature}")
        logger.info("  This will take longer but provides more accurate results")
    else:
        logger.info("Using keyword-only classification (faster but less accurate)")
    crosslinking_projects = process_projects_streaming(
        projects_file, 
        raw_file_counts, 
        use_llm=use_llm, 
        keywords=keywords,
        llm_model=llm_model,
        llm_temperature=llm_temperature
    )
    
    logger.info(f"Found {len(crosslinking_projects)} crosslinking datasets")
    
    # Sort by number of raw files (descending - most raw files first)
    logger.info("Sorting datasets by number of raw files (descending)...")
    crosslinking_projects.sort(key=lambda x: x['numRawFiles'], reverse=True)
    
    # Output results
    output_file = args.output
    logger.info(f"Saving results to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(crosslinking_projects, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Results saved to {output_file}")
    
    # Print summary statistics
    total_raw_files = sum(p['numRawFiles'] for p in crosslinking_projects)
    avg_raw_files = total_raw_files / len(crosslinking_projects) if crosslinking_projects else 0
    max_raw_files = max((p['numRawFiles'] for p in crosslinking_projects), default=0)
    
    logger.info("="*80)
    logger.info("SUMMARY STATISTICS")
    logger.info("="*80)
    logger.info(f"Total crosslinking datasets: {len(crosslinking_projects)}")
    logger.info(f"Total raw files: {total_raw_files:,}")
    logger.info(f"Average raw files per dataset: {avg_raw_files:.1f}")
    logger.info(f"Maximum raw files in a dataset: {max_raw_files:,}")
    logger.info("="*80)
    
    # Also print a summary table (sorted by raw files)
    print("\n" + "="*100)
    print(f"{'Accession':<15} {'Raw Files':<12} {'Submission Date':<15} {'Title'}")
    print("="*100)
    for project in crosslinking_projects[:20]:  # Show first 20
        title_short = project['title'][:70] + '...' if len(project['title']) > 70 else project['title']
        print(f"{project['accession']:<15} {project['numRawFiles']:<12} {project['submissionDate']:<15} {title_short}")
    
    if len(crosslinking_projects) > 20:
        print(f"\n... and {len(crosslinking_projects) - 20} more (see {output_file} for full list)")
    
    logger.info("Script completed successfully")
    return crosslinking_projects

if __name__ == '__main__':
    main()

