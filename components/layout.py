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

    # Toggle switch (moon = dark, sun = light)
    color_mode_switch = html.Div(
        [
            html.I(className="fa fa-moon me-2 text-body", style={"fontSize": "1.3rem"}),
            dbc.Switch(
                id="color-mode-switch",
                value=False,  # False = karanlık başlasın
                className="d-inline-block align-middle",
                persistence=True,
            ),
            html.I(className="fa fa-sun ms-2 text-body", style={"fontSize": "1.3rem"}),
        ],
        className="d-flex align-items-center justify-content-end mt-3 mb-3 px-3"
    )

    # Dosya yükleme bölümü
    upload_section = dbc.Card([
        dbc.CardBody([
            html.H5("Kendi Verinizi Yükleyin", className="text-center mb-3"),
            dcc.Upload(
                id="upload-data",
                children=html.Div([
                    "CSV veya Excel dosyanızı sürükleyin veya ",
                    html.A("seçin", href="#", style={"color": "white"})
                ]),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "margin": "10px"
                },
                multiple=False
            ),
            html.Div(id="upload-status", className="text-center mt-2")
        ])
    ], className="mb-4")

    # Tüm dashboard'ı saran wrapper
    return html.Div(
        id="theme-wrapper",
        className="bg-light",
        children=dbc.Container([
            # Dosya yükleme bölümü en üstte
            upload_section,

            # Toggle + Başlık
            dbc.Row([
                dbc.Col(
                    html.H2("Mikro ERP Dashboard", className="text-center my-3 text-body"),
                    md=10
                ),
                dbc.Col(color_mode_switch, md=2, className="d-flex align-items-center justify-content-end"),
            ], className="align-items-center mb-2"),

            html.Div(id="kpi-cards", children=generate_kpi_cards(df), className="mb-4"),

            html.Hr(className="border-secondary"),
            
            # Filtreler ve Grafikler
            dbc.Row([
                dbc.Col([
                    html.Div([
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
                            labelStyle={
                                "display": "inline-block",
                                "margin-right": "15px",
                                "color": "inherit",
                                "fontWeight": "500"
                            },
                            inputStyle={"margin-right": "8px"},
                            style={
                                "margin-bottom": "10px",
                                "textAlign": "center",
                                "color": "inherit"
                            },
                            className="radio-items-label"
                        ),

                        dcc.Graph(
                            id="sales-trend",
                            figure=sales_trend_chart(df),
                            responsive=True,
                            config={'responsive': True, 'displayModeBar': 'hover', 'scrollZoom': False},
                            style={'width': '100%', 'height': '50vh', 'minHeight': '300px'}
                        ),

                        dbc.Row(className="mt-4"),  # sadece boş row

                        dbc.Card([
                            dbc.CardBody([
                                html.H4("📅 Tarihe Göre Filtrele", className="text-center mb-4 text-body"),

                                dbc.Row([
                                    dbc.Col([
                                        dbc.Row([
                                            dbc.Col(
                                                html.Label("🗓️ İlk Tarih", className="form-label me-2 text-body"),
                                                width="auto", className="d-flex align-items-center"
                                            ),
                                            dbc.Col(
                                                html.Div(
                                                    dcc.DatePickerSingle(
                                                        id="start-date",
                                                        min_date_allowed=min_date,
                                                        max_date_allowed=max_date,
                                                        date=min_date,
                                                        display_format="DD.MM.YYYY",
                                                        persistence=True,
                                                        className="w-100"
                                                    ),
                                                    className="dbc"
                                                ),
                                                width="auto"
                                            )
                                        ], className="g-1")
                                    ], md="auto", className="d-flex align-items-center"),

                                    dbc.Col([
                                        dbc.Row([
                                            dbc.Col(
                                                html.Label("🗓️ Son Tarih", className="form-label me-2 text-body"),
                                                width="auto", className="d-flex align-items-center"
                                            ),
                                            dbc.Col(
                                                html.Div(
                                                    dcc.DatePickerSingle(
                                                        id="end-date",
                                                        min_date_allowed=min_date,
                                                        max_date_allowed=max_date,
                                                        date=max_date,
                                                        display_format="DD.MM.YYYY",
                                                        persistence=True,
                                                        className="w-100"
                                                    ),
                                                    className="dbc"
                                                ),
                                                width="auto"
                                            ),
                                            dbc.Col([
                                                dbc.Button("📅 Bugün", id="today-button",
                                                           color="primary", outline=True, size="sm",
                                                           className="me-1"),
                                                dbc.Button("📊 Son İşlem Tarihi", id="last-date-button",
                                                           color="secondary", outline=True, size="sm",
                                                           className="me-1"),
                                                dbc.Button("📅 Tarih Temizle", id="reset-date-button",
                                                           color="danger", outline=True, size="sm")
                                            ], width="auto", className="d-flex align-items-center flex-wrap")
                                        ], className="g-1")
                                    ], md="auto", className="d-flex align-items-center")
                                ], className="mb-3 justify-content-center flex-wrap"),

                                dbc.Row([
                                    dbc.Col(
                                        html.Div(segment_dropdown, className="dbc"),
                                        md=4, className="mb-2"
                                    ),
                                    dbc.Col(
                                        html.Div(customer_dropdown, className="dbc"),
                                        md=4, className="mb-2"
                                    ),
                                    dbc.Col(
                                        dbc.Button(
                                            "🧹 Filtreyi Temizle",
                                            id="reset-filters-button",
                                            color="danger",
                                            outline=True,
                                            size="sm",
                                            className="w-100"
                                        ),
                                        md=2
                                    )
                                ], className="mb-3 justify-content-center"),
                            ])
                        ], className="mb-4 border-secondary")
                    ])
                ], md=12),
            ]),

            dbc.Row([
                dbc.Col(dcc.Graph(id="top-stock", figure=top_stock_chart(df), responsive=True,
                                  config={'responsive': True, 'displayModeBar': 'hover', 'scrollZoom': False},
                                  style={'width': '100%', 'height': '50vh', 'minHeight': '300px'}), md=6),
                dbc.Col(dcc.Graph(id="cash-expense", figure=cash_vs_expense_pie(df), responsive=True,
                                  config={'responsive': True, 'displayModeBar': 'hover', 'scrollZoom': False},
                                  style={'width': '100%', 'height': '50vh', 'minHeight': '300px'}), md=6),
            ], className="mb-4"),

            dbc.Row([
                dbc.Col(dcc.Graph(id="segment-scatter", figure=segment_scatter(df), responsive=True,
                                  config={'responsive': True, 'displayModeBar': 'hover', 'scrollZoom': False},
                                  style={'width': '100%', 'height': '50vh', 'minHeight': '300px'}), md=12),
            ]),

            html.Label("Kâr Marjı Eşiği (%)", className="w-100 text-center text-body mt-4"),
            html.Div(
                dcc.Slider(
                    id="margin-threshold-slider",
                    min=5,
                    max=30,
                    step=1,
                    value=10,
                    marks={i: f"%{i}" for i in range(5, 31, 5)},
                    tooltip={"placement": "bottom", "always_visible": True},
                    className="w-100"
                ),
                className="dbc mb-4"
            ),

            dbc.Row([
                dbc.Col(dcc.Graph(id="profit-scatter", figure=profit_scatter(df), responsive=True,
                                  config={'responsive': True, 'displayModeBar': 'hover', 'scrollZoom': False},
                                  style={'width': '100%', 'height': '60vh', 'minHeight': '400px'}), md=12),
            ]),

            dbc.Row(className="mt-4"),  # sadece boş row

            dbc.Row([
                dbc.Col(dcc.Graph(id="sales-year-comparison", figure=sales_year_comparison_chart(df), responsive=True,
                                  config={'responsive': True, 'displayModeBar': 'hover', 'scrollZoom': False},
                                  style={'width': '100%', 'height': '50vh', 'minHeight': '300px'}), md=12),
            ]),

            # İmza / Footer
            html.Div(
                [
                    html.Div(
                        [
                            html.Img(
                                src="/assets/ln.png",
                                style={"height": "24px", "marginRight": "10px"}  # logo ile metin arası boşluk
                            ),
                            html.Span(
                                "Serdal Kağan Çelebi",
                                className="text-muted",
                                style={"fontSize": "0.9rem"}
                            )
                        ],
                        className="d-flex align-items-center justify-content-center"  # yatay + dikey ortala
                    ),
                    html.A(
                        "GitHub / LinkedIn / Kişisel Site",
                        href="https://linkedin.com/in/serdalkagancelebi",
                        target="_blank",
                        className="text-muted d-block text-center mt-2",
                        style={"fontSize": "0.85rem"}
                    )
                ],
                className="mt-5 mb-4"
            )
        ], fluid=True, className="px-2")
    )

