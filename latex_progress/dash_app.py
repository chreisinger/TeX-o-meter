import json
from pathlib import Path
import dash
from dash import dcc, html
import plotly.graph_objs as go
import pandas as pd

def load_progress(log_path):
    if not Path(log_path).exists():
        return pd.DataFrame()
    with open(log_path, 'r', encoding='utf-8') as f:
        lines = [json.loads(line) for line in f if line.strip()]
    if not lines:
        return pd.DataFrame()
    return pd.DataFrame(lines)

def create_dash_app(log_path):
    df = load_progress(log_path)
    app = dash.Dash(__name__, suppress_callback_exceptions=True)

    def serve_layout():
        df = load_progress(log_path)
        if df.empty:
            return html.Div([html.H2("No progress data found.")])

        # Words over time
        words_fig = go.Figure()
        words_fig.add_trace(go.Bar(x=df['date'], y=df['words_delta'], name='Words per day'))
        words_fig.add_trace(go.Scatter(x=df['date'], y=df['words_total'], name='Cumulative words', mode='lines+markers'))
        if 'project_goal_total' in df:
            words_fig.add_trace(go.Scatter(x=df['date'], y=[df['project_goal_total'].iloc[0]]*len(df), name='Total goal', mode='lines', line=dict(dash='dash')))
        if 'daily_goal' in df:
            words_fig.add_trace(go.Scatter(x=df['date'], y=[df['daily_goal'].iloc[0]]*len(df), name='Daily goal', mode='lines', line=dict(dash='dot')))
        words_fig.update_layout(title='Words Progress', xaxis_title='Date', yaxis_title='Words')

        # Artifacts chart
        artifacts_fig = go.Figure()
        for col, label in [('figures_total','Figures'),('tables_total','Tables'),('algorithms_total','Algorithms'),('equations_total','Equations')]:
            if col in df:
                artifacts_fig.add_trace(go.Scatter(x=df['date'], y=df[col], name=label, mode='lines+markers'))
        artifacts_fig.update_layout(title='Artifacts Over Time', xaxis_title='Date', yaxis_title='Count')

        # Bibliography chart
        bib_fig = go.Figure()
        if 'bib_total' in df and 'citations_used_unique' in df:
            bib_fig.add_trace(go.Scatter(x=df['date'], y=df['bib_total'], name='Total Bib Entries', mode='lines+markers'))
            bib_fig.add_trace(go.Scatter(x=df['date'], y=df['citations_used_unique'], name='Unique Citations Used', mode='lines+markers'))
        if 'citation_coverage' in df:
            bib_fig.add_trace(go.Scatter(x=df['date'], y=df['citation_coverage']*100, name='Citation Coverage (%)', mode='lines+markers', yaxis='y2'))
        bib_fig.update_layout(title='Bibliography Progress', xaxis_title='Date', yaxis_title='Count', yaxis2=dict(overlaying='y', side='right', title='Coverage (%)'))

        return html.Div([
            html.H1("LaTeX Progress Dashboard"),
            dcc.Graph(figure=words_fig),
            dcc.Graph(figure=artifacts_fig),
            dcc.Graph(figure=bib_fig),
            html.Button("Refresh", id="refresh-btn"),
            dcc.Interval(id='interval', interval=30*1000, n_intervals=0),
            html.Div(id="dummy", style={"display": "none"}),
        ])

    app.layout = serve_layout

    @app.callback(
        dash.dependencies.Output('interval', 'n_intervals'),
        [dash.dependencies.Input('refresh-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def refresh(n):
        return 0

    @app.callback(
        dash.dependencies.Output('dummy', 'children'),
        [dash.dependencies.Input('interval', 'n_intervals')]
    )
    def auto_refresh(n):
        # This triggers layout refresh
        return None

    return app