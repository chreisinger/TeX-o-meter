
## Google Calendar integration

If you enable calendar integration, TeX-o-meter will add events to your Google Calendar. By default, events go to your primary calendar.

### Using a different calendar (optional)

If you want to use a different calendar (e.g., a shared or project-specific calendar), you can specify a `calendar_id` in your `.latex-progress.json` config file.

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
# TeX-o-meter
Latex writing progress tool with calendar integration


# latex-progress

TeX-o-meter is a command line tool to track your LaTeX writing progress, visualize your work, and optionally sync your progress to Google Calendar.

## How it works

1. **Initialize your project** with your writing goals and bibliography file using `latex-progress init`.
2. **Track your progress** by running `latex-progress track` on your LaTeX files or project directory. The tool will count words, figures, tables, algorithms, equations, and citations, and log your daily progress.
3. **Visualize your progress** with a live dashboard using `latex-progress dash`.
4. **(Optional) Sync to Google Calendar**: If you enable calendar integration, your daily and weekly progress will be added as events to your Google Calendar.

## Features

- Tracks word count, figures, tables, algorithms, equations, and citation coverage from your LaTeX source.
- Logs daily progress to a local file for historical tracking.
- Visualizes your progress and goals in a web dashboard.
- Integrates with Google Calendar to log daily and weekly writing progress (requires setup, see below).
- Simulate writing progress for testing and demo purposes.

A typical workflow:

## Google calendar setup
```
https://developers.google.com/workspace/calendar/api/quickstart/python
```

## Usage

```bash
latex-progress init --target-total 50000 --target-daily 500 --target-weekly 3500 --bib references.bib --calendar google
latex-progress track main.tex
latex-progress dash --port 8050 --open
```

## Development

- CLI: [Click](https://click.palletsprojects.com/)
- Install: `pip install -e .`
