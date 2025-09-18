# TeX-o-meter

TeX-o-meter is a command line tool to track your LaTeX writing progress, visualize your work, and optionally sync your progress to Google Calendar.

## How it works

1. **Initialize your project** with your writing goals and bibliography file using `latex-progress init`.
2. **Track your progress** by running `latex-progress track` on your LaTeX files or project directory. The tool will count words, figures, tables, algorithms, equations, and citations, and log your daily progress.
3. **Visualize your progress** with a live dashboard using `latex-progress dash`.
4. **(Optional) Sync to Google Calendar**: If you enable calendar integration, your daily and weekly progress will be added as events to your Google Calendar.

## Key Features
- **Tracks**: word count, figures, tables, algorithms, equations, and citation coverage from your LaTeX source (using PlainTeX for robust parsing).
- **Logs**: daily progress to a local file (`.latex-progress/progress.jsonl`) for historical tracking.
- **Visualizes**: your progress and goals in a web dashboard (`latex-progress dash`).
- **Google Calendar integration**: logs daily writing progress as upserted (overwritten) events in your Google Calendar (no duplicates, always up-to-date).
- **YAML config**: project configuration is stored in `.latex-progress.yaml`.
- **BibTeX abbreviation support**: supports a separate bib abbreviation file (e.g., for short or long conference/journal strings)

## Environment setup

It is recommended to use a Python virtual environment for development and usage.

**Python version:**

- Python 3.7 or newer is required.

1. **Create and activate a virtual environment:**

	```bash
	python3 -m venv .venv
	source .venv/bin/activate
	```

2. **Install required dependencies:**

	```bash
    pip install click hydra-core omegaconf bibtexparser dash plotly pandas
    # Install PlainTeX (latex to plain text converter):
    pip install git+https://github.com/chreisinger/PlainTeX.git
	# Google Calendar integration:
	pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
	pip install -e .
	```
## Google Calendar setup

Follow the [Google Calendar API Python Quickstart](https://developers.google.com/workspace/calendar/api/quickstart/python) to set up your credentials. Place the credentials file as `~/.latex-progress.credentials.json`.

## Google Calendar integration

If you enable calendar integration, TeX-o-meter will add or update events in your Google Calendar for each day you track. By default, events go to your primary calendar.
If you want to use a different calendar (e.g., a shared or project-specific calendar), specify `--calendar-id` during `init` or edit your `.latex-progress.yaml` config file.

- **How to find your calendar ID:**
	1. Go to [Google Calendar](https://calendar.google.com/).
	2. In the left sidebar, find the calendar you want to use and click the three dots next to it.
	3. Click "Settings and sharing".
	4. Scroll down to the "Integrate calendar" section. The "Calendar ID" will be shown there.
- **How to set:**
	- Edit your `.latex-progress.json` and add or change the line:
	  ```json
	  "calendar_id": "your_calendar_id@group.calendar.google.com"
	  ```
- **If not set:**
	- If you do not set `calendar_id`, events will be added to your default (primary) Google Calendar.

## Usage

```bash
# Initialize project (example)
# init the tracker within your writing project folder
latex-progress init --target-total 30000 --target-daily 300 --target-weekly 1500 \
	--latex-path doc/chapters --bib doc/references.bib --bib-abbrev <path_to_abbrev.bib> \
	--calendar <google> --calendar-id <your_calendar_id>

# Track progress (run in your project directory)
latex-progress track

# Visualize progress in a web dashboard
latex-progress dash --port 8050 --open

```