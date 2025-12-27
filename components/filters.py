from dash import dcc

def generate_filters(df):
    segment_options = [{"label": s, "value": s} for s in sorted(df["Segment"].dropna().unique())]
    customer_options = [{"label": c, "value": c} for c in sorted(df["Müşteri"].dropna().unique())]

    return [
        dcc.Dropdown(
            id="segment-filter",
            options=segment_options,
            multi=True,
            placeholder="Segment seçin",
            className="mb-2"
        ),
        dcc.Dropdown(
            id="customer-filter",
            options=customer_options,
            multi=True,
            placeholder="Müşteri seçin"
        )
    ]
