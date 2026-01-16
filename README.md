# 🛍️ Bershka Otomatik Stok Takip Sistemi

Multi-user Bershka stok takip uygulaması. Ürünlerin stok durumunu otomatik kontrol eder ve stok geldiğinde anında email bildirimi gönderir.

## ✨ Özellikler

- ✅ **Multi-User Desteği**: Her kullanıcının kendi oturumu, ürün listesi ve email ayarları
- ✅ **Anında Bildirim**: Stok geldiğinde 5 saniye içinde email bildirimi
- ✅ **Beden Takibi**: Belirli bedenlerin stok durumunu takip edebilirsiniz
- ✅ **7/24 Çalışır**: Deploy edildiğinde sürekli çalışır
- ✅ **Otomatik Kontrol**: Her 5 saniyede bir otomatik stok kontrolü

## 🚀 Hızlı Başlangıç

### Local Development

#### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Deploy

Detaylı deploy rehberi için:
- **Vercel + Railway**: [VERCEL-DEPLOY.md](./VERCEL-DEPLOY.md)
- **Genel Deploy**: [DEPLOY.md](./DEPLOY.md)

## 📋 Kullanım

1. **Kayıt Ol / Giriş Yap**: Email adresinizle kayıt olun
2. **Email Ayarları**: Email bildirimleri için SMTP ayarlarınızı yapın
3. **Ürün Ekle**: Bershka ürün URL'sini ekleyin
4. **Beden Seç**: İsterseniz belirli bir beden takip edin
5. **Bekle**: Stok geldiğinde otomatik email alacaksınız!

## 🛠️ Teknolojiler

- **Backend**: Python, Flask, SQLite, Selenium
- **Frontend**: React, Vite, Axios
- **Deploy**: Vercel (Frontend), Railway (Backend)

## 📧 Email Ayarları

Gmail kullanıyorsanız:
1. Google Hesabınız → Güvenlik
2. 2 Adımlı Doğrulama → Açık olmalı
3. Uygulama Şifreleri → Yeni şifre oluştur
4. Bu şifreyi email ayarlarında kullanın

## 🔒 Güvenlik

- Her kullanıcı sadece kendi verilerini görür
- Email şifreleri güvenli şekilde saklanır
- CORS ayarları production için yapılandırılmıştır

## 📝 Lisans

Bu proje kişisel kullanım içindir.

## 🤝 Katkıda Bulunma

Sorun bildirmek veya öneride bulunmak için GitHub Issues kullanın.
