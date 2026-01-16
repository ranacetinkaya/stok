# 🚀 Deployment Rehberi - Multi-User Bershka Stok Takip

Bu uygulama **birden fazla kullanıcı** için tasarlanmıştır. Her kullanıcının:
- ✅ Kendi oturumu var (email ile giriş)
- ✅ Kendi ürün listesi var (karışmaz)
- ✅ Kendi email ayarları var (bildirimler kendi email'ine gider)
- ✅ Kendi stok takipleri var (her kullanıcı bağımsız çalışır)

## 📋 Multi-User Desteği Kontrolü

### ✅ Veritabanı Yapısı
- `kullanicilar` tablosu: Her kullanıcının email, isim ve email ayarları
- `urunler` tablosu: Her ürün `kullanici_id` ile bağlı (veriler karışmaz)
- Her sorgu `kullanici_id` ile filtreleniyor

### ✅ Güvenlik
- Her kullanıcı sadece kendi ürünlerini görebilir
- Her kullanıcı sadece kendi ürünlerini silebilir
- Email bildirimleri kullanıcının kendi email ayarlarıyla gönderilir

## 🌐 Deployment Seçenekleri

### 1. Railway (Önerilen - En Kolay) ⭐

**Avantajlar:**
- ✅ Ücretsiz tier mevcut ($5 kredi/ay)
- ✅ Otomatik deploy (GitHub push ile)
- ✅ Kolay kurulum
- ✅ SQLite desteği (ekstra database gerekmez)
- ✅ Multi-user hazır

**Adımlar:**

1. **Railway hesabı oluşturun:**
   - https://railway.app/ adresine gidin
   - GitHub ile giriş yapın

2. **Yeni proje oluşturun:**
   - "New Project" butonuna tıklayın
   - "Deploy from GitHub repo" seçin
   - Repository'nizi seçin

3. **Backend'i deploy edin:**
   - Root directory: `backend`
   - Start command: `python app.py`
   - Port: Railway otomatik atar (PORT env var kullanılır)

4. **Environment Variables ekleyin:**
   ```
   PORT=5001
   HOST=0.0.0.0
   DEBUG=False
   DATABASE_PATH=stok.db
   ```

5. **Frontend'i deploy edin:**
   - Yeni bir service oluşturun
   - Root directory: `frontend`
   - Build command: `npm install && npm run build`
   - Start command: `npm run preview` (veya `npx serve dist`)
   - Port: `3000`
   - Environment Variable: `VITE_API_URL=https://your-backend-url.railway.app/api`

### 2. Render (Alternatif)

**Adımlar:**

1. https://render.com/ adresine gidin
2. "New Web Service" oluşturun
3. GitHub repo'nuzu bağlayın
4. Backend için:
   - Build Command: `cd backend && pip install -r requirements.txt`
   - Start Command: `cd backend && python app.py`
   - Environment Variables:
     ```
     PORT=5001
     HOST=0.0.0.0
     DEBUG=False
     DATABASE_PATH=stok.db
     ```
5. Frontend için ayrı bir service oluşturun:
   - Build Command: `cd frontend && npm install && npm run build`
   - Start Command: `cd frontend && npx serve dist -s -l 3000`
   - Environment Variable: `VITE_API_URL=https://your-backend-url.onrender.com/api`

### 3. VPS (Kendi Sunucunuz)

Eğer kendi sunucunuz varsa:

1. **SSH ile bağlanın**
2. **Python ve gerekli paketleri yükleyin**
3. **systemd service oluşturun:**

```bash
# /etc/systemd/system/stok-takip.service
[Unit]
Description=Bershka Stok Takip (Multi-User)
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/stok/backend
Environment="PATH=/path/to/venv/bin"
Environment="PORT=5001"
Environment="HOST=0.0.0.0"
Environment="DEBUG=False"
Environment="DATABASE_PATH=/path/to/stok/backend/stok.db"
ExecStart=/path/to/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

4. **Servisi başlatın:**
```bash
sudo systemctl enable stok-takip
sudo systemctl start stok-takip
```

5. **Frontend için Nginx kullanın:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    root /path/to/stok/frontend/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📝 Deployment Öncesi Hazırlık

### 1. Procfile (Backend)

`backend/Procfile` zaten mevcut:
```
web: python app.py
```

### 2. Port ve Host Ayarları

Backend'de port ve host zaten environment variable'dan alınıyor:
```python
port = int(os.getenv('PORT', 5001))
host = os.getenv('HOST', '127.0.0.1')
app.run(debug=debug, host=host, port=port)
```

### 3. CORS Ayarları

Production için CORS ayarları yapıldı:
```python
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

### 4. Database Path

SQLite database path environment variable'dan alınıyor:
```python
DATABASE_PATH = os.getenv('DATABASE_PATH', 'stok.db')
```

### 5. Frontend API URL

Frontend'de API URL environment variable'dan alınıyor:
```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api'
```

## ✅ Multi-User Test

Deploy sonrası test:

1. **İlk kullanıcı kaydı:**
   - Email: `user1@example.com`
   - Ürün ekle
   - Email ayarlarını yap

2. **İkinci kullanıcı kaydı:**
   - Email: `user2@example.com`
   - Ürün ekle
   - Email ayarlarını yap

3. **Kontrol:**
   - User1 sadece kendi ürünlerini görmeli
   - User2 sadece kendi ürünlerini görmeli
   - Veriler karışmamalı
   - Her kullanıcı kendi email'ine bildirim almalı

## 🔒 Güvenlik Notları

1. **HTTPS kullanın:** Production'da mutlaka HTTPS kullanın
2. **Email şifreleri:** Email şifreleri environment variable'da saklanıyor (güvenli)
3. **Database:** SQLite dosyası güvenli bir yerde saklanmalı
4. **CORS:** Production'da CORS ayarlarını sınırlandırabilirsiniz

## 📧 Email Ayarları

Her kullanıcı kendi email ayarlarını yapılandırır:
- Frontend'de "Email Ayarları" bölümünden
- SMTP sunucusu, port, email ve şifre
- Gmail için Uygulama Şifresi kullanılmalı

## 🎯 Önerilen Çözüm

**Railway** kullanmanızı öneririm çünkü:
- ✅ Ücretsiz tier var ($5 kredi/ay)
- ✅ Çok kolay kurulum
- ✅ Otomatik deploy (GitHub push ile)
- ✅ 7/24 çalışır
- ✅ Multi-user hazır
- ✅ Bilgisayarınızı açık tutmanıza gerek yok

## 🔄 Sürekli Kontrol

Deploy ettikten sonra:
- ✅ Sistem 7/24 çalışır
- ✅ Her 5 saniyede bir kontrol yapar
- ✅ Stok geldiğinde anında email gönderir
- ✅ Her kullanıcı kendi bildirimlerini alır
- ✅ Bilgisayarınızı açık tutmanıza gerek yok

## 🐛 Sorun Giderme

### Database bulunamıyor
- `DATABASE_PATH` environment variable'ını kontrol edin
- Railway/Render'da persistent storage kullanın

### CORS hatası
- Backend'de CORS ayarlarını kontrol edin
- Frontend API URL'ini kontrol edin

### Email gönderilmiyor
- Kullanıcının email ayarlarını kontrol edin
- Gmail için Uygulama Şifresi kullanıldığından emin olun
- Backend log'larını kontrol edin

## 📞 Destek

Sorun yaşarsanız:
1. Backend log'larını kontrol edin
2. Frontend console'u kontrol edin
3. Database'i kontrol edin (SQLite browser ile)
