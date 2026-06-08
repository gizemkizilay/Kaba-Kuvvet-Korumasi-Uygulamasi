# Araştırma ve Geliştirme Notları

Bu projede kaba kuvvet saldırılarını engellemek için şu stratejileri izledim:

1. **Kademeli Gecikme (Throttling):** Saldırganı anında engellemek yerine, sistem kaynaklarını korumak için 4. denemeden sonra 2 saniye, 7. denemeden sonra 10 saniye bekleme süresi koydum.
2. **Kalıcı Veritabanı:** Hesap kilitleme durumlarını bellek yerine SQLite veritabanında tutarak, sunucu yeniden başlasa bile kilitlerin kalıcı olmasını sağladım.
3. **Güvenlik Başlıkları:** Flask-Talisman kullanarak modern web standartlarına uygun güvenlik başlıklarını (CSP) aktif ettim.
