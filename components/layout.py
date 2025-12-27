from dash import html, dcc
import dash_bootstrap_components as dbc
from components.kpi_cards import generate_kpi_cards
from components.filters import generate_filters
from components.charts import (
    sales_trend_chart,
    top_stock_chart,
    cash_vs_expense_pie,
    segment_scatter,
    profit_scatter,
    sales_year_comparison_chart
)

def main_layout(df):
    min_date = df["Tarih"].min().date()
    max_date = df["Tarih"].max().date()
    segment_dropdown, customer_dropdown = generate_filters(df)

    return html.Div(
        id="theme-wrapper",
        className="bg-light",
        children=dbc.Container([
            # Dosya yükleme + Store
            dbc.Card([
                dbc.CardBody([
                    html.H5("Kendi Verinizi Yükleyin", className="text-center mb-3"),
                    dcc.Upload(
                        id="upload-data",
                        children=html.Div([
                            "CSV veya Excel dosyanızı sürükleyin veya ",
                            html.A("seçin", href="#", style={"color": "white"})
                        ]),
                        style={
                            "width": "100%", "height": "60px", "lineHeight": "60px",
                            "borderWidth": "1px", "borderStyle": "dashed", "borderRadius": "5px",
                            "textAlign": "center", "margin": "10px"
                        },
                        multiple=False
                    ),
                    html.Div(id="upload-status", className="text-center mt-2"),
                    dcc.Store(id="uploaded-data", storage_type="memory")
                ])
            ], className="mb-4"),

            # Başlık + Tema toggle
            dbc.Row([
                dbc.Col(html.H2("Mikro ERP Dashboard", className="text-center my-3 text-body"), md=10),
                dbc.Col(html.Div([
                    html.I(className="fa fa-moon me-2 text-body", style={"fontSize": "1.3rem"}),
                    dbc.Switch(id="color-mode-switch", value=False, persistence=True),
                    html.I(className="fa fa-sun ms-2 text-body", style={"fontSize": "1.3rem"}),
                ], className="d-flex align-items-center justify-content-end"), md=2)
            ]),

            html.Div(id="kpi-cards", children=generate_kpi_cards(df), className="mb-4"),
            html.Hr(className="border-secondary"),

            # Satış trendi + tarih filtreleri
            dbc.Row([
                dbc.Col([
                    html.H4("📊 Günlük Satış Trendleri", className="text-center mb-3 text-body"),
                    dcc.RadioItems(
                        id="sales-trend-range",
                        options=[
                            {"label": " Son 1 Ay", "value": "1M"},
                            {"label": " Son 3 Ay", "value": "3M"},
                            {"label": " Son 6 Ay", "value": "6M"},
                            {"label": " Son 1 Yıl", "value": "12M"},
                        ],
                        value="3M",
                        labelStyle={"display": "inline-block", "margin-right": "15px"},
                        inputStyle={"margin-right": "8px"},
                        style={"textAlign": "center", "marginBottom": "10px"}
                    ),
                    dcc.Graph(id="sales-trend", figure=sales_trend_chart(df),
                              responsive=True,
                              config={'responsive': True, 'displayModeBar': 'hover', 'scrollZoom': False},
                              style={'width': '100%', 'height': '50vh', 'minHeight': '300px'})
                ])
            ]),

            # Tarih filtreleri
            dbc.Card([
                dbc.CardBody([
                    html.H4("📅 Tarihe Göre Filtrele", className="text-center mb-4 text-body"),
                    dbc.Row([
                        dbc.Col(dcc.DatePickerSingle(
                            id="start-date",
                            min_date_allowed=min_date,
                            max_date_allowed=max_date,
                            date=min_date,
                            display_format="DD.MM.YYYY",
                            persistence=True,
                            className="w-100"
                        ), md=3),
                        dbc.Col(dcc.DatePickerSingle(
                            id="end-date",
                            min_date_allowed=min_date,
                            max_date_allowed=max_date,
                            date=max_date,
                            display_format="DD.MM.YYYY",
                            persistence=True,
                            className="w-100"
                        ), md=3),
                        dbc.Col([
                            dbc.Button("📅 Bugün", id="today-button", color="primary", outline=True, size="sm", className="me-1"),
                            dbc.Button("📊 Son İşlem Tarihi", id="last-date-button", color="secondary", outline=True, size="sm", className="me-1"),
                            dbc.Button("📅 Tarih Temizle", id="reset-date-button", color="danger", outline=True, size="sm")
                        ], md=6, className="d-flex align-items-center flex-wrap justify-content-center")
                    ])
                ])
            ], className="mb-4"),

            # Segment ve müşteri filtreleri
            dbc.Row([
                dbc.Col(segment_dropdown, md=4),
                dbc.Col(customer_dropdown, md=4),
                dbc.Col(dbc.Button("🧹 Filtreyi Temizle", id="reset-filters-button",
                                   color="danger", outline=True, size="sm", className="w-100"), md=2)
            ], className="mb-4 justify-content-center"),

            # Grafikler
            dbc.Row([
                dbc.Col(dcc.Graph(id="top-stock", figure=top_stock_chart(df), responsive=True,
                                  config={'responsive': True, 'displayModeBar': 'hover'},
                                  style={'height': '50vh'}), md=6),
                dbc.Col(dcc.Graph(id="cash-expense", figure=cash_vs_expense_pie(df), responsive=True,
                                  config={'responsive': True, 'displayModeBar': 'hover'},
                                  style={'height': '50vh'}), md=6)
            ], className="mb-4"),

            dbc.Row([
                dbc.Col(dcc.Graph(id="segment-scatter", figure=segment_scatter(df), responsive=True,
                                  config={'responsive': True, 'displayModeBar': 'hover'},
                                  style={'height': '50vh'}), md=12)
            ]),

            html.Label("Kâr Marjı Eşiği (%)", className="w-100 text-center text-body mt-4"),
            dcc.Slider(
                id="margin-threshold-slider",
                min=5, max=30, step=1, value=10,
                marks={i: f"%{i}" for i in range(5, 31, 5)},
                tooltip={"placement": "bottom", "always_visible": True},
                className="w-100"
            ),

            dbc.Row([
                dbc.Col(dcc.Graph(id="profit-scatter", figure=profit_scatter(df), responsive=True,
                                  config={'responsive': True, 'displayModeBar': 'hover'},
                                  style={'height': '60vh'}), md=12)
            ]),

            dbc.Row([
                dbc.Col(dcc.Graph(id="sales-year-comparison", figure=sales_year_comparison_chart(df), responsive=True,
                                  config={'responsive': True, 'displayModeBar': 'hover'},
                                  style={'height': '50vh'}), md=12)
            ]),

            # Footer
            html.Div([
                html.Div([
                    html.Img(src="/assets/ln.png", style={"height": "24px", "marginRight": "10px"}),
                    html.Span("Serdal Kağan Çelebi", className="text-muted", style={"fontSize": "0.9rem"})
                ], className="d-flex align-items-center justify-content-center"),
                html.A("GitHub / LinkedIn / Kişisel Site",
                       href="https://linkedin.com/in/serdalkagancelebi",
                       target="_blank",
                       className="text-muted d-block text-center mt-2",
                       style={"fontSize": "0.85rem"})
            ], className="mt-5 mb-4")
        ], fluid=True, className="px-2")
    )
