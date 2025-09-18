import re
import datetime
import json
import os
from pathlib import Path
def count_words(text):
    """Count words in a string (split on whitespace)."""
    return len(text.split())

from plaintex import CleanerConfig, CitationManager, LaTeXCleaner

def extract_project_plaintext(root_dir, folders=None, include_glob=None):
    """
    Extract plain text from a LaTeX project using PlainTeX.
    Returns a dict with 'files' (filename: text) and 'citations' (sorted citations).
    """
    if folders is None:
        folders = ["."]
    if include_glob is None:
        include_glob = ["**/*.tex"]
    cfg = {
        "root_dir": root_dir,
        "folders": folders,
        "include_glob": include_glob,
        "extra_extensions": [".tex"],
        "output_json": "",
        "normalize_whitespace": True,
    }
    conf = CleanerConfig.model_validate(cfg)
    citations = CitationManager()
    cleaner = LaTeXCleaner(conf, citations)
    files_map = cleaner.extract_project_texts()
    files_map, sorted_citations = citations.renumber_alphabetically(files_map)
    return {"files": files_map, "citations": sorted_citations}


def parse_latex_metrics(files_map, bib_path=None):
    """
    Parse LaTeX files for metrics: word count, figures, tables, algorithms, equations, citations.
    Optionally parse .bib file for total entries and citation coverage.
    Returns a dict of metrics.
    """
    # Count words from plain text
    words_total = sum(count_words(text) for text in files_map.values())

    # Parse environments and citations from raw LaTeX source
    # Find all .tex files in the project root and subfolders
    tex_files = []
    for root, dirs, files in os.walk(Path(list(files_map.keys())[0]).parent):
        for file in files:
            if file.endswith('.tex'):
                tex_files.append(os.path.join(root, file))

    env_patterns = {
        'figures_total': r'\\begin\{figure\}',
        'tables_total': r'\\begin\{table\}',
        'algorithms_total': r'\\begin\{algorithm\}',
        'equations_total': r'\\begin\{equation\}',
    }
    env_counts = {k: 0 for k in env_patterns}
    citation_keys = set()
    cite_pat = re.compile(r'\\cite[a-zA-Z]*\{([^}]+)\}')

    for tex_path in tex_files:
        try:
            with open(tex_path, 'r', encoding='utf-8') as f:
                content = f.read()
            for k, pat in env_patterns.items():
                env_counts[k] += len(re.findall(pat, content))
            for match in cite_pat.findall(content):
                for key in match.split(','):
                    citation_keys.add(key.strip())
        except Exception:
            pass

    citations_used_unique = len(citation_keys)
    bib_total = 0
    citation_coverage = 0.0
    if bib_path and Path(bib_path).exists():
        try:
            import bibtexparser
            with open(bib_path, 'r', encoding='utf-8') as bibfile:
                bib_db = bibtexparser.load(bibfile)
            bib_total = len(bib_db.entries)
            if bib_total > 0:
                citation_coverage = citations_used_unique / bib_total
        except Exception:
            pass
    metrics = {
        'words_total': words_total,
        **env_counts,
        'citations_used_unique': citations_used_unique,
        'bib_total': bib_total,
        'citation_coverage': round(citation_coverage, 4),
    }
    return metrics

def log_daily_metrics(metrics, config, log_dir=None, date_override=None):
    """
    Log daily metrics to a JSONL file in .latex-progress/progress.jsonl.
    """
    if log_dir is None:
        log_dir = Path('.latex-progress')
    else:
        log_dir = Path(log_dir)
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / 'progress.jsonl'
    entry_date = date_override if date_override else datetime.date.today().isoformat()
    entry = {
        'date': entry_date,
        **metrics,
        'daily_goal': config.get('target_daily', 0),
        'weekly_goal': config.get('target_weekly', 0),
        'project_goal_total': config.get('target_total', 0),
    }
    # Compute words_delta (difference from previous day)
    words_delta = entry['words_total']
    if log_path.exists():
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if lines:
                last = json.loads(lines[-1])
                words_delta = entry['words_total'] - last.get('words_total', 0)
        except Exception:
            pass
    entry['words_delta'] = words_delta
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')
    return entry