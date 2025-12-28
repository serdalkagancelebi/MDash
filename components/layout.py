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
                        html.A("seçin", href="#", style={"color": "inherit"}),  # inherit → tema uyumlu olsun
                    ]),
                    style={
                        "width": "100%", "height": "60px", "lineHeight": "60px",
                        "borderWidth": "1px", "borderStyle": "dashed", "borderRadius": "5px",
                        "textAlign": "center", "margin": "10px 0"
                    },
                    multiple=False
                ),
                html.Div([
                    "Örnek veri setini indirmek için ",
                    html.A(
                        "buraya tıklayın",
                        href="/assets/ornekveri.csv",
                        download="ornek_veri.csv",           # indirme adı olarak çıksın
                        target="_blank",
                        style={"color": "var(--bs-primary)", "textDecoration": "underline"}
                    ),
                    "."
                ], className="text-center mt-2 small text-muted"),
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
                              config={'responsive': True, 'displayModeBar': False, 'scrollZoom': False},
                              style={'width': '100%', 'height': '50vh', 'minHeight': '300px'})
                ])
            ], className="mb-5"),

            # Tarih seçimi + hızlı butonlar (mobil → dikey, masaüstü → daha yatay)
            dbc.Card(
                dbc.CardBody([
                    html.H5(
                        "Tarih ve Müşteri Filtresi",
                        className="card-title text-center mb-4 fw-semibold"
                    ),

                    # Tarih seçimi + butonlar
                    dbc.Row(
                        className="g-3 justify-content-center mb-4",
                        align="end",  # butonları aşağı hizala
                        children=[
                            # Başlangıç
                            dbc.Col(
                                [
                                    html.Label(
                                        "Başlangıç",
                                        className="form-label small text-center d-block mb-1 fw-medium"
                                    ),
                                    dcc.DatePickerSingle(
                                        id="start-date",
                                        min_date_allowed=min_date,
                                        max_date_allowed=max_date,
                                        date=min_date,
                                        display_format="DD.MM.YYYY",
                                        placeholder="Başlangıç",
                                        className="w-100 form-control-sm",  # biraz daha kompakt
                                        persistence=True,
                                        persistence_type="local",
                                    ),
                                ],
                                xs=12,
                                sm=6,
                                md=5,
                                lg=4,
                                className="text-center"  # label + input ortalı
                            ),

                            # Bitiş
                            dbc.Col(
                                [
                                    html.Label(
                                        "Bitiş",
                                        className="form-label small text-center d-block mb-1 fw-medium"
                                    ),
                                    dcc.DatePickerSingle(
                                        id="end-date",
                                        min_date_allowed=min_date,
                                        max_date_allowed=max_date,
                                        date=max_date,
                                        display_format="DD.MM.YYYY",
                                        placeholder="Bitiş",
                                        className="w-100 form-control-sm",
                                        persistence=True,
                                        persistence_type="local",
                                    ),
                                ],
                                xs=12,
                                sm=6,
                                md=5,
                                lg=4,
                                className="text-center"
                            ),

                            # Butonlar
                            dbc.Col(
                                dbc.ButtonGroup(
                                    [
                                        dbc.Button("Bugün", id="today-button", color="primary", outline=True, size="sm", className="px-3 py-1"),
                                        dbc.Button("Son İşlem", id="last-date-button", color="secondary", outline=True, size="sm", className="px-3 py-1"),
                                        dbc.Button("Temizle", id="reset-date-button", color="danger", outline=True, size="sm", className="px-3 py-1"),
                                    ],
                                    className="d-flex flex-wrap justify-content-center gap-2 w-100"
                                ),
                                xs=12,
                                sm=12,
                                md="auto",
                                lg="auto",
                                className="d-flex align-items-end justify-content-center"
                            ),
                        ]
                    ),

                    # Segment + Müşteri + Temizle
                    dbc.Row(
                        className="g-3 justify-content-center",
                        children=[
                            dbc.Col(segment_dropdown, xs=12, sm=6, md=5, lg=4, className="mb-2 mb-md-0"),
                            dbc.Col(customer_dropdown, xs=12, sm=6, md=5, lg=4, className="mb-2 mb-md-0"),
                            dbc.Col(
                                dbc.Button(
                                    "🧹 Tüm Filtreleri Temizle",
                                    id="reset-filters-button",
                                    color="outline-danger",
                                    size="md",
                                    className="w-100 py-2"
                                ),
                                xs=12,
                                sm=12,
                                md=12,
                                lg=4,
                                className="d-flex align-items-center"
                            ),
                        ]
                    ),
                ]),
                className="mb-4 shadow-sm border-0 mx-auto",
                style={"maxWidth": "980px"}  # masaüstünde çok yayılmasın, ortalı kalsın
            ),

            # Grafikler
            dbc.Row([
                dbc.Col(dcc.Graph(id="top-stock", figure=top_stock_chart(df), responsive=True,
                                  config={'responsive': True, 'displayModeBar': False},
                                  style={'height': '50vh'}), md=6),
                dbc.Col(dcc.Graph(id="cash-expense", figure=cash_vs_expense_pie(df), responsive=True,
                                  config={'responsive': True, 'displayModeBar': False},
                                  style={'height': '50vh'}), md=6)
            ], className="mb-4"),

            dbc.Row([
                dbc.Col(dcc.Graph(id="segment-scatter", figure=segment_scatter(df), responsive=True,
                                  config={'responsive': True, 'displayModeBar': False},
                                  style={'height': '50vh'}), md=12)
            ], className="mb-5"),

            html.Label("Kâr Marjı Eşiği (%)", className="w-100 text-center text-body mt-4"),
            dcc.Slider(
                id="margin-threshold-slider",
                min=5, max=30, step=1, value=10,
                marks={i: f"%{i}" for i in range(5, 31, 5)},
                tooltip={"placement": "bottom", "always_visible": True},
                className="w-100"
                
            ),
            
            dbc.Row(className="mt-5"),  # sadece boş row

            dbc.Row([
                dbc.Col(dcc.Graph(id="profit-scatter", figure=profit_scatter(df), responsive=True,
                                  config={'responsive': True, 'displayModeBar': False},
                                  style={'height': '60vh'}), md=12)
            ], className="mb-5"),
            
            #dbc.Row(className="my-5"),  # sadece boş row
            
            dbc.Row([
                dbc.Col(dcc.Graph(id="sales-year-comparison", figure=sales_year_comparison_chart(df), responsive=True,
                                  config={'responsive': True, 'displayModeBar': False},
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
