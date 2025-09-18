import click
import hydra
from omegaconf import OmegaConf, DictConfig
import os
import json
from latex_progress.utils import extract_project_plaintext, count_words, parse_latex_metrics, log_daily_metrics

CONFIG_FILE = ".latex-progress.json"

def get_config_path():
    return os.path.join(os.getcwd(), CONFIG_FILE)

def save_config(cfg):
    with open(get_config_path(), "w") as f:
        json.dump(OmegaConf.to_container(cfg, resolve=True), f, indent=2)

def load_config():
    path = get_config_path()
    if os.path.exists(path):
        with open(path) as f:
            return OmegaConf.create(json.load(f))
    return None

@click.group()
def cli():
    """LaTeX Writing Progress Tracker CLI"""
    pass

@cli.command()
@click.option('--target-total', type=int, required=True, help='Total word goal')
@click.option('--target-daily', type=int, required=True, help='Daily word goal')
@click.option('--target-weekly', type=int, required=True, help='Weekly word goal')
@click.option('--bib', type=click.Path(), required=True, help='Path to .bib file')
@click.option('--calendar', type=str, default=None, help='Calendar integration (e.g., google)')
def init(target_total, target_daily, target_weekly, bib, calendar):
    """Initialize project config."""
    cfg = OmegaConf.create({
        "target_total": target_total,
        "target_daily": target_daily,
        "target_weekly": target_weekly,
        "bib": bib,
        "calendar": calendar,
    })
    save_config(cfg)
    click.echo(f"Initialized config and saved to {CONFIG_FILE}")


@cli.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=True))
def track(paths):
    """Track progress for given .tex files, a directory, or current directory."""
    cfg = load_config()
    if not cfg:
        click.echo("Config not found. Please run 'latex-progress init' first.")
        return
    # If a directory is given, use it as root. If .tex files are given, use their directory. If nothing, use cwd.
    root_dir = None
    if paths:
        # If any path is a directory, use it as root
        for p in paths:
            if os.path.isdir(p):
                root_dir = os.path.abspath(p)
                break
        if not root_dir:
            # Use the directory of the first file
            root_dir = os.path.dirname(os.path.abspath(paths[0]))
    else:
        root_dir = os.getcwd()
    result = extract_project_plaintext(root_dir)
    files = result["files"]
    # Get bib path from config if available
    bib_path = cfg.get('bib', None)
    metrics = parse_latex_metrics(files, bib_path=bib_path)
    entry = log_daily_metrics(metrics, cfg)
    click.echo(f"Date: {entry['date']}")
    click.echo(f"Total words in project: {entry['words_total']} (+{entry['words_delta']} today)")
    click.echo(f"Figures: {entry['figures_total']}, Tables: {entry['tables_total']}, Algorithms: {entry['algorithms_total']}, Equations: {entry['equations_total']}")
    click.echo(f"Unique citations used: {entry['citations_used_unique']} / {entry['bib_total']} (Coverage: {entry['citation_coverage']*100:.1f}%)")
    click.echo(f"Daily goal: {entry['daily_goal']}, Weekly goal: {entry['weekly_goal']}, Project goal: {entry['project_goal_total']}")


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
        webbrowser.open(url)
    app.run(debug=True, port=port)

if __name__ == '__main__':
    cli()
