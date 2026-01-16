# 🔑 GitHub Token Sorunu Çözümü

403 hatası alıyorsanız, token'ınızın yeterli izinlere sahip olmadığı anlamına gelir.

## ✅ Çözüm: Yeni Token Oluştur

### 1. GitHub'da Yeni Token Oluştur

1. https://github.com/settings/tokens adresine gidin
2. **"Generate new token"** → **"Generate new token (classic)"** tıklayın
3. **Note**: `stok-takip-push` yazın
4. **Expiration**: 90 days (veya istediğiniz süre)
5. **Scopes**: Aşağıdaki seçenekleri işaretleyin:
   - ✅ **repo** (tüm repo izinleri) - **ÖNEMLİ!**
   - ✅ **workflow** (opsiyonel)
6. **"Generate token"** butonuna tıklayın
7. Token'ı kopyalayın (bir daha gösterilmeyecek!)

### 2. Token ile Push Yap

```bash
cd /Users/ranacetinkaya/stok

# Token'ı URL'ye ekleyin (YENİ_TOKEN yerine yeni token'ınızı yazın)
git remote set-url origin https://YENİ_TOKEN@github.com/ranacetinkaya/stok.git

# Push yapın
git push -u origin main
```

### 3. Güvenlik için Remote'u Temizle

Push başarılı olduktan sonra:

```bash
# Token'ı remote URL'den kaldır
git remote set-url origin https://github.com/ranacetinkaya/stok.git

# Credential helper kullan (bir sonraki push için)
git config --global credential.helper osxkeychain  # macOS için
```

## 🔄 Alternatif: SSH Kullan

SSH key'iniz varsa:

```bash
cd /Users/ranacetinkaya/stok

# Remote'u SSH'ye çevir
git remote set-url origin git@github.com:ranacetinkaya/stok.git

# Push yap
git push -u origin main
```

SSH key yoksa:
1. https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
2. SSH key oluşturun ve GitHub'a ekleyin

## ⚠️ Önemli Notlar

- Token'ı asla commit etmeyin!
- Token'ı paylaşmayın!
- Token süresi dolduğunda yeniden oluşturun
