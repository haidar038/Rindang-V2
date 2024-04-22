import requests
from datetime import datetime, timedelta

# Get current date and date one week ago
today = datetime.today()
one_week_ago = today - timedelta(days=7)

# Format dates as YYYY-MM-DD
start_date = one_week_ago.strftime("%Y-%m-%d")
end_date = today.strftime("%Y-%m-%d")

url = f"https://panelharga.badanpangan.go.id/data/kabkota-range-by-levelharga/458/3/{start_date}/{end_date}"

response = requests.get(url)
response.raise_for_status()

data = response.json()

target = ["Cabai Merah Keriting", "Cabai Rawit Merah", "Bawang Merah"]

for item in data["data"]:
    if item["name"] in target:
        komoditas = item["by_date"]
        print(f"Data untuk {item['name']}:")
        print(komoditas)