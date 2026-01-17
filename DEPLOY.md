# 🚀 Sürekli Çalıştırma (Deploy) Rehberi

Python kodunu sürekli çalıştırmak yerine, buluta deploy edebilirsiniz. Böylece 7/24 çalışır ve sizin bilgisayarınızı açık tutmanıza gerek kalmaz.

## 🌐 Deployment Seçenekleri

### 1. Railway (Önerilen - En Kolay) ⭐

**Avantajlar:**
- Ücretsiz tier mevcut
- Otomatik deploy
- Kolay kurulum
- PostgreSQL desteği (SQLite yerine)

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
   - Port: `5001` (veya Railway otomatik atar)

4. **Environment Variables ekleyin:**
   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   RECIPIENT_EMAIL=your-email@gmail.com
   ```

5. **Frontend'i deploy edin:**
   - Yeni bir service oluşturun
   - Root directory: `frontend`
   - Build command: `npm install && npm run build`
   - Start command: `npm run preview`
   - Port: `3000`

### 2. Render (Alternatif)

**Adımlar:**

1. https://render.com/ adresine gidin
2. "New Web Service" oluşturun
3. GitHub repo'nuzu bağlayın
4. Backend için:
   - Build Command: `cd backend && pip install -r requirements.txt`
   - Start Command: `cd backend && python app.py`
5. Frontend için ayrı bir service oluşturun

### 3. Heroku (Klasik)

**Adımlar:**

1. Heroku CLI yükleyin:
   ```bash
   brew tap heroku/brew && brew install heroku
   ```

2. Heroku'ya giriş yapın:
   ```bash
   heroku login
   ```

3. Proje oluşturun:
   ```bash
   cd backend
   heroku create stok-takip-backend
   ```

4. Deploy edin:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push heroku main
   ```

5. Environment variables ekleyin:
   ```bash
   heroku config:set SMTP_SERVER=smtp.gmail.com
   heroku config:set EMAIL_USER=your-email@gmail.com
   # ... diğer değişkenler
   ```

### 4. VPS (Kendi Sunucunuz)

Eğer kendi sunucunuz varsa:

1. **SSH ile bağlanın**
2. **Python ve gerekli paketleri yükleyin**
3. **systemd service oluşturun:**

```bash
# /etc/systemd/system/stok-takip.service
[Unit]
Description=Bershka Stok Takip
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/stok/backend
Environment="PATH=/path/to/venv/bin"
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

## 📝 Deployment Öncesi Hazırlık

### 1. Procfile Oluşturun (Heroku/Railway için)

`backend/Procfile`:
```
web: python app.py
```

### 2. Port'u Dinamik Yapın

Backend'de port'u environment variable'dan alın:

```python
import os
port = int(os.getenv('PORT', 5001))
app.run(debug=False, host='0.0.0.0', port=port)
```

### 3. requirements.txt'i Güncelleyin

Tüm bağımlılıkların olduğundan emin olun.

## ✅ Kontrol Aralığını Kısaltma

Kontrol aralığını 15 saniyeye düşürdük. Daha da hızlı isterseniz:

`backend/app.py` dosyasında:
```python
time.sleep(10)  # 10 saniye
# veya
time.sleep(5)   # 5 saniye (çok agresif)
```

## 🎯 Önerilen Çözüm

**Railway** kullanmanızı öneririm çünkü:
- ✅ Ücretsiz tier var
- ✅ Çok kolay kurulum
- ✅ Otomatik deploy
- 7/24 çalışır
- ✅ Bilgisayarınızı açık tutmanıza gerek yok

## 📧 Email Ayarları

Deploy ettikten sonra email ayarlarını environment variables olarak ekleyin. Gmail için Uygulama Şifresi kullanmayı unutmayın.

## 🔄 Sürekli Kontrol

Deploy ettikten sonra:
- ✅ Sistem 7/24 çalışır
- ✅ Her 15 saniyede bir kontrol yapar
- ✅ Stok geldiğinde anında email gönderir
- ✅ Bilgisayarınızı açık tutmanıza gerek yok
