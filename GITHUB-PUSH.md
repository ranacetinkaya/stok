# 📤 GitHub'a Push Rehberi

## 1️⃣ GitHub'da Repository Oluştur

1. https://github.com/new adresine gidin
2. **Repository name**: `bershka-stok-takip` (veya istediğiniz ad)
3. **Description**: "Multi-user Bershka stok takip uygulaması"
4. **Public** veya **Private** seçin
5. ⚠️ **"Initialize this repository with a README" seçeneğini İŞARETLEMEYİN**
6. **"Create repository"** butonuna tıklayın

## 2️⃣ Terminal'de Push Yap

Repository oluşturduktan sonra GitHub size şu komutları gösterecek. Aşağıdaki komutları çalıştırın:

```bash
cd /Users/ranacetinkaya/stok

# GitHub'dan aldığınız URL'i kullanın (örnek):
git remote add origin https://github.com/KULLANICI_ADI/bershka-stok-takip.git

# Veya SSH kullanıyorsanız:
# git remote add origin git@github.com:KULLANICI_ADI/bershka-stok-takip.git

# Branch'i main olarak ayarlayın
git branch -M main

# Push yapın
git push -u origin main
```

## 3️⃣ GitHub Credentials

İlk push'ta GitHub kullanıcı adı ve şifre (veya Personal Access Token) isteyebilir.

### Personal Access Token (Önerilen)

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token" → "Generate new token (classic)"
3. **Note**: "stok-takip-push"
4. **Expiration**: 90 days (veya istediğiniz süre)
5. **Scopes**: `repo` seçeneğini işaretleyin
6. "Generate token" butonuna tıklayın
7. Token'ı kopyalayın (bir daha gösterilmeyecek!)
8. Push yaparken şifre yerine bu token'ı kullanın

## ✅ Kontrol

Push başarılı olduktan sonra:
- GitHub repository sayfanızı yenileyin
- Tüm dosyaların yüklendiğini görün
- Artık Railway ve Vercel'de bu repository'yi kullanabilirsiniz!

## 🔄 Sonraki Adımlar

1. **Railway Deploy**: [VERCEL-DEPLOY.md](./VERCEL-DEPLOY.md) dosyasındaki adımları takip edin
2. **Vercel Deploy**: Frontend'i Vercel'e deploy edin
3. **Test**: Uygulamayı test edin
