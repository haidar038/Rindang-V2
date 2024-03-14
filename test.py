import requests

API_KEY = "294543cfa1ae88aa6e2cb83213707d21b03892c7"

def fetch_komoditas(level_harga_id):
  """
  Mengambil data komoditas berdasarkan level harga.

  Args:
      level_harga_id: ID level harga (misalnya, 1 untuk tingkat nasional).

  Returns:
      List komoditas dengan informasi detail.
  """

  """
  https://www.bi.go.id/hargapangan/WebSite/TabelHarga/GetGridDataDaerah?price_type_id=1&comcat_id=cat_7%2Ccat_8%2Ccom_13%2Ccom_14%2Ccom_15%2Ccom_16&province_id=32&regency_id=79&market_id=&tipe_laporan=1&start_date=2024-03-06&end_date=2024-03-14&_=1710425298417
  """

  url = f"https://panelharga.badanpangan.go.id/api/komoditas-by-levelharga/{level_harga_id}"
  headers = {"apikey": API_KEY}

  response = requests.get(url, headers=headers)
  response.raise_for_status()

  data = response.json()

  komoditas_list = []
  for komoditas in data["result"]:
    komoditas_id = komoditas["id"]

    detail_url = f"https://panelharga.badanpangan.go.id/api/historis-by-province/{level_harga_id}/{komoditas_id}"
    detail_response = requests.get(detail_url, headers=headers)
    detail_response.raise_for_status()

    detail_data = detail_response.json()

    komoditas_detail = {
      "harga_rata_rata": detail_data["hargaratarata"],
      "harga_tertinggi": detail_data["hargatertinggi"],
      "provinsi_tertinggi": detail_data["provinsitertinggi"],
      "harga_terendah": detail_data["hargaterendah"],
      "provinsi_terendah": detail_data["provinsiterendah"],
      "satuan": detail_data["satuan"],
      "nama": komoditas["nama"],
      "id": komoditas["id"],
    }
    # print(komoditas)

    komoditas_list.append(komoditas_detail)

  return komoditas_list

# Contoh penggunaan
level_harga_id = 1
komoditas_list = fetch_komoditas(level_harga_id)

for komoditas in komoditas_list:
  print(komoditas)
