import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Debug amaçlı: segmentleri görmek için
df = pd.read_csv("data/mikro_dummy_data.csv")
print(df["Segment"].unique())

def sales_trend_chart(df):
    df["Satış"] = pd.to_numeric(df["Satış"], errors="coerce")
    df = df[df["Satış"] > 0]

    df_grouped = df.groupby("Tarih")["Satış"].sum().reset_index()

    fig = px.line(
        df_grouped,
        x="Tarih",
        y="Satış",
        title="📈 Günlük Satış Trendleri",
        line_shape="spline"
    )

    fig.update_traces(
        hovertemplate="Tarih: %{x|%d %b %Y}<br>Satış: ₺%{y:,.0f}<extra></extra>"
    )

    fig.update_layout(
        xaxis=dict(
            tickformat="%d %b %Y",
            tickangle=45,
            tickmode="linear",
            dtick=604800000 # 7 gün = 7 * 24 * 60 * 60 * 1000 ms
        ),
        xaxis_title="Tarih (Haftalar)",
        yaxis_title="Satış (₺)",
        margin=dict(l=10, r=10, t=50, b=10)
    )

    return fig


def top_stock_chart(df, top_n=10):
    t = df.groupby("Müşteri")["Stok"].sum().nlargest(top_n).reset_index()
    fig = px.bar(
        t,
        x="Müşteri",
        y="Stok",
        title=f"📦 En Yüksek Stoklu {top_n} Müşteri",
        color="Stok",
        color_continuous_scale="Blues"
    )
    fig.update_traces(
        hovertemplate="Müşteri: %{x}<br>Stok: %{y:,.0f}<extra></extra>"
    )
    return fig


def cash_vs_expense_pie(df):
    sum_cashin = df["Tahsilat"].sum()
    sum_expense = df["Gider"].sum()
    fig = go.Figure(
        go.Pie(
            labels=["Tahsilat", "Gider"],
            values=[sum_cashin, sum_expense],
            hole=0.45,
            textinfo="label+percent",
            hovertemplate="%{label}: ₺%{value:,.0f}<extra></extra>"
        )
    )
    fig.update_layout(title="💰 Tahsilat vs Gider")
    return fig


def segment_scatter(df):
    seg = df.groupby("Segment")[["Satış", "Tahsilat"]].mean().reset_index()
    fig = px.scatter(
        seg,
        x="Satış",
        y="Tahsilat",
        color="Segment",
        size="Satış",
        hover_name="Segment",
        title="👥 Segment Bazlı Ortalama Satış vs Tahsilat",
        labels={
            "Satış": "Satış (₺)",
            "Tahsilat": "Tahsilat (₺)",    
        },       
    )
    fig.update_traces(
        hovertemplate="Segment: %{hovertext}<br>Satış: ₺%{x:,.0f}<br>Tahsilat: ₺%{y:,.0f}<extra></extra>"
    )
    return fig


def profit_scatter(df, threshold=0.10):
    # Kâr ve kâr marjı hesapla
    df["Kar"] = df["Tahsilat"] - df["Gider"]
    df["Kar Marjı"] = df["Kar"] / df["Satış"]
    df["Kar Marjı"] = df["Kar Marjı"].replace([np.inf, -np.inf], np.nan).clip(lower=-1, upper=1)
    df["Segment"] = df["Segment"].astype(str).str.strip().fillna("Bilinmiyor")

    # Müşteri bazlı özet
    df_grouped = df.groupby("Müşteri").agg({
        "Satış": "sum",
        "Tahsilat": "sum",
        "Gider": "sum",
        "Kar": "sum",
        "Kar Marjı": "mean",
        "Segment": lambda x: x.mode().iloc[0] if not x.mode().empty else "Bilinmiyor"
    }).reset_index()

    # Renk skalası: 0 merkezli, simetrik
    kar_marji_min = float(df_grouped["Kar Marjı"].min() or -0.3)
    kar_marji_max = float(df_grouped["Kar Marjı"].max() or 0.3)
    max_abs = max(abs(kar_marji_min), abs(kar_marji_max), 0.3)
    range_min, range_max = -max_abs, max_abs

    fig = px.scatter(
        df_grouped,
        x="Satış",
        y="Kar",
        color="Kar Marjı",
        color_continuous_scale="RdYlGn",
        range_color=(range_min, range_max),
        size="Satış",
        hover_name="Müşteri",
        title="💸 Müşteri Bazlı Satış vs Kâr",
        labels={
            "Satış": "Toplam Satış (₺)",
            "Kar": "Toplam Kâr (₺)",
            "Kar Marjı": "Kâr Marjı"
        },
        custom_data=["Segment", "Kar Marjı"]
    )

    # Tooltip
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b>"
                      "<br>Segment: %{customdata[0]}"
                      "<br>Satış: ₺%{x:,.0f}"
                      "<br>Kâr: ₺%{y:,.0f}"
                      "<br>Kâr Marjı: %{customdata[1]:.1%}<extra></extra>"
    )

    # Eşik çizgisi
    x_min = max(0, float(df_grouped["Satış"].min() or 0))
    x_max = float(df_grouped["Satış"].max() or 1000000)
    fig.add_scatter(
        x=[x_min, x_max],
        y=[threshold * x_min, threshold * x_max],
        mode="lines",
        line=dict(color="red", dash="dash", width=2),
        name=f"Kâr Marjı %{int(threshold * 100)} Eşiği"
    )

    # Eşik altı müşterileri işaretle (mobil için daha küçük)
    df_below = df_grouped[df_grouped["Kar"] < threshold * df_grouped["Satış"]]
    fig.add_trace(
        go.Scatter(
            x=df_below["Satış"],
            y=df_below["Kar"],
            mode="markers",
            marker=dict(
                symbol="x",
                color="red",
                size=7,                  # küçülttük
                line=dict(width=1.2)
            ),
            name="Eşik Altı Müşteri",
            hovertemplate="%{text}<br>Satış: ₺%{x:,.0f}<extra></extra>",
            text=df_below["Müşteri"]
        )
    )

    # ── MOBİL DOSTU LAYOUT ────────────────────────────────
    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=140),   # ← ALT MARGIN'İ ÖNEMLİ ARTTIRDIK (140px)
        
        # Colorbar yatay, daha aşağıda ve biraz daha kısa
        coloraxis_colorbar=dict(
            orientation="h",
            y=-0.32,                   # ← daha aşağı taşı (daha önce -0.22 idi)
            x=0.5,
            xanchor="center",
            yanchor="top",
            len=0.75,                  # ← biraz kısalttık ki taşmasın
            thickness=12,              # incelttik
            title=dict(
                text="Kâr Marjı (%)",
                font=dict(size=11),    # biraz küçülttük
                side="top"
            ),
            tickfont=dict(size=9),
            tickformat=".0%",
        ),
        
        # Legend'i de daha aşağı ve ortalı yaptık + font küçült
        legend=dict(
            orientation="h",
            x=0.5,
            y=-0.61,                   # ← colorbar'ın altına, daha aşağı
            xanchor="center",
            yanchor="top",
            bgcolor="rgba(15,15,45,0.6)",
            bordercolor="rgba(255,255,255,0.2)",
            borderwidth=1,
            font=dict(color="#e0e0e0", size=10),        # küçülttük
            tracegroupgap=8,           # item'lar arası boşluk azalt
            itemclick="toggle",        # tıklanabilir kalsın
        ),
        
        # Genel font ve hover iyileştirmeleri
        
        title_font_size=16,
        hoverlabel=dict(
        bgcolor="rgba(0,0,0,0.8)",
        font_color="#ffffff"
        ),
        dragmode="pan",
        
        # Eksen etiketleri de sıkışmasın diye
        xaxis_title_font=dict(size=12),
        yaxis_title_font=dict(size=12),
        xaxis_tickfont=dict(size=10),
        yaxis_tickfont=dict(size=10),
    )

    return fig


def sales_year_comparison_chart(df):
    df["Tarih"] = pd.to_datetime(df["Tarih"], dayfirst=True, errors="coerce")
    df["Satış"] = pd.to_numeric(df["Satış"], errors="coerce")

    df["Yıl"] = df["Tarih"].dt.year
    df["Ay"] = df["Tarih"].dt.month

    grouped = df.groupby(["Yıl", "Ay"])["Satış"].sum().reset_index()

    fig = px.line(
        grouped,
        x="Ay",
        y="Satış",
        color="Yıl",
        markers=True,
        title="📊 Yıllık Satış Karşılaştırması (Geçen Yıllar vs Bu Yıl)",
        labels={"Ay": "Ay", "Satış": "Toplam Satış (₺)", "Yıl": "Yıl"},
        custom_data=["Yıl"]
    )

    fig.update_traces(
        hovertemplate="Yıl: %{customdata[0]}<br>Ay: %{x}<br>Satış: ₺%{y:,.0f}<extra></extra>"
    )

    fig.update_layout(
        xaxis=dict(tickmode="linear", tick0=1, dtick=1),
        margin=dict(l=10, r=10, t=60, b=10)
    )

    return fig

