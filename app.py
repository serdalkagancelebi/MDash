import dash
from dash import dcc, html, Input, Output, State, clientside_callback
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import date
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import load_figure_template

from components.layout import main_layout
from components.charts import (
    sales_trend_chart,
    top_stock_chart,
    cash_vs_expense_pie,
    segment_scatter,
    profit_scatter,
    sales_year_comparison_chart
)
from components.kpi_cards import generate_kpi_cards

# Dash uygulaması
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.FONT_AWESOME,
        "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@latest/dbc.min.css",
        "/assets/custom.css",  # varsa, yoksa bu satırı sil
    ],
    meta_tags=[
        {'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'}
    ],
    suppress_callback_exceptions=True
)

load_figure_template(["bootstrap", "bootstrap_dark"])

# Veri yükleme
df_global = pd.read_csv("data/mikro_dummy_data.csv")
df_global["Tarih"] = pd.to_datetime(df_global["Tarih"], dayfirst=True, errors="coerce")
df_global["Satış"] = pd.to_numeric(df_global["Satış"], errors="coerce")
df_global["Tahsilat"] = pd.to_numeric(df_global["Tahsilat"], errors="coerce")
df_global["Gider"] = pd.to_numeric(df_global["Gider"], errors="coerce")

# Layout
app.layout = main_layout(df_global)

# Toggle callback (light/dark)
clientside_callback(
    """
    function(switchValue) {
        const wrapper = document.getElementById('theme-wrapper');
        if (wrapper) {
            if (switchValue) {
                document.documentElement.setAttribute('data-bs-theme', 'light');
                wrapper.classList.remove('bg-dark');
                wrapper.classList.add('bg-light');
                document.body.style.backgroundColor = '#f8f9fa';  // açık gri
            } else {
                document.documentElement.setAttribute('data-bs-theme', 'dark');
                wrapper.classList.remove('bg-light');
                wrapper.classList.add('bg-dark');
                document.body.style.backgroundColor = '#212529';  // koyu siyah
            }
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output("dummy-output-for-toggle", "children"),
    Input("color-mode-switch", "value")
)

# Ana callback (grafikler)
@app.callback(
    [
        Output("sales-year-comparison", "figure"),
        Output("top-stock", "figure"),
        Output("cash-expense", "figure"),
        Output("segment-scatter", "figure"),
        Output("profit-scatter", "figure"),
        Output("kpi-cards", "children"),
    ],
    [
        Input("start-date", "date"),
        Input("end-date", "date"),
        Input("segment-filter", "value"),
        Input("customer-filter", "value"),
        Input("margin-threshold-slider", "value"),
        Input("color-mode-switch", "value")
    ],
    prevent_initial_call=False
)
def update_dashboard(start_date, end_date, selected_segments, selected_customers, threshold_percent, is_light):
    df = df_global.copy()

    if not start_date or not end_date:
        start_date = df["Tarih"].min().date()
        end_date = df["Tarih"].max().date()

    mask = (
        (df["Tarih"] >= pd.to_datetime(start_date)) &
        (df["Tarih"] <= pd.to_datetime(end_date))
    )
    if selected_segments:
        mask &= df["Segment"].isin(selected_segments)
    if selected_customers:
        mask &= df["Müşteri"].isin(selected_customers)

    df_filtered = df[mask]

    template = "bootstrap" if is_light else "bootstrap_dark"

    year_comparison_fig = sales_year_comparison_chart(df_filtered)
    year_comparison_fig.update_layout(template=template)

    fig_top_stock = top_stock_chart(df_filtered)
    fig_top_stock.update_layout(template=template)

    fig_cash_expense = cash_vs_expense_pie(df_filtered)
    fig_cash_expense.update_layout(template=template)

    fig_segment = segment_scatter(df_filtered)
    fig_segment.update_layout(template=template)

    fig_profit = profit_scatter(df_filtered, threshold=threshold_percent / 100 if threshold_percent else 0.10)
    fig_profit.update_layout(template=template)

    kpi_cards = generate_kpi_cards(df_filtered)

    return (
        year_comparison_fig,
        fig_top_stock,
        fig_cash_expense,
        fig_segment,
        fig_profit,
        kpi_cards
    )

# Satış trend callback
@app.callback(
    Output("sales-trend", "figure"),
    [Input("sales-trend-range", "value"),
     Input("color-mode-switch", "value")],
    prevent_initial_call=False
)
def update_sales_trend(selected_range, is_light):
    df = df_global.copy()
    today = pd.Timestamp.today()

    if selected_range == "1M":
        start_date = today - pd.DateOffset(months=1)
    elif selected_range == "3M":
        start_date = today - pd.DateOffset(months=3)
    elif selected_range == "6M":
        start_date = today - pd.DateOffset(months=6)
    else:
        start_date = today - pd.DateOffset(years=1)

    df_filtered = df[df["Tarih"] >= start_date]
    fig = sales_trend_chart(df_filtered)
    template = "bootstrap" if is_light else "bootstrap_dark"
    fig.update_layout(template=template)
    return fig

# Diğer callback'ler (tarih butonları, filtre sıfırlama) - kısaltılmış hali
@app.callback(
    [Output("start-date", "date"), Output("end-date", "date")],
    [Input("today-button", "n_clicks"), Input("last-date-button", "n_clicks"), Input("reset-date-button", "n_clicks")],
    [State("start-date", "date"), State("end-date", "date")],
    prevent_initial_call=True
)
def manage_dates(today_clicks, last_clicks, reset_clicks, start_state, end_state):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    trigger = ctx.triggered[0]["prop_id"].split(".")[0]
    min_date = df_global["Tarih"].min().date()
    max_date = df_global["Tarih"].max().date()

    if trigger == "reset-date-button":
        return min_date, max_date
    if trigger == "today-button":
        today_d = date.today()
        return start_state or min_date, today_d
    if trigger == "last-date-button":
        return start_state or min_date, max_date
    raise PreventUpdate

@app.callback(
    [Output("segment-filter", "value"), Output("customer-filter", "value")],
    Input("reset-filters-button", "n_clicks"),
    prevent_initial_call=True
)
def reset_filters(n_clicks):
    if n_clicks:
        return None, None
    raise PreventUpdate

if __name__ == "__main__":
    print("Sunucu başlatılıyor...")

    app.run(debug=True, host="127.0.0.1", port=8050)

server = app.server
