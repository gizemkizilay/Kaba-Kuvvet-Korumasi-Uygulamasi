# Proje Yol Haritası (Roadmap)

## Faz 0: Yazmadan Önce Anla
- Kaba kuvvet saldırılarının doğasını anlama.
- Neden anında kilitlemek yerine kademeli gecikme (throttling) kullanmalıyız sorusunun cevabını bulma.

## Faz 1: Araştırma ve Keşif
- Rate limiting algoritmalarının incelenmesi.
- IP tabanlı vs. Hesap tabanlı engelleme stratejilerinin analizi.
- *(Detaylar docs/research/ klasöründe belgelenmiştir.)*

## Faz 2: Ortam Kurulumu
- Python Flask ortamının ayağa kaldırılması.
- Bağımlılıkların (requirements.txt) ve Docker konteyner yapısının yapılandırılması.

## Faz 3: Uygulama
1. Temel Login API endpoint'inin oluşturulması.
2. Başarısız denemeleri sayacak sözlük (dictionary) yapısının kurgulanması.
3. 4. denemeden sonra 2 saniye, 7. denemeden sonra 10 saniye gecikme eklenmesi.
4. 10. denemede hesabın kilitlenmesi.
5. UUID tabanlı kilit açma (unlock) rotasının yazılması.

## Faz 4: Test ve Raporlama
- `requests` kütüphanesi ile `attack.py` betiğinin yazılması.
- API'ye 12 ardışık istek atılarak savunma ve kilitleme mekanizmalarının test edilmesi.

## Faz 5: Teslim Kontrol Listesi
- [x] Tüm kodların `src` klasörüne taşınması.
- [x] Dockerfile ve docker-compose.yml dosyalarının hazırlanması.
- [x] Markdown belgelerinin (README, ROADMAP) şablona uygun tamamlanması.
- [x] Danışman hocanın repoya Collaborator olarak eklenmesi.