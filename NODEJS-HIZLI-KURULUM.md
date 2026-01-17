# 🚀 Node.js Hızlı Kurulum (macOS)

## ⚠️ Node.js Henüz Yüklü Değil

Node.js'i yüklemeniz gerekiyor. İşte en kolay yöntem:

## 📥 Adım 1: Node.js İndirin

1. **Tarayıcıda şu adrese gidin:**
   ```
   https://nodejs.org/
   ```

2. **"LTS" (Long Term Support) butonuna tıklayın**
   - Yeşil renkli büyük buton
   - Örnek: "Download Node.js (LTS)" veya "v20.x.x LTS"

3. **macOS için otomatik olarak `.pkg` dosyası indirilecek**
   - Downloads klasörünüze kaydedilecek

## 🔧 Adım 2: Kurulumu Yapın

1. **Finder'ı açın ve Downloads klasörüne gidin**

2. **İndirilen `.pkg` dosyasını bulun**
   - İsim: `node-vXX.X.X.pkg` gibi bir şey olacak

3. **Dosyaya çift tıklayın**
   - Kurulum sihirbazı açılacak

4. **Kurulum adımlarını takip edin:**
   - "Continue" butonlarına tıklayın
   - Lisans sözleşmesini kabul edin
   - Kurulum konumunu seçin (varsayılanı bırakın)
   - Admin şifrenizi girin
   - Kurulum tamamlanınca "Close" butonuna tıklayın

## ✅ Adım 3: Terminal'i Yenileyin

**ÖNEMLİ:** Kurulumdan sonra terminal'i yenilemeniz gerekiyor:

### Yöntem 1: Yeni Terminal Açın (Önerilen)
- Mevcut terminal penceresini kapatın
- Yeni bir terminal penceresi açın (Cmd + Space, "Terminal" yazın)

### Yöntem 2: PATH'i Güncelleyin
```bash
export PATH="/usr/local/bin:$PATH"
```

## 🧪 Adım 4: Kurulumu Test Edin

Yeni terminal'de şu komutları çalıştırın:

```bash
node --version
npm --version
```

**Başarılı olursa şöyle bir çıktı göreceksiniz:**
```
v20.10.0
10.2.3
```

## 🎯 Adım 5: Frontend'i Kurun

Node.js yüklendikten sonra:

```bash
cd frontend
npm install
npm run dev
```

## 🆘 Sorun Giderme

**Hala "command not found" hatası alıyorsanız:**

1. Terminal'i tamamen kapatıp yeniden açın
2. Şu komutu çalıştırın:
   ```bash
   export PATH="/usr/local/bin:$PATH"
   node --version
   ```

**Kurulum dosyası bulamıyorsanız:**
- Tarayıcının Downloads klasörünü kontrol edin
- Veya tekrar https://nodejs.org/ adresinden indirin

**Kurulum sırasında hata alıyorsanız:**
- Admin şifrenizi doğru girdiğinizden emin olun
- Sistem Tercihleri > Güvenlik'te izinleri kontrol edin
