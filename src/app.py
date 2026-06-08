from flask import Flask, request, jsonify
import time
import uuid

app = Flask(__name__)

# Başarısız giriş denemelerini ve kilit durumlarını tutuyoruz
failed_attempts = {}

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '')
    password = data.get('password', '')
    client_ip = request.remote_addr
    
    track_key = f"{username}_{client_ip}"
    
    if track_key not in failed_attempts:
        failed_attempts[track_key] = {'deneme_sayisi': 0, 'kilitli': False, 'kilit_acma_tokeni': None}
        
    user_record = failed_attempts[track_key]
    
    # 1. Kilit Kontrolü
    if user_record['kilitli']:
        return jsonify({
            "durum": "hata", 
            "mesaj": "Hesabınız kilitli. Lütfen e-postanıza gönderilen bağlantı ile kilidi açın."
        }), 403
        
    # 2. Başarılı Giriş Senaryosu
    if username == "admin" and password == "admin123":
        user_record['deneme_sayisi'] = 0
        return jsonify({"durum": "basarili", "mesaj": "Giriş başarılı!"})
        
    # 3. Hatalı Giriş ve Kademeli Gecikme
    user_record['deneme_sayisi'] += 1
    deneme = user_record['deneme_sayisi']
    
    # 10. Denemede hesabı kilitle ve e-posta simülasyonu tetikle
    if deneme >= 10:
        user_record['kilitli'] = True
        user_record['kilit_acma_tokeni'] = str(uuid.uuid4()) # Benzersiz bir kilit açma şifresi oluştur
        
        # Gerçek bir e-posta atmak yerine sistem loglarına yazdırıyoruz (Simülasyon)
        print("\n" + "="*50)
        print(f"[GÜVENLİK UYARISI] {username} hesabı kilitlendi!")
        print(f"Hedef IP: {client_ip}")
        print(f"Kilit Açma Linki: http://127.0.0.1:5000/unlock/{user_record['kilit_acma_tokeni']}")
        print("="*50 + "\n")
        
        return jsonify({"durum": "hata", "mesaj": "Maksimum deneme sayısına ulaşıldı. Hesap kilitlendi!"}), 403

    gecikme_suresi = 0
    if 4 <= deneme <= 6:
        gecikme_suresi = 2
    elif 7 <= deneme <= 9:
        gecikme_suresi = 10
        
    if gecikme_suresi > 0:
        time.sleep(gecikme_suresi)
        
    return jsonify({
        "durum": "hata", 
        "kalan_deneme_hakki": 10 - deneme,
        "uygulanan_gecikme": f"{gecikme_suresi} saniye"
    }), 401

# Yeni Eklenen: Kilit Açma Endpoint'i
@app.route('/unlock/<token>', methods=['GET'])
def unlock(token):
    # Sistemdeki tüm kayıtları gezip eşleşen tokeni buluyoruz
    for key, record in failed_attempts.items():
        if record.get('kilit_acma_tokeni') == token:
            # Kilidi kaldır ve sayaçları sıfırla
            record['kilitli'] = False
            record['deneme_sayisi'] = 0
            record['kilit_acma_tokeni'] = None
            return jsonify({"durum": "basarili", "mesaj": "Hesap kilidiniz başarıyla açıldı! Yeniden giriş yapabilirsiniz."})
            
    return jsonify({"durum": "hata", "mesaj": "Geçersiz veya süresi dolmuş bağlantı."}), 400

if __name__ == '__main__':
    app.run(debug=True)