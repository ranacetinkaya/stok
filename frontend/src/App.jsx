import React, { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

const API_BASE =
  (import.meta.env.VITE_API_URL || "http://localhost:5001").replace(/\/$/, "");
const API_URL = `${API_BASE}/api`;


function App() {
  const [kullanici, setKullanici] = useState(null)
  const [kullaniciId, setKullaniciId] = useState(null)
  const [urunler, setUrunler] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [showEmailAyarlari, setShowEmailAyarlari] = useState(false)
  const [urunUrl, setUrunUrl] = useState('')
  const [takipEdilenBeden, setTakipEdilenBeden] = useState('')
  const [adding, setAdding] = useState(false)
  const [email, setEmail] = useState('')
  const [isim, setIsim] = useState('')
  const [emailAyarlari, setEmailAyarlari] = useState({
    smtp_server: 'smtp.gmail.com',
    smtp_port: 587,
    email_user: '',
    email_password: ''
  })

  useEffect(() => {
    // LocalStorage'dan kullanıcı ID'sini al
    const savedKullaniciId = localStorage.getItem('kullanici_id')
    if (savedKullaniciId) {
      setKullaniciId(parseInt(savedKullaniciId))
      fetchKullanici(parseInt(savedKullaniciId))
      fetchUrunler(parseInt(savedKullaniciId))
    } else {
      setLoading(false)
    }
  }, [])

  const fetchKullanici = async (id) => {
    try {
      const response = await axios.get(`${API_URL}/kullanicilar/${id}`)
      if (response.data.success) {
        setKullanici(response.data)
        setEmailAyarlari({
          smtp_server: response.data.smtp_server || 'smtp.gmail.com',
          smtp_port: response.data.smtp_port || 587,
          email_user: response.data.email_user || '',
          email_password: ''
        })
      }
    } catch (error) {
      console.error('Kullanıcı bilgileri yüklenirken hata:', error)
    }
  }

  const fetchUrunler = async (kullaniciId) => {
    if (!kullaniciId) return
    
    try {
      const response = await axios.get(`${API_URL}/urunler?kullanici_id=${kullaniciId}`)
      setUrunler(response.data)
      setLoading(false)
    } catch (error) {
      console.error('Ürünler yüklenirken hata:', error)
      setLoading(false)
    }
  }

  const handleKayitOl = async (e) => {
    e.preventDefault()
    if (!email.trim()) {
      alert('Lütfen email adresinizi girin')
      return
    }

    try {
      const response = await axios.post(`${API_URL}/kullanicilar`, {
        email: email.trim().toLowerCase(),
        isim: isim.trim()
      })
      
      if (response.data.success) {
        const id = response.data.id
        setKullaniciId(id)
        setKullanici(response.data)
        localStorage.setItem('kullanici_id', id.toString())
        localStorage.setItem('kullanici_email', response.data.email)
        alert(`✅ Hoş geldiniz! Email ayarlarınızı yapılandırın.`)
        setShowEmailAyarlari(true)
        fetchUrunler(id)
      }
    } catch (error) {
      alert(error.response?.data?.error || 'Kayıt olurken hata oluştu')
    }
  }

  const handleEmailAyarlariKaydet = async (e) => {
    e.preventDefault()
    if (!kullaniciId) return

    try {
      const response = await axios.put(`${API_URL}/kullanicilar/${kullaniciId}/email-ayarlari`, emailAyarlari)
      if (response.data.success) {
        alert('✅ Email ayarları kaydedildi! Artık stok geldiğinde bildirim alacaksınız.')
        setShowEmailAyarlari(false)
        fetchKullanici(kullaniciId)
      }
    } catch (error) {
      alert(error.response?.data?.error || 'Email ayarları kaydedilirken hata oluştu')
    }
  }

  const handleAddUrun = async (e) => {
    e.preventDefault()
    if (!kullaniciId) {
      alert('Lütfen önce giriş yapın')
      return
    }
    
    if (!urunUrl.trim()) {
      alert('Lütfen Bershka ürün URL\'si girin')
      return
    }

    setAdding(true)
    try {
      const response = await axios.post(`${API_URL}/urunler`, {
        urun_url: urunUrl,
        kullanici_id: kullaniciId,
        takip_edilen_beden: takipEdilenBeden.trim() || null
      })
      if (response.data.success) {
        const stokDurumu = response.data.stok_durumu
        let mesaj = `✅ Ürün eklendi!`
        if (stokDurumu === 'stokta_var') {
          mesaj += '\n🎉 Stokta Var - Sürekli kontrol devam ediyor'
        } else if (stokDurumu === 'hata') {
          mesaj += '\n⚠️ İlk stok kontrolü yapılamadı ama sürekli kontrol başlatıldı'
        } else {
          mesaj += '\n⏳ Stokta Yok - Stok geldiğinde bildirim alacaksınız'
        }
        alert(mesaj)
        setUrunUrl('')
        setTakipEdilenBeden('')
        setShowForm(false)
        fetchUrunler(kullaniciId)
      } else {
        alert(response.data.error || 'Ürün eklenirken hata oluştu')
      }
    } catch (error) {
      console.error('Hata detayı:', error)
      const errorMessage = error.response?.data?.error || error.message || 'Ürün eklenirken hata oluştu'
      alert(`❌ Hata: ${errorMessage}`)
    } finally {
      setAdding(false)
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Bu ürünü takip listesinden çıkarmak istediğinize emin misiniz?')) {
      try {
        const response = await axios.delete(`${API_URL}/urunler/${id}?kullanici_id=${kullaniciId}`)
        if (response.data.success) {
          alert('✅ Ürün başarıyla silindi ve veritabanından kaldırıldı')
          fetchUrunler(kullaniciId)
        } else {
          alert(response.data.error || 'Silme işlemi başarısız')
        }
      } catch (error) {
        alert(error.response?.data?.error || 'Silme işlemi başarısız')
      }
    }
  }

  const handleManualCheck = async (id) => {
    try {
      const response = await axios.post(`${API_URL}/stok-kontrol`, { 
        urun_id: id,
        kullanici_id: kullaniciId
      })
      alert(`Stok durumu: ${response.data.stok_durumu === 'stokta_var' ? '✅ Stokta Var' : '❌ Stokta Yok'}`)
      fetchUrunler(kullaniciId)
    } catch (error) {
      alert('Stok kontrolü başarısız')
    }
  }

  const handleCheckAll = async () => {
    if (window.confirm('Tüm ürünlerin stok durumunu kontrol etmek istediğinize emin misiniz?')) {
      try {
        await axios.post(`${API_URL}/stok-kontrol`, {
          kullanici_id: kullaniciId
        })
        alert('Tüm ürünler kontrol edildi! Sonuçlar güncelleniyor...')
        setTimeout(() => fetchUrunler(kullaniciId), 2000)
      } catch (error) {
        alert('Stok kontrolü başarısız')
      }
    }
  }

  const getStokDurumuBadge = (durum) => {
    switch (durum) {
      case 'stokta_var':
        return { text: '✅ Stokta Var', class: 'stok-var', emoji: '🎉' }
      case 'stokta_yok':
        return { text: '❌ Stokta Yok', class: 'stok-yok', emoji: '⏳' }
      case 'hata':
        return { text: '⚠️ Kontrol Edilemedi', class: 'stok-hata', emoji: '⚠️' }
      default:
        return { text: '❓ Bilinmiyor', class: 'stok-bilinmiyor', emoji: '❓' }
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Henüz kontrol edilmedi'
    const date = new Date(dateString)
    return date.toLocaleString('tr-TR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return <div className="loading">Yükleniyor...</div>
  }

  // Kullanıcı girişi yapılmamışsa
  if (!kullaniciId) {
    return (
      <div className="app">
        <div className="container">
          <header>
            <h1>🛍️ Bershka Otomatik Stok Takip</h1>
            <p>Ürün URL'lerini ekleyin, stok geldiğinde otomatik bildirim alın</p>
          </header>

          <div className="form-container">
            <h2>Giriş Yap / Kayıt Ol</h2>
            <form onSubmit={handleKayitOl}>
              <div className="form-group">
                <label>Email Adresiniz *</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="ornek@gmail.com"
                  required
                />
                <small className="form-help">
                  Bu email adresine stok bildirimleri gönderilecek
                </small>
              </div>
              <div className="form-group">
                <label>İsim (Opsiyonel)</label>
                <input
                  type="text"
                  value={isim}
                  onChange={(e) => setIsim(e.target.value)}
                  placeholder="Adınız"
                />
              </div>
              <button type="submit" className="btn btn-primary">
                Giriş Yap / Kayıt Ol
              </button>
            </form>
          </div>
        </div>
      </div>
    )
  }

  // Ana uygulama
  return (
    <div className="app">
      <div className="container">
        <header>
          <h1>🛍️ Bershka Otomatik Stok Takip</h1>
          <p>Hoş geldiniz, {kullanici?.isim || kullanici?.email}!</p>
          <div className="user-info">
            <span>📧 {kullanici?.email}</span>
            <button 
              className="btn btn-small btn-secondary"
              onClick={() => setShowEmailAyarlari(!showEmailAyarlari)}
            >
              {showEmailAyarlari ? '✖️ Kapat' : '⚙️ Email Ayarları'}
            </button>
          </div>
        </header>

        {showEmailAyarlari && (
          <div className="form-container">
            <h2>📧 Email Bildirim Ayarları</h2>
            <form onSubmit={handleEmailAyarlariKaydet}>
              <div className="form-group">
                <label>SMTP Sunucusu</label>
                <input
                  type="text"
                  value={emailAyarlari.smtp_server}
                  onChange={(e) => setEmailAyarlari({...emailAyarlari, smtp_server: e.target.value})}
                  placeholder="smtp.gmail.com"
                />
              </div>
              <div className="form-group">
                <label>SMTP Port</label>
                <input
                  type="number"
                  value={emailAyarlari.smtp_port}
                  onChange={(e) => setEmailAyarlari({...emailAyarlari, smtp_port: parseInt(e.target.value)})}
                  placeholder="587"
                />
              </div>
              <div className="form-group">
                <label>Email Adresi (Gönderen) *</label>
                <input
                  type="email"
                  value={emailAyarlari.email_user}
                  onChange={(e) => setEmailAyarlari({...emailAyarlari, email_user: e.target.value})}
                  placeholder="your-email@gmail.com"
                  required
                />
              </div>
              <div className="form-group">
                <label>Email Şifresi (Uygulama Şifresi) *</label>
                <input
                  type="password"
                  value={emailAyarlari.email_password}
                  onChange={(e) => setEmailAyarlari({...emailAyarlari, email_password: e.target.value})}
                  placeholder="Gmail için Uygulama Şifresi"
                  required
                />
                <small className="form-help">
                  Gmail kullanıyorsanız, normal şifreniz yerine <strong>Uygulama Şifresi</strong> kullanın.
                  <br />Google Hesabınız → Güvenlik → 2 Adımlı Doğrulama → Uygulama Şifreleri
                </small>
              </div>
              <div className="form-actions">
                <button type="submit" className="btn btn-success">
                  💾 Kaydet
                </button>
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={() => setShowEmailAyarlari(false)}
                >
                  İptal
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="actions">
          <button 
            className="btn btn-primary" 
            onClick={() => setShowForm(!showForm)}
          >
            {showForm ? '✖️ İptal' : '➕ Yeni Ürün Ekle'}
          </button>
          {urunler.length > 0 && (
            <button 
              className="btn btn-secondary" 
              onClick={handleCheckAll}
            >
              🔍 Tümünü Kontrol Et
            </button>
          )}
        </div>

        {showForm && (
          <div className="form-container">
            <h2>Yeni Ürün Ekle</h2>
            <form onSubmit={handleAddUrun}>
              <div className="form-group">
                <label>Bershka Ürün URL'si *</label>
                <input
                  type="url"
                  value={urunUrl}
                  onChange={(e) => setUrunUrl(e.target.value)}
                  placeholder="https://www.bershka.com/tr/..."
                  required
                  disabled={adding}
                />
                <small className="form-help">
                  Bershka web sitesinden ürün sayfasının URL'sini kopyalayıp yapıştırın
                </small>
              </div>
              <div className="form-group">
                <label>Takip Edilecek Beden (Opsiyonel)</label>
                <select
                  value={takipEdilenBeden}
                  onChange={(e) => setTakipEdilenBeden(e.target.value)}
                  disabled={adding}
                >
                  <option value="">Tüm Bedenler (Varsayılan)</option>
                  <optgroup label="Harf Bedenleri">
                    <option value="XXS">XXS - Extra Extra Small</option>
                    <option value="XS">XS - Extra Small</option>
                    <option value="S">S - Small</option>
                    <option value="M">M - Medium</option>
                    <option value="L">L - Large</option>
                    <option value="XL">XL - Extra Large</option>
                    <option value="XXL">XXL - Extra Extra Large</option>
                  </optgroup>
                  <optgroup label="Sayısal Bedenler">
                    <option value="32">32</option>
                    <option value="34">34</option>
                    <option value="36">36</option>
                    <option value="38">38</option>
                    <option value="40">40</option>
                    <option value="42">42</option>
                    <option value="44">44</option>
                    <option value="46">46</option>
                    <option value="48">48</option>
                  </optgroup>
                </select>
                <small className="form-help">
                  Belirli bir bedenin stok durumunu takip etmek istiyorsanız seçin. Boş bırakırsanız tüm bedenler kontrol edilir.
                </small>
              </div>
              <div className="form-actions">
                <button 
                  type="submit" 
                  className="btn btn-success"
                  disabled={adding}
                >
                  {adding ? '⏳ Ekleniyor...' : '➕ Ekle ve Kontrol Et'}
                </button>
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={() => {
                    setShowForm(false)
                    setUrunUrl('')
                  }}
                  disabled={adding}
                >
                  İptal
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="urunler-listesi">
          <h2>Takip Edilen Ürünler ({urunler.length})</h2>
          {urunler.length === 0 ? (
            <div className="empty-state">
              <p>Henüz ürün eklenmemiş.</p>
              <p>Bershka'dan beğendiğiniz ürünün URL'sini ekleyerek stok takibine başlayın!</p>
            </div>
          ) : (
            <div className="urun-grid">
              {urunler.map((urun) => {
                const stokBadge = getStokDurumuBadge(urun.stok_durumu)
                return (
                  <div key={urun.id} className="urun-kart">
                    <div className="urun-header">
                      <h3>{urun.urun_adi || 'Ürün adı yükleniyor...'}</h3>
                      {urun.takip_edilen_beden && (
                        <span className="badge badge-info">👕 {urun.takip_edilen_beden}</span>
                      )}
                      {urun.bildirim_gonderildi && urun.stok_durumu === 'stokta_var' && (
                        <span className="badge badge-success">📧 Bildirim Gönderildi</span>
                      )}
                    </div>
                    <div className="urun-body">
                      <div className="urun-info">
                        <p className={`stok-durumu ${stokBadge.class}`}>
                          {stokBadge.emoji} {stokBadge.text}
                        </p>
                        <p className="urun-url">
                          <a href={urun.urun_url} target="_blank" rel="noopener noreferrer">
                            🔗 Ürün Sayfasına Git
                          </a>
                        </p>
                        <p className="kontrol-tarihi">
                          <strong>Son Kontrol:</strong> {formatDate(urun.son_kontrol_tarihi)}
                        </p>
                      </div>
                    </div>
                    <div className="urun-footer">
                      <button
                        className="btn btn-small btn-primary"
                        onClick={() => handleManualCheck(urun.id)}
                      >
                        🔍 Şimdi Kontrol Et
                      </button>
                      <button
                        className="btn btn-small btn-danger"
                        onClick={() => handleDelete(urun.id)}
                      >
                        🗑️ Kaldır
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        <div className="info-box">
          <h3>ℹ️ Nasıl Çalışır?</h3>
          <ul>
            <li>✅ Bershka ürün sayfasının URL'sini ekleyin</li>
            <li>⚡ <strong>ANINDA KONTROL:</strong> Her ürün için sürekli kontrol (her 15 saniyede bir)</li>
            <li>🎉 Stok geldiğinde <strong>ANINDA</strong> email bildirimi gönderilir</li>
            <li>📧 Email ayarlarınızı yapılandırmayı unutmayın!</li>
            <li>🔍 İstediğiniz zaman manuel kontrol de yapabilirsiniz</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default App
