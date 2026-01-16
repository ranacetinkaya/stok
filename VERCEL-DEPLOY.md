# 🚀 Vercel + Railway Deploy Rehberi

Frontend: **Vercel** (Ücretsiz, kolay)  
Backend: **Railway** (Ücretsiz tier, Flask için ideal)

## 📋 Adım Adım Deploy

### 1️⃣ Backend'i Railway'e Deploy Et

#### A. Railway Hesabı Oluştur
1. https://railway.app/ adresine gidin
2. "Start a New Project" butonuna tıklayın
3. GitHub ile giriş yapın

#### B. Proje Oluştur
1. "Deploy from GitHub repo" seçin
2. Repository'nizi seçin
3. "Deploy Now" butonuna tıklayın

#### C. Backend Ayarları
1. **Settings** sekmesine gidin
2. **Root Directory** ayarlayın: `backend`
3. **Start Command** ayarlayın: `python app.py`

#### D. Environment Variables Ekle
**Variables** sekmesine gidin ve şunları ekleyin:

```
PORT=5001
HOST=0.0.0.0
DEBUG=False
DATABASE_PATH=stok.db
```

⚠️ **Selenium için ChromeDriver:** Railway'de ChromeDriver otomatik kurulur, ama sorun yaşarsanız `nixpacks.toml` dosyası ekleyebilirsiniz.

#### E. Public URL Al
1. **Settings** → **Networking** sekmesine gidin
2. **Generate Domain** butonuna tıklayın
3. Backend URL'inizi kopyalayın (örn: `https://stok-backend.railway.app`)
4. Bu URL'i not edin, frontend'de kullanacağız

### 2️⃣ Frontend'i Vercel'e Deploy Et

#### A. Vercel Hesabı Oluştur
1. https://vercel.com/ adresine gidin
2. GitHub ile giriş yapın

#### B. Proje Oluştur
1. "Add New..." → "Project" seçin
2. GitHub repository'nizi seçin
3. **Import Project** butonuna tıklayın

#### C. Build Ayarları
Vercel otomatik olarak algılayacak, ama kontrol edin:

- **Framework Preset:** Vite
- **Root Directory:** `frontend` ⚠️ ÖNEMLİ: Root directory'yi `frontend` olarak ayarlayın!
- **Build Command:** `npm run build` (otomatik algılanır)
- **Output Directory:** `dist` (otomatik algılanır)
- **Install Command:** `npm install` (otomatik algılanır)

#### D. Environment Variables Ekle
**Environment Variables** sekmesine gidin ve ekleyin:

```
VITE_API_URL=https://your-backend-url.railway.app/api
```

⚠️ **ÖNEMLİ:** `your-backend-url.railway.app` yerine Railway'den aldığınız gerçek URL'i yazın!

#### E. Deploy
1. **Deploy** butonuna tıklayın
2. Birkaç dakika bekleyin
3. Frontend URL'inizi alın (örn: `https://stok-takip.vercel.app`)

### 3️⃣ CORS Ayarları (Backend)

Backend'de CORS zaten ayarlı, ama Railway URL'inizi kontrol edin:

```python
# backend/app.py
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

Bu ayar tüm origin'lere izin veriyor, güvenlik için sadece Vercel URL'inizi ekleyebilirsiniz:

```python
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://your-frontend.vercel.app",
            "http://localhost:3000"  # Development için
        ]
    }
})
```

## ✅ Test

### 1. Frontend'i Açın
- Vercel URL'inize gidin
- Kayıt olun / Giriş yapın

### 2. Backend'i Test Edin
- Frontend'den ürün ekleyin
- Backend log'larını Railway'de kontrol edin

### 3. Email Bildirimlerini Test Edin
- Email ayarlarınızı yapılandırın
- Stokta olan bir ürün ekleyin
- Email bildirimi gelmeli

## 🔧 Sorun Giderme

### Frontend API'ye bağlanamıyor
1. `VITE_API_URL` environment variable'ını kontrol edin
2. Backend URL'inin doğru olduğundan emin olun
3. Backend'in çalıştığından emin olun (Railway log'larını kontrol edin)

### CORS Hatası
1. Backend'de CORS ayarlarını kontrol edin
2. Vercel URL'inizi CORS origins'e ekleyin

### Database Hatası
1. Railway'de `DATABASE_PATH` environment variable'ını kontrol edin
2. Railway persistent storage kullanıyor mu kontrol edin

### Selenium/ChromeDriver Hatası
1. Railway'de ChromeDriver otomatik kurulur
2. Sorun yaşarsanız `backend/nixpacks.toml` dosyasını kontrol edin
3. Railway log'larında ChromeDriver kurulum mesajlarını kontrol edin

### Email Gönderilmiyor
1. Kullanıcının email ayarlarını kontrol edin
2. Gmail için Uygulama Şifresi kullanıldığından emin olun
3. Railway log'larını kontrol edin

## 📝 Önemli Notlar

### Railway (Backend)
- ✅ Ücretsiz tier: $5 kredi/ay
- ✅ Otomatik deploy (GitHub push ile)
- ✅ SQLite desteği
- ✅ 7/24 çalışır

### Vercel (Frontend)
- ✅ Ücretsiz tier (sınırsız)
- ✅ Otomatik deploy (GitHub push ile)
- ✅ CDN desteği
- ✅ Hızlı ve güvenilir

## 🔄 Güncelleme

Her GitHub push'ta:
- ✅ Backend otomatik deploy olur (Railway)
- ✅ Frontend otomatik deploy olur (Vercel)
- ✅ Manuel işlem gerekmez

## 🎯 Sonuç

Artık uygulamanız:
- ✅ 7/24 çalışıyor
- ✅ Her kullanıcı kendi oturumunu kullanıyor
- ✅ Veriler karışmıyor
- ✅ Email bildirimleri çalışıyor
- ✅ Bilgisayarınızı açık tutmanıza gerek yok

## 📞 Destek

Sorun yaşarsanız:
1. Railway log'larını kontrol edin
2. Vercel build log'larını kontrol edin
3. Browser console'u kontrol edin
4. Network tab'ını kontrol edin (API istekleri)
