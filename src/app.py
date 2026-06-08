from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
import time
import uuid
import os

app = Flask(__name__)

# ---------------------------------------------------------
# 1. GÜVENLİK BAŞLIKLARI (CSP ve HSTS) - Flask-Talisman
# ---------------------------------------------------------
csp = {
    'default-src': ['\'self\''],
    'script-src': ['\'self\'']
}
# force_https=False yapıyoruz çünkü şu an localhost'ta test ediyoruz.
Talisman(app, content_security_policy=csp, force_https=False)

# ---------------------------------------------------------
# 2. RATE LIMITING MIDDLEWARE - Flask-Limiter
# ---------------------------------------------------------
# Dakikada maksimum 20, saniyede 5 isteğe izin ver (DDoS koruması)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "20 per minute"]
)

# ---------------------------------------------------------
# 3. VERİTABANI (SQLite) - Kalıcı Depolama
# ---------------------------------------------------------
# 'instance/security.db' adında bir dosya oluşturup verileri oraya yazacak
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///security.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class LoginRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    track_key = db.Column(db.String(100), unique=True, nullable=False)
    deneme_sayisi = db.Column(db.Integer, default=0)
    kilitli = db.Column(db.Boolean, default=False)
    kilit_acma_tokeni = db.Column(db.String(100), nullable=True)

# Sunucu başlarken veritabanı dosyasını otomatik oluştur
with app.app_context():
    db.create_all()

# ---------------------------------------------------------
# 4. GERÇEK E-POSTA ALTYAPISI - Flask-Mail
# ---------------------------------------------------------
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'sandbox.smtp.mailtrap.io')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 2525))
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '') # Mailtrap'ten alınacak
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '') # Mailtrap'ten alınacak
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

# ---------------------------------------------------------
# API ENDPOINT'LERİ
# ---------------------------------------------------------
@app.route('/login', methods=['POST'])
@limiter.limit("15 per minute") # /login rotasına özel ekstra middleware kısıtlaması
def login():
    data = request.get_json() or {}
    username = data.get('username', '')
    password = data.get('password', '')
    client_ip = request.remote_addr
    
    track_key = f"{username}_{client_ip}"
    
    # Veritabanından kaydı getir veya yeni kayıt oluştur
    record = LoginRecord.query.filter_by(track_key=track_key).first()
    if not record:
        record = LoginRecord(track_key=track_key)
        db.session.add(record)
        db.session.commit()
        
    if record.kilitli:
        return jsonify({"durum": "hata", "mesaj": "Hesabınız kilitli. Lütfen e-postanızı kontrol edin."}), 403
        
    # Başarılı Giriş
    if username == "admin" and password == "admin123":
        record.deneme_sayisi = 0
        db.session.commit()
        return jsonify({"durum": "basarili", "mesaj": "Giriş başarılı!"})
        
    # Hatalı Giriş Senaryosu
    record.deneme_sayisi += 1
    deneme = record.deneme_sayisi
    
    # 10. Deneme: Kilitle ve E-posta Gönder
    if deneme >= 10:
        record.kilitli = True
        token = str(uuid.uuid4())
        record.kilit_acma_tokeni = token
        db.session.commit()
        
        # Gerçek e-posta gönderim bloğu
        try:
            msg = Message("Güvenlik Uyarısı: Hesabınız Kilitlendi",
                          sender="security@qline.tech",
                          recipients=["kendi_mailin@gmail.com"]) # Test için buraya kendi mailini yazabilirsin
            
            unlock_link = f"http://127.0.0.1:5000/unlock/{token}"
            msg.body = f"Merhaba,\nHesabınıza yönelik çok fazla başarısız giriş tespit ettik ve güvenliğiniz için hesabı kilitledik.\nKilidi açmak için tıklayın: {unlock_link}"
            mail.send(msg)
            print(">>> [BAŞARILI] Kilit açma maili SMTP sunucusuna iletildi.")
        except Exception as e:
            print(f">>> [HATA] E-posta gönderilemedi (SMTP ayarlarını kontrol edin): {e}")
            print(f">>> Loglanan Link: http://127.0.0.1:5000/unlock/{token}")
        
        return jsonify({"durum": "hata", "mesaj": "Maksimum deneme sayısına ulaşıldı. Hesap kilitlendi!"}), 403

    db.session.commit() # Deneme sayısını veritabanına kaydet

    # Kademeli Gecikme (Throttling)
    gecikme_suresi = 0
    if 4 <= deneme <= 6:
        gecikme_suresi = 2
    elif 7 <= deneme <= 9:
        gecikme_suresi = 10
        
    if gecikme_suresi > 0:
        time.sleep(gecikme_suresi)
        
    return jsonify({"durum": "hata", "kalan_deneme_hakki": 10 - deneme, "uygulanan_gecikme": f"{gecikme_suresi} saniye"}), 401

@app.route('/unlock/<token>', methods=['GET'])
def unlock(token):
    # Veritabanında token'ı ara
    record = LoginRecord.query.filter_by(kilit_acma_tokeni=token).first()
    if record:
        record.kilitli = False
        record.deneme_sayisi = 0
        record.kilit_acma_tokeni = None
        db.session.commit()
        return jsonify({"durum": "basarili", "mesaj": "Hesap kilidiniz veritabanından başarıyla kaldırıldı!"})
        
    return jsonify({"durum": "hata", "mesaj": "Geçersiz veya süresi dolmuş bağlantı."}), 400

if __name__ == '__main__':
    app.run(debug=True)
