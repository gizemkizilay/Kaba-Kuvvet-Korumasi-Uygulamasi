import requests
import time

url = 'http://127.0.0.1:5000/login'
# Kasten yanlış şifre gönderiyoruz ki savunma sistemimiz tetiklensin
payload = {'username': 'admin', 'password': 'yanlissifre123'}

print("Kaba Kuvvet (Brute Force) Saldırı Simülasyonu Başlıyor...\n")

# Sistemi 12 kez test edeceğiz (10'da kilitlenmesi lazım)
for i in range(1, 13):
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload)
        elapsed_time = time.time() - start_time
        
        # Sunucudan gelen yanıtı JSON olarak alıyoruz
        data = response.json()
        
        print(f"Deneme {i} - Geçen Süre: {elapsed_time:.2f} saniye")
        print(f"Sonuç: {data.get('mesaj')}")
        
        if 'kalan_deneme_hakki' in data:
            print(f"Kalan Hak: {data['kalan_deneme_hakki']}")
            
        print("-" * 40)
        
    except requests.exceptions.RequestException as e:
        print(f"Bağlantı hatası: {e}")
        break