import dash
from dash import dcc, html, Input, Output, State, clientside_callback
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import date
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import load_figure_template
import base64, io

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

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.FONT_AWESOME,
        "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@latest/dbc.min.css",
        "/assets/custom.css",  # Tron grid + neon efektleri
    ],
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)
server = app.server
load_figure_template(["bootstrap", "bootstrap_dark"])

# Dummy veri
df_global = pd.read_csv("data/mikro_dummy_data.csv")
df_global["Tarih"] = pd.to_datetime(df_global["Tarih"], errors="coerce", infer_datetime_format=True)
df_global["Satış"] = pd.to_numeric(df_global["Satış"], errors="coerce")
df_global["Tahsilat"] = pd.to_numeric(df_global["Tahsilat"], errors="coerce")
df_global["Gider"] = pd.to_numeric(df_global["Gider"], errors="coerce")

app.layout = main_layout(df_global)

# Tema switch - tüm sayfayı dark/light yap (clientside)
clientside_callback(
    """
    function(switchValue) {
        const theme = switchValue ? 'light' : 'dark';
        document.documentElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem('dashTheme', theme);
        return window.dash_clientside.no_update;
    }
    """,
    Output("color-mode-switch", "id"),  # dummy
    Input("color-mode-switch", "value"),
    prevent_initial_call=False
)

# Sayfa yüklendiğinde kaydedilmiş temayı uygula
clientside_callback(
    """
    function(n) {
        const savedTheme = localStorage.getItem('dashTheme') || 'light';
        document.documentElement.setAttribute('data-bs-theme', savedTheme);
        return savedTheme === 'light';
    }
    """,
    Output("color-mode-switch", "value"),
    Input("theme-wrapper", "id"),  # dummy tetikleyici
    prevent_initial_call=False
)

# Dosya yükleme
@app.callback(
    Output("uploaded-data", "data"),
    Output("upload-status", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    prevent_initial_call=True
)
def parse_upload(contents, filename):
    if contents is None:
        raise PreventUpdate
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return None, "❌ Sadece CSV veya Excel dosyası yükleyebilirsiniz!"
        if "Tarih" not in df.columns:
            return None, "❌ Dosyada 'Tarih' sütunu eksik!"
        df["Tarih"] = pd.to_datetime(df["Tarih"], errors="coerce", infer_datetime_format=True)
        df = df.dropna(subset=["Tarih"])
        df["Satış"] = pd.to_numeric(df["Satış"], errors="coerce")
        df["Tahsilat"] = pd.to_numeric(df["Tahsilat"], errors="coerce")
        df["Gider"] = pd.to_numeric(df["Gider"], errors="coerce")
        return df.to_json(date_format="iso", orient="split"), f"✅ {filename} yüklendi"
    except Exception as e:
        return None, f"❌ Hata: {str(e)}"

# Dashboard callback (tüm grafiklerin arka planı şeffaf yapıldı)
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
        Input("color-mode-switch", "value"),
        Input("uploaded-data", "data")
    ],
    prevent_initial_call=False
)
def update_dashboard(start_date, end_date, selected_segments, selected_customers,
                     threshold_percent, is_light, uploaded_json):
    df = pd.read_json(uploaded_json, orient="split") if uploaded_json else df_global.copy()
    if df.empty or "Tarih" not in df.columns:
        raise PreventUpdate
    df["Tarih"] = pd.to_datetime(df["Tarih"], errors="coerce", infer_datetime_format=True)
    df = df.dropna(subset=["Tarih"])
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    mask = (df["Tarih"] >= start_date) & (df["Tarih"] <= end_date)
    if selected_segments:
        mask &= df["Segment"].isin(selected_segments)
    if selected_customers:
        mask &= df["Müşteri"].isin(selected_customers)
    df_filtered = df[mask]
    template = "bootstrap" if is_light else "bootstrap_dark"

    fig1 = sales_year_comparison_chart(df_filtered)
    fig1.update_layout(
        template=template,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    fig2 = top_stock_chart(df_filtered)
    fig2.update_layout(
        template=template,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    fig3 = cash_vs_expense_pie(df_filtered)
    fig3.update_layout(
        template=template,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    fig4 = segment_scatter(df_filtered)
    fig4.update_layout(
        template=template,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    fig5 = profit_scatter(df_filtered, threshold=threshold_percent / 100 if threshold_percent else 0.10)
    fig5.update_layout(
        template=template,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    return fig1, fig2, fig3, fig4, fig5, generate_kpi_cards(df_filtered)

# Satış trend callback (burada da şeffaflık eklendi)
@app.callback(
    Output("sales-trend", "figure"),
    [Input("sales-trend-range", "value"),
     Input("color-mode-switch", "value"),
     Input("uploaded-data", "data")],
    prevent_initial_call=False
)
def update_sales_trend(selected_range, is_light, uploaded_json):
    df = pd.read_json(uploaded_json, orient="split") if uploaded_json else df_global.copy()
    if df.empty or "Tarih" not in df.columns:
        raise PreventUpdate
    df["Tarih"] = pd.to_datetime(df["Tarih"], errors="coerce", infer_datetime_format=True)
    df = df.dropna(subset=["Tarih"])
    today = pd.Timestamp.today()
    if selected_range == "1M":
        start_date = today - pd.DateOffset(months=1)
    elif selected_range == "3M":
        start_date = today - pd.DateOffset(months=3)
    elif selected_range == "6M":
        start_date = today - pd.DateOffset(months=6)
    else:
        start_date = today - pd.DateOffset(years=1)
    start_date = pd.to_datetime(start_date)
    df_filtered = df[df["Tarih"] >= start_date]

    fig = sales_trend_chart(df_filtered)
    fig.update_layout(
        template="bootstrap" if is_light else "bootstrap_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
        # font_color="var(--bs-body-color)"  # istersen aç, ama genelde otomatik oluyor
    )

    return fig

# Tarih butonları
@app.callback(
    [Output("start-date", "date"), Output("end-date", "date")],
    [Input("today-button", "n_clicks"),
     Input("last-date-button", "n_clicks"),
     Input("reset-date-button", "n_clicks")],
    [State("start-date", "date"), State("end-date", "date"),
     State("uploaded-data", "data")],
    prevent_initial_call=True
)
def manage_dates(today_clicks, last_clicks, reset_clicks, start_state, end_state, uploaded_json):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    trigger = ctx.triggered[0]["prop_id"].split(".")[0]
    df = pd.read_json(uploaded_json, orient="split") if uploaded_json else df_global.copy()
    if df.empty or "Tarih" not in df.columns:
        raise PreventUpdate
    df["Tarih"] = pd.to_datetime(df["Tarih"], errors="coerce", infer_datetime_format=True)
    df = df.dropna(subset=["Tarih"])
    min_date = df["Tarih"].min().date()
    max_date = df["Tarih"].max().date()
    if trigger == "reset-date-button":
        return min_date, max_date
    if trigger == "today-button":
        return start_state or min_date, date.today()
    if trigger == "last-date-button":
        return start_state or min_date, max_date
    raise PreventUpdate

# Filtre sıfırlama
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