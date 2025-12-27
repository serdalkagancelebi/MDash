import os

# Proje kök dizini
base_dir = r"D:\PythonProjects\MikroERPDashboard"

# Oluşturulacak klasörler
folders = [
    "data",
    "components",
    "assets"
]

# Oluşturulacak dosyalar (klasör + dosya adı)
files = {
    "app.py": "",  # ana uygulama dosyası
    os.path.join("components", "kpi_cards.py"): "",
    os.path.join("components", "filters.py"): "",
    os.path.join("components", "charts.py"): "",
    os.path.join("components", "layout.py"): "",
    os.path.join("assets", "custom.css"): "/* Özel CSS stillerini buraya ekle */"
}

# Klasörleri oluştur
for folder in folders:
    path = os.path.join(base_dir, folder)
    os.makedirs(path, exist_ok=True)

# Dosyaları oluştur (varsa dokunma, yoksa boş içerik ekle)
for file, content in files.items():
    path = os.path.join(base_dir, file)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

print("Klasör ve dosya yapısı başarıyla oluşturuldu.")
