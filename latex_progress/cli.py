import click
from omegaconf import OmegaConf
import os
import json
from latex_progress.utils import extract_project_plaintext, parse_latex_metrics, log_daily_metrics
from datetime import timedelta

CONFIG_FILE = ".latex-progress.yaml"

def get_config_path():
    return os.path.join(os.getcwd(), CONFIG_FILE)

def save_config(cfg):
    OmegaConf.save(cfg, get_config_path())

def load_config():
    path = get_config_path()
    if os.path.exists(path):
        return OmegaConf.load(path)
    return None

@click.group()
def cli():
    """LaTeX Writing Progress Tracker CLI"""
    pass

@cli.command()
@click.option('--target-total', type=int, required=True, help='Total word goal')
@click.option('--target-daily', type=int, required=True, help='Daily word goal')
@click.option('--target-weekly', type=int, required=True, help='Weekly word goal')
@click.option('--latex-path', type=click.Path(exists=True), required=True, help='Path to LaTeX file or directory')
@click.option('--bib', type=click.Path(), required=True, help='Path to .bib file')
@click.option('--calendar', type=str, default=None, help='Calendar integration (e.g., google)')
@click.option('--calendar-id', type=str, default='primary', help='Calendar ID (if using calendar integration)')
def init(target_total, target_daily, target_weekly, latex_path, bib, calendar, calendar_id):
    """Initialize project config."""
    resolved_latex_path = os.path.abspath(os.path.expanduser(latex_path))
    cfg = OmegaConf.create({
        "target_total": target_total,
        "target_daily": target_daily,
        "target_weekly": target_weekly,
        "latex_path": resolved_latex_path,
        "bib": bib,
        "calendar": calendar,
        "calendar_id": calendar_id
    })
    save_config(cfg)
    click.echo(f"Initialized config and saved to {CONFIG_FILE}")


@cli.command()
@click.option('--date', type=str, default=None, help='Override date for tracking (YYYY-MM-DD)')
def track(date):
    """Track progress for given .tex files, a directory, or current directory."""
    cfg = load_config()
    if not cfg:
        click.echo("Config not found. Please run 'latex-progress init' first.")
        return
    # Always use the latex_path from config
    latex_path = cfg.get('latex_path', None)
    if latex_path is None:
        click.echo("No LaTeX file or directory specified in config. Please re-run 'latex-progress init'.")
        return
    result = extract_project_plaintext(latex_path)
    files = result["files"]
    # Get bib path from config if available
    bib_path = cfg.get('bib', None)
    metrics = parse_latex_metrics(files, bib_path=bib_path)
    entry = log_daily_metrics(metrics, cfg, date_override=date)
    click.echo(f"Date: {entry['date']}")
    click.echo(f"Total words in project: {entry['words_total']} (+{entry['words_delta']} today)")
    click.echo(f"Figures: {entry['figures_total']}, Tables: {entry['tables_total']}, Algorithms: {entry['algorithms_total']}, Equations: {entry['equations_total']}")
    click.echo(f"Unique citations used: {entry['citations_used_unique']} / {entry['bib_total']} (Coverage: {entry['citation_coverage']*100:.1f}%)")
    click.echo(f"Daily goal: {entry['daily_goal']}, Weekly goal: {entry['weekly_goal']}, Project goal: {entry['project_goal_total']}")

    calendar_val = str(cfg.get('calendar', '') or '').lower()
    if calendar_val == 'google':
        try:
            from latex_progress.calendar import create_event
            percent_daily = 0
            if entry['daily_goal']:
                percent_daily = int(100 * entry['words_delta'] / entry['daily_goal'])
            percent_total = 0
            if entry['project_goal_total']:
                percent_total = int(100 * entry['words_total'] / entry['project_goal_total'])
            percent_citations = 0
            if entry['bib_total']:
                percent_citations = int(100 * entry['citations_used_unique'] / entry['bib_total'])
            n = entry['words_delta']
            m = entry['daily_goal']
            x = int(100 * n / m) if m else 0
            summary = f"Words: {n}/{m} ({x}%)"
            from datetime import datetime as dt
            tracked_date = entry['date']
            try:
                tracked_dt = dt.fromisoformat(tracked_date)
            except Exception:
                tracked_dt = None
            # Weekly progress calculation
            week_sum = 0
            week_goal = entry.get('weekly_goal', 0)
            week_pct = 0
            if tracked_dt:
                monday = tracked_dt - timedelta(days=tracked_dt.weekday())
                log_path = os.path.join('.latex-progress', 'progress.jsonl')
                try:
                    with open(log_path) as f:
                        for line in f:
                            rec = json.loads(line)
                            rec_date = dt.fromisoformat(rec['date'])
                            if monday <= rec_date <= tracked_dt:
                                week_sum += rec.get('words_delta', 0)
                except Exception:
                    pass
                week_pct = int(100 * week_sum / week_goal) if week_goal else 0
            # Overall progress
            total_words = entry.get('words_total', 0)
            total_goal = entry.get('project_goal_total', 0)
            total_pct = int(100 * total_words / total_goal) if total_goal else 0
            description = (
                f"Weekly: {week_sum}/{week_goal} ({week_pct}%)\n"
                f"Overall: {total_words}/{total_goal} ({total_pct}%)\n"
                f"Figures: {entry['figures_total']}, Tables: {entry['tables_total']}, Algorithms: {entry['algorithms_total']}, Equations: {entry['equations_total']}\n"
                f"Citation coverage: {entry['citation_coverage']*100:.1f}%"
            )
            calendar_id = cfg.get('calendar_id', 'primary')
            create_event(summary, description, entry['date'], calendar_id=calendar_id)
            click.echo("Google Calendar event created.")
        except Exception as e:
            click.echo(f"[Calendar] Failed to create event: {e}")


@cli.command()
@click.option('--port', type=int, default=8050, help='Port for Dash app')
@click.option('--open', 'open_browser', is_flag=True, help='Open in browser')
def dash(port, open_browser):
    """Launch Dash dashboard."""
    from latex_progress.dash_app import create_dash_app
    import webbrowser
    log_path = os.path.join('.latex-progress', 'progress.jsonl')
    app = create_dash_app(log_path)
    url = f"http://127.0.0.1:{port}"
    if open_browser:
        import time
        import threading
        def open_browser_delayed():
            time.sleep(1)
            webbrowser.open(url)
        threading.Thread(target=open_browser_delayed, daemon=True).start()
    app.run(debug=False, port=port, use_reloader=False)

if __name__ == '__main__':
    cli()
