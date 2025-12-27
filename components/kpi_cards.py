import dash_bootstrap_components as dbc
from dash import html

def generate_kpi_cards(df):
    total_sales  = df["Satış"].sum()
    total_cashin = df["Tahsilat"].sum()
    total_expense = df["Gider"].sum()
    net_cash     = total_cashin - total_expense

    cards = dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Toplam Satış", className="fs-5 fw-bold text-center py-2"),
            dbc.CardBody(
                f"₺{total_sales:,.0f}",
                className="fs-3 fw-bold text-center py-3"   # ← en büyük fark burada
            )
        ], color="primary", inverse=True), md=3),

        dbc.Col(dbc.Card([
            dbc.CardHeader("Tahsilat", className="fs-5 fw-bold text-center py-2"),
            dbc.CardBody(
                f"₺{total_cashin:,.0f}",
                className="fs-3 fw-bold text-center py-3"
            )
        ], color="success", inverse=True), md=3),

        dbc.Col(dbc.Card([
            dbc.CardHeader("Gider", className="fs-5 fw-bold text-center py-2"),
            dbc.CardBody(
                f"₺{total_expense:,.0f}",
                className="fs-3 fw-bold text-center py-3"
            )
        ], color="danger", inverse=True), md=3),

        dbc.Col(dbc.Card([
            dbc.CardHeader("Net Nakit", className="fs-5 fw-bold text-center py-2"),
            dbc.CardBody(
                f"₺{net_cash:,.0f}",
                className="fs-3 fw-bold text-center py-3"
            )
        ], color="info", inverse=True), md=3),
    ], className="g-3")  # kartlar arası boşluk güzel olsun diye

    return cards