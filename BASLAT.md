# 🚀 Uygulamayı Başlatma Rehberi

## 1️⃣ Backend'i Başlatın

### Terminal 1'de (Backend için):

```bash
cd backend
source venv/bin/activate
python app.py
```

Backend `http://localhost:5000` adresinde çalışacak.

**Başarılı mesaj:**
```
🚀 Stok Takip Sistemi başlatılıyor...
📧 Email bildirimleri için .env dosyasını yapılandırın
 * Running on http://127.0.0.1:5000
```

## 2️⃣ Frontend'i Kurun ve Başlatın

### Yeni bir Terminal açın (Terminal 2):

```bash
cd frontend
npm install
npm run dev
```

Frontend `http://localhost:3000` adresinde açılacak.

## 3️⃣ Tarayıcıda Açın

- Frontend otomatik olarak açılır
- Veya manuel olarak: `http://localhost:3000`

## 📧 Email Bildirimi Ayarları (Opsiyonel)

Email bildirimlerini aktif etmek için:

```bash
cd backend
cp ../env.example .env
```

Sonra `.env` dosyasını düzenleyip email bilgilerinizi girin.

## ✅ Hazır!

Artık stok takip uygulamanızı kullanabilirsiniz:
- Ürün ekleyin
- Stok durumunu takip edin
- Stok geldiğinde otomatik bildirim alın
