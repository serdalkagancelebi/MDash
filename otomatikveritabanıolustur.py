import pandas as pd
import numpy as np

np.random.seed(42)

dates = pd.date_range("2022-01-01", "2025-12-31", freq="M")  # aylık veri, daha kompakt
customers = [
    "Müşteri_0", "Müşteri_4", "Müşteri_6", "Müşteri_10", "Müşteri_30",
    "Müşteri_A", "Müşteri_B", "Müşteri_C"
]
segments = ["A", "B", "C", "D"]

rows = []

for date in dates:
    for cust in customers:
        seg = np.random.choice(segments)
        sales = np.random.randint(10000, 20000)

        # Kontrollü kâr marjı senaryoları
        if cust == "Müşteri_0":
            tahsilat = sales
            gider = sales  # kâr = 0 → marj = 0
        elif cust == "Müşteri_4":
            tahsilat = sales
            gider = sales * 0.96  # kâr marjı ≈ %4
        elif cust == "Müşteri_6":
            tahsilat = sales
            gider = sales * 0.94  # kâr marjı ≈ %6
        elif cust == "Müşteri_10":
            tahsilat = sales
            gider = sales * 0.90  # kâr marjı ≈ %10
        elif cust == "Müşteri_30":
            tahsilat = sales
            gider = sales * 0.70  # kâr marjı ≈ %30
        else:
            # Rastgele senaryolar (pozitif/negatif kar marjı)
            tahsilat = sales * np.random.uniform(0.8, 1.2)
            gider = tahsilat * np.random.uniform(0.5, 1.1)

        stok = np.random.randint(50, 500)

        rows.append([date, cust, seg, sales, tahsilat, gider, stok])

df = pd.DataFrame(rows, columns=["Tarih", "Müşteri", "Segment", "Satış", "Tahsilat", "Gider", "Stok"])
df.to_csv("mikro_dummy_data.csv", index=False, encoding="utf-8-sig")

print("Yeni dummy veri dosyası oluşturuldu: mikro_dummy_data.csv")
