from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import threading
import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
import time
import re

app = Flask(__name__)
CORS(app)

# Scheduler başlatma
scheduler = BackgroundScheduler()
scheduler.start()

# Veritabanı başlatma
def init_db():
    conn = sqlite3.connect('stok.db')
    c = conn.cursor()
    
    # Kullanıcılar tablosu
    c.execute('''CREATE TABLE IF NOT EXISTS kullanicilar
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT UNIQUE NOT NULL,
                  isim TEXT,
                  smtp_server TEXT DEFAULT 'smtp.gmail.com',
                  smtp_port INTEGER DEFAULT 587,
                  email_user TEXT,
                  email_password TEXT,
                  olusturma_tarihi TEXT)''')
    
    # Eski ürünler tablosunu kontrol et
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='urunler'")
    table_exists = c.fetchone()
    
    if table_exists:
        # Tablo var, sütunları kontrol et
        c.execute("PRAGMA table_info(urunler)")
        columns = [row[1] for row in c.fetchall()]
        
        # takip_edilen_beden sütunu yoksa ekle
        if 'takip_edilen_beden' not in columns:
            print("⚠️ 'takip_edilen_beden' sütunu ekleniyor...")
            try:
                c.execute("ALTER TABLE urunler ADD COLUMN takip_edilen_beden TEXT")
                conn.commit()
                print("✅ 'takip_edilen_beden' sütunu eklendi")
            except Exception as e:
                print(f"⚠️ Sütun eklenirken hata: {str(e)}")
        
        # Eski yapıdan yeni yapıya migration
        if 'kullanici_id' not in columns:
            print("⚠️ Veritabanı migration yapılıyor...")
            try:
                # Geçici tablo oluştur
                c.execute('''CREATE TABLE urunler_new
                             (id INTEGER PRIMARY KEY AUTOINCREMENT,
                              kullanici_id INTEGER NOT NULL DEFAULT 1,
                              urun_url TEXT NOT NULL,
                              urun_adi TEXT,
                              urun_kodu TEXT,
                              takip_edilen_beden TEXT,
                              stok_durumu TEXT DEFAULT 'stokta_yok',
                              bildirim_gonderildi INTEGER DEFAULT 0,
                              son_kontrol_tarihi TEXT,
                              olusturma_tarihi TEXT,
                              guncelleme_tarihi TEXT)''')
                
                # Eski verileri yeni tabloya kopyala
                if 'urun_url' in columns:
                    # Yeni yapı
                    c.execute('SELECT * FROM urunler')
                    old_data = c.fetchall()
                    for row in old_data:
                        # Eski yapı: id, urun_url, urun_adi, urun_kodu, stok_durumu, bildirim_gonderildi, son_kontrol_tarihi, olusturma_tarihi, guncelleme_tarihi
                        # Yeni yapı: id, kullanici_id, urun_url, urun_adi, urun_kodu, stok_durumu, bildirim_gonderildi, son_kontrol_tarihi, olusturma_tarihi, guncelleme_tarihi
                        if len(row) >= 9:
                            c.execute('''INSERT INTO urunler_new 
                                        (kullanici_id, urun_url, urun_adi, urun_kodu, takip_edilen_beden, stok_durumu, bildirim_gonderildi, 
                                         son_kontrol_tarihi, olusturma_tarihi, guncelleme_tarihi)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                    (1, row[1], row[2], row[3] if len(row) > 3 else None, None,
                                     row[4] if len(row) > 4 else 'stokta_yok',
                                     row[5] if len(row) > 5 else 0,
                                     row[6] if len(row) > 6 else None,
                                     row[7] if len(row) > 7 else None,
                                     row[8] if len(row) > 8 else None))
                
                # Eski tabloyu sil ve yenisini yeniden adlandır
                c.execute('DROP TABLE urunler')
                c.execute('ALTER TABLE urunler_new RENAME TO urunler')
                
                # Varsayılan kullanıcı oluştur (eski veriler için)
                c.execute('SELECT id FROM kullanicilar WHERE email = ?', ('default@example.com',))
                if not c.fetchone():
                    c.execute('''INSERT INTO kullanicilar (email, isim, olusturma_tarihi)
                                VALUES (?, ?, ?)''', 
                            ('default@example.com', 'Varsayılan Kullanıcı', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                
                print("✅ Migration tamamlandı")
            except Exception as e:
                print(f"⚠️ Migration hatası: {str(e)}")
                # Hata olursa yeni tabloyu oluştur
                c.execute('DROP TABLE IF EXISTS urunler')
                table_exists = False
    
    if not table_exists:
        # Yeni tablo oluştur
        c.execute('''CREATE TABLE urunler
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      kullanici_id INTEGER NOT NULL,
                      urun_url TEXT NOT NULL,
                      urun_adi TEXT,
                      urun_kodu TEXT,
                      stok_durumu TEXT DEFAULT 'stokta_yok',
                      bildirim_gonderildi INTEGER DEFAULT 0,
                      son_kontrol_tarihi TEXT,
                      olusturma_tarihi TEXT,
                      guncelleme_tarihi TEXT,
                      UNIQUE(kullanici_id, urun_url))''')
    
    conn.commit()
    conn.close()
    print("✅ Veritabanı hazır")

# Bershka web scraping fonksiyonu
def check_bershka_stock(product_url, beden=None):
    """
    Bershka ürün sayfasından stok durumunu kontrol eder
    beden: Takip edilecek beden (örn: 'S', 'M', 'L', 'Small', 'Medium', 'Large', None=tüm bedenler)
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.bershka.com/',
        }
        
        # URL'den ürün ID'sini çıkar (c0p204066773 gibi)
        import re
        product_id_match = re.search(r'c0p(\d+)', product_url)
        product_id = product_id_match.group(1) if product_id_match else None
        
        # Önce API endpoint'ini deneyelim
        if product_id:
            try:
                # Bershka API endpoint'i (tahmin)
                api_url = f'https://www.bershka.com/tr/api/product/{product_id}'
                api_response = requests.get(api_url, headers=headers, timeout=10)
                if api_response.status_code == 200:
                    try:
                        api_data = api_response.json()
                        if 'availability' in api_data or 'stock' in api_data:
                            stok_durumu = 'stokta_var' if api_data.get('availability', {}).get('available', False) else 'stokta_yok'
                            urun_adi = api_data.get('name', 'Bilinmeyen Ürün')
                            return {
                                'stok_durumu': stok_durumu,
                                'urun_adi': urun_adi,
                                'success': True
                            }
                    except:
                        pass
            except:
                pass
        
        # API çalışmazsa normal scraping yap
        response = requests.get(product_url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        # Sayfa içeriğini kontrol et
        content = response.text
        
        # Eğer sayfa çok küçükse (bot koruması), Selenium kullan
        if len(content) < 5000:
            print("⚠️ Sayfa JavaScript ile yükleniyor, Selenium ile kontrol ediliyor...")
            return check_bershka_stock_selenium(product_url, beden=beden)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Bershka stok durumunu kontrol et - farklı olasılıklar
        # Varsayılan: Stokta yok (güvenli yaklaşım - sadece kesin işaretler görürsek stokta var deriz)
        stok_durumu = 'stokta_yok'  # Varsayılan olarak stokta yok kabul et
        urun_adi = ''
        
        # Ürün adını bul
        title_tag = soup.find('h1') or soup.find('title')
        if title_tag:
            urun_adi = title_tag.get_text(strip=True)
        
        # Sayfa içeriğinde stok durumu ipuçları ara
        page_text = soup.get_text().lower()
        page_html = str(soup).lower()
        
        # 1. "Out of stock" veya "Stokta yok" mesajı - KESIN STOKTA YOK
        out_of_stock_patterns = [
            r'out of stock',
            r'stokta yok',
            r'tükendi',
            r'stok yok',
            r'not available',
            r'unavailable',
            r'no longer available',
            r'agotado',
            r'stokta değil'
        ]
        for pattern in out_of_stock_patterns:
            if re.search(pattern, page_text, re.I) or re.search(pattern, page_html, re.I):
                stok_durumu = 'stokta_yok'
                print(f"  ❌ Stokta yok tespit edildi: {pattern}")
                return {
                    'stok_durumu': 'stokta_yok',
                    'urun_adi': urun_adi or 'Bilinmeyen Ürün',
                    'success': True
                }
        
        # 2. "Add to bag" veya "Sepete Ekle" butonu - KESIN STOKTA VAR (ama disabled olmamalı)
        add_to_bag_patterns = [
            r'add to bag',
            r'sepete ekle',
            r'add to cart',
            r'buy now',
            r'şimdi satın al'
        ]
        
        # Butonları kontrol et
        buttons = soup.find_all('button')
        active_button_found = False
        
        for button in buttons:
            button_text = button.get_text().lower()
            button_class = str(button.get('class', [])).lower()
            button_disabled = button.get('disabled') is not None or 'disabled' in button_class
            
            # Buton metninde "sepete ekle" veya "add to bag" var mı?
            for pattern in add_to_bag_patterns:
                if re.search(pattern, button_text, re.I):
                    if not button_disabled:
                        stok_durumu = 'stokta_var'
                        active_button_found = True
                        print(f"  ✅ Aktif buton bulundu: {button_text[:50]}")
                        break
            if active_button_found:
                break
        
        # Eğer aktif buton bulunamadıysa, sayfa içeriğinde ara ama dikkatli
        if not active_button_found:
            for pattern in add_to_bag_patterns:
                if re.search(pattern, page_text, re.I):
                    # Ama disabled buton olmamalı
                    disabled_buttons = soup.find_all('button', class_=re.compile(r'disabled|unavailable', re.I))
                    if len(disabled_buttons) == 0:
                        stok_durumu = 'stokta_var'
                        print(f"  ✅ Sayfa içeriğinde aktif 'Sepete Ekle' bulundu")
                        break
        
        # 3. Button elementlerinde kontrol - Disabled olmamalı
        buttons = soup.find_all('button')
        active_button_found = False
        for button in buttons:
            button_text = button.get_text().lower()
            button_class = str(button.get('class', [])).lower()
            button_disabled = button.get('disabled') is not None
            
            if any(word in button_text for word in ['sepete ekle', 'add to bag', 'add to cart', 'buy now']):
                # Buton aktif ve disabled değilse stokta var
                if not button_disabled and 'disabled' not in button_class and 'unavailable' not in button_class:
                    stok_durumu = 'stokta_var'
                    active_button_found = True
                    print(f"  ✅ Aktif buton bulundu: {button_text[:50]}")
                    break
                else:
                    # Disabled buton varsa stokta yok
                    stok_durumu = 'stokta_yok'
                    print(f"  ❌ Disabled buton bulundu: {button_text[:50]}")
                    break
        
        # 4. JSON-LD structured data kontrolü
        json_ld = soup.find('script', type='application/ld+json')
        if json_ld:
            try:
                import json
                data = json.loads(json_ld.string)
                if isinstance(data, dict) and 'offers' in data:
                    availability = data['offers'].get('availability', '')
                    if 'OutOfStock' in availability or 'out of stock' in availability.lower() or 'SoldOut' in availability:
                        stok_durumu = 'stokta_yok'
                        print(f"  ❌ JSON-LD: Stokta yok")
                    elif 'InStock' in availability or 'in stock' in availability.lower() or 'InStoreOnly' in availability:
                        stok_durumu = 'stokta_var'
                        print(f"  ✅ JSON-LD: Stokta var")
            except:
                pass
        
        # 5. Beden seçenekleri kontrolü - Sadece aktif bedenler varsa stokta var
        if stok_durumu != 'stokta_yok' and not active_button_found:
            size_elements = soup.find_all(['button', 'div', 'span', 'a'], 
                                         class_=re.compile(r'size|beden|talla', re.I))
            if size_elements:
                available_count = 0
                disabled_count = 0
                for elem in size_elements:
                    classes = str(elem.get('class', [])).lower()
                    is_disabled = elem.get('disabled') is not None
                    if 'disabled' not in classes and 'unavailable' not in classes and not is_disabled:
                        available_count += 1
                    else:
                        disabled_count += 1
                
                # Sadece disabled bedenler varsa stokta yok
                if available_count == 0 and disabled_count > 0:
                    stok_durumu = 'stokta_yok'
                    print(f"  ❌ Sadece disabled bedenler var ({disabled_count} adet)")
                elif available_count > 0:
                    stok_durumu = 'stokta_var'
                    print(f"  ✅ {available_count} aktif beden seçeneği mevcut")
        
        print(f"  📊 Sonuç: {stok_durumu}")
        
        return {
            'stok_durumu': stok_durumu,
            'urun_adi': urun_adi or 'Bilinmeyen Ürün',
            'success': True
        }
        
    except requests.exceptions.RequestException as e:
        error_msg = f"URL'ye erişilemedi: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            'stok_durumu': 'hata',
            'urun_adi': '',
            'success': False,
            'error': error_msg
        }
    except Exception as e:
        error_msg = f"Stok kontrolü hatası: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        return {
            'stok_durumu': 'hata',
            'urun_adi': '',
            'success': False,
            'error': error_msg
        }

# Selenium ile stok kontrolü (JavaScript gerektiren sayfalar için)
def check_bershka_stock_selenium(product_url, beden=None):
    """
    Selenium kullanarak JavaScript ile yüklenen sayfaları kontrol eder
    beden: Takip edilecek beden (örn: 'S', 'M', 'L', 'Small', 'Medium', 'Large')
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException, NoSuchElementException
        import time
        
        print("  🌐 Selenium ile sayfa yükleniyor...")
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        try:
            driver.get(product_url)
            
            # Sayfanın yüklenmesini bekle (en fazla 10 saniye)
            time.sleep(5)  # JavaScript'in çalışması için bekle
            
            # Ürün adını bul
            urun_adi = 'Bilinmeyen Ürün'
            try:
                # Farklı selector'ları dene
                selectors = [
                    'h1',
                    '[data-testid="product-title"]',
                    '.product-title',
                    '.product-name',
                    'h1.product-title',
                    'h1.product-name'
                ]
                for selector in selectors:
                    try:
                        title_elem = driver.find_element(By.CSS_SELECTOR, selector)
                        if title_elem and title_elem.text.strip():
                            urun_adi = title_elem.text.strip()
                            print(f"  ✅ Ürün adı bulundu: {urun_adi[:50]}")
                            break
                    except:
                        continue
            except:
                pass
            
            # Beden seçim durumu
            beden_secildi = False
            
            # Eğer belirli bir beden takip ediliyorsa, önce o bedeni seç
            if beden:
                print(f"  👕 Belirli beden kontrol ediliyor: {beden}")
                try:
                    # Beden seçeneklerini bul - farklı selector'ları dene
                    
                    # Beden mapping (S -> Small, M -> Medium, vb.)
                    beden_mapping = {
                        'XXS': ['XXS', 'xxs', 'extra extra small', 'extra-extra-small', '2xs'],
                        'XS': ['XS', 'xs', 'extra small', 'extra-small'],
                        'S': ['S', 's', 'small'],
                        'M': ['M', 'm', 'medium'],
                        'L': ['L', 'l', 'large'],
                        'XL': ['XL', 'xl', 'extra large', 'extra-large'],
                        'XXL': ['XXL', 'xxl', 'extra extra large', '2xl'],
                        '32': ['32'],
                        '34': ['34'],
                        '36': ['36'],
                        '38': ['38'],
                        '40': ['40'],
                        '42': ['42'],
                        '44': ['44'],
                        '46': ['46'],
                        '48': ['48']
                    }
                    
                    beden_variants = [beden, beden.upper(), beden.lower()]
                    if beden in beden_mapping:
                        beden_variants.extend(beden_mapping[beden])
                    
                    # ÖNCE: Ürün sayfasındaki beden seçim alanını bul
                    # Bershka'da bedenler genellikle belirli container'larda bulunur
                    size_container = None
                    container_selectors = [
                        "[class*='size-selector']",
                        "[class*='product-sizes']",
                        "[class*='size-list']",
                        "[class*='size-options']",
                        "[class*='size-container']",
                        "[class*='sizes']",
                        "[data-testid*='size']",
                        "[id*='size']",
                        ".product-size-selector",
                        ".size-selector",
                        "[class*='product-detail'] [class*='size']"
                    ]
                    
                    for container_selector in container_selectors:
                        try:
                            containers = driver.find_elements(By.CSS_SELECTOR, container_selector)
                            if containers:
                                size_container = containers[0]
                                print(f"  📦 Beden container bulundu: {container_selector}")
                                break
                        except:
                            continue
                    
                    # Eğer container bulunduysa, sadece o container içindeki elementleri ara
                    # Aksi halde tüm sayfada ara (ama daha spesifik selector'larla)
                    if size_container:
                        # Container içinde beden elementlerini bul
                        # ÖNEMLİ: Button elementlerini öncelikli olarak al (div'ler wrapper olabilir)
                        button_elements = size_container.find_elements(By.CSS_SELECTOR, "button")
                        div_elements = size_container.find_elements(By.CSS_SELECTOR, "div[class*='size'], div[class*='dot']")
                        # Önce button'ları, sonra div'leri ekle
                        size_elements = button_elements + div_elements
                        print(f"  🔍 Container içinde {len(button_elements)} button, {len(div_elements)} div bulundu (Toplam: {len(size_elements)})")
                    else:
                        # Container bulunamadıysa, daha spesifik selector'larla tüm sayfada ara
                        # SADECE gerçek beden elementlerini bulmak için daha kısıtlayıcı selector'lar
                        size_elements = driver.find_elements(By.CSS_SELECTOR, 
                            "button[data-size], "
                            "div[data-size], "
                            "span[data-size], "
                            "a[data-size], "
                            "button[class*='size-option'], "
                            "button[class*='size-button'], "
                            "div[class*='size-option'], "
                            "span[class*='size-option'], "
                            "[class*='size-selector'] button, "
                            "[class*='size-selector'] div, "
                            "[class*='product-sizes'] button, "
                            "[class*='product-sizes'] div")
                        print(f"  🔍 Container bulunamadı, tüm sayfada {len(size_elements)} potansiyel beden elementi bulundu")
                    
                    # Eğer hala çok fazla element bulunduysa, daha da filtrele
                    if len(size_elements) > 50:
                        print(f"  ⚠️ Çok fazla element bulundu ({len(size_elements)}), filtreleme yapılıyor...")
                        # Sadece görünür ve tıklanabilir elementleri al
                        filtered_elements = []
                        for elem in size_elements:
                            try:
                                if elem.is_displayed() and elem.is_enabled():
                                    elem_text = elem.text.strip()
                                    elem_class = elem.get_attribute('class') or ''
                                    elem_data_size = elem.get_attribute('data-size') or ''
                                    
                                    # Eğer text'te beden numarası/harfi varsa veya data-size varsa
                                    if (elem_text and len(elem_text) <= 5 and 
                                        (any(char.isdigit() for char in elem_text) or 
                                         any(char.isalpha() for char in elem_text) and len(elem_text) <= 3) or
                                        elem_data_size):
                                        filtered_elements.append(elem)
                            except:
                                continue
                        size_elements = filtered_elements
                        print(f"  ✅ Filtreleme sonrası {len(size_elements)} beden elementi kaldı")
                    
                    for idx, elem in enumerate(size_elements):
                        try:
                            elem_text = elem.text.strip()
                            elem_text_upper = elem_text.upper()
                            elem_data_size = elem.get_attribute('data-size') or ''
                            elem_class = elem.get_attribute('class') or ''
                            elem_class_lower = elem_class.lower()
                            elem_class_upper = elem_class.upper()
                            elem_aria_label = elem.get_attribute('aria-label') or ''
                            elem_title = elem.get_attribute('title') or ''
                            elem_tag = elem.tag_name
                            
                            # Debug: Element bilgilerini yazdır (daha fazla detay)
                            if idx < 10:  # İlk 10 elementi göster
                                print(f"    [{idx}] Tag: {elem_tag}, Text: '{elem_text[:30]}', Data-size: '{elem_data_size}', Class: '{elem_class[:60]}', Aria: '{elem_aria_label[:30]}'")
                            
                            # Beden eşleşmesi kontrol et - TAM EŞLEŞME OLMALI
                            beden_eslesti = False
                            matched_variant = None
                            
                            for variant in beden_variants:
                                variant_upper = variant.upper()
                                
                                # 1. Tam metin eşleşmesi (en güvenilir)
                                if variant_upper == elem_text_upper:
                                    beden_eslesti = True
                                    matched_variant = variant
                                    print(f"    ✅ Tam metin eşleşmesi: '{variant}' == '{elem_text}'")
                                    break
                                
                                # 2. Tek kelime ve tam eşleşme (örnek: "S" == "S", "36" == "36")
                                elem_words = elem_text_upper.split()
                                if len(elem_words) == 1 and variant_upper == elem_words[0]:
                                    beden_eslesti = True
                                    matched_variant = variant
                                    print(f"    ✅ Tek kelime eşleşmesi: '{variant}' == '{elem_text}'")
                                    break
                                
                                # 3. Data-size attribute eşleşmesi
                                if elem_data_size and variant_upper == elem_data_size.upper():
                                    beden_eslesti = True
                                    matched_variant = variant
                                    print(f"    ✅ Data-size eşleşmesi: '{variant}' == '{elem_data_size}'")
                                    break
                                
                                # 4. Aria-label eşleşmesi - SADECE beden ile ilgili aria-label'lar
                                # ÖNEMLİ: Aria-label'da beden tam olarak geçmeli (örnek: "S Beden", "M Beden", "36 Beden")
                                if elem_aria_label:
                                    aria_upper = elem_aria_label.upper().strip()
                                    # Aria-label formatı genellikle: "S Beden", "M Beden", "36 Beden" gibi
                                    # Tam eşleşme: aria-label başında beden olmalı
                                    if (aria_upper.startswith(variant_upper + ' ') or  # "S Beden", "M Beden"
                                        aria_upper == variant_upper or  # Sadece "S", "M", "36"
                                        aria_upper == variant_upper + ' BEDEN' or  # "S BEDEN"
                                        aria_upper == variant_upper + ' SIZE'):  # "S SIZE"
                                        # Ama "MENÜ", "SEARCH" gibi kelimelerde geçmemeli
                                        if ('MENÜ' not in aria_upper and 
                                            'MENU' not in aria_upper and
                                            'SEARCH' not in aria_upper and
                                            'ARAMA' not in aria_upper):
                                            beden_eslesti = True
                                            matched_variant = variant
                                            print(f"    ✅ Aria-label eşleşmesi: '{variant}' == '{elem_aria_label}'")
                                            break
                                
                                # 5. Title eşleşmesi - SADECE beden ile ilgili title'lar
                                # ÖNEMLİ: Title'da beden tam olarak geçmeli
                                if elem_title:
                                    title_upper = elem_title.upper().strip()
                                    # Title formatı genellikle: "S Beden", "M Beden" gibi
                                    if (title_upper.startswith(variant_upper + ' ') or  # "S Beden"
                                        title_upper == variant_upper or  # Sadece "S"
                                        title_upper == variant_upper + ' BEDEN' or  # "S BEDEN"
                                        title_upper == variant_upper + ' SIZE'):  # "S SIZE"
                                        if ('MENÜ' not in title_upper and 
                                            'MENU' not in title_upper and
                                            'SEARCH' not in title_upper):
                                            beden_eslesti = True
                                            matched_variant = variant
                                            print(f"    ✅ Title eşleşmesi: '{variant}' == '{elem_title}'")
                                            break
                                
                                # 6. Class içinde eşleşme (daha az güvenilir, son çare)
                                # SADECE "size" veya "beden" içeren class'larda ara
                                if ('size' in elem_class_lower or 'beden' in elem_class_lower) and variant_upper in elem_class_upper:
                                    # Ama çok dikkatli - sadece beden numarası/harfi olmalı
                                    # Ve "menu", "search" gibi kelimeler içermemeli
                                    if (len(variant_upper) <= 3 and  # S, M, L, 36, 38 gibi kısa bedenler
                                        'menu' not in elem_class_lower and
                                        'search' not in elem_class_lower):
                                        beden_eslesti = True
                                        matched_variant = variant
                                        print(f"    ⚠️ Class eşleşmesi (daha az güvenilir): '{variant}' in class")
                                        break
                            
                            if beden_eslesti:
                                # ÖNEMLİ KONTROL: Element text'i ile aranan beden eşleşmeli!
                                # Eğer element text'i farklıysa (örnek: XXS ama M aranıyor), bu yanlış eşleşme
                                elem_text_clean = elem_text.strip().upper()
                                
                                # Element text'i ile variant eşleşmeli
                                text_matches = (
                                    elem_text_clean == variant_upper or  # Tam eşleşme
                                    (elem_text_clean and variant_upper in elem_text_clean and len(elem_text_clean) <= len(variant_upper) + 2)  # Çok yakın
                                )
                                
                                # Eğer text eşleşmiyorsa ama data-size eşleşiyorsa, o da kabul edilebilir
                                data_size_matches = (elem_data_size and variant_upper == elem_data_size.upper())
                                
                                if not text_matches and not data_size_matches:
                                    print(f"  ⚠️ Yanlış eşleşme: Aranan='{beden}', Element text='{elem_text}', Variant='{matched_variant}' - ATLANIYOR")
                                    continue  # Bu elementi atla, bir sonrakine geç
                                
                                # EK KONTROL: Element gerçekten bir beden elementi mi?
                                # ÖNEMLİ: Button elementlerini tercih et (div'ler wrapper olabilir)
                                is_real_size_element = (
                                    text_matches or data_size_matches or  # Text veya data-size eşleşiyor
                                    elem_tag == 'button' or  # Button elementleri her zaman kabul et
                                    'size' in elem_class_lower or  # Class'ta "size" varsa
                                    'beden' in elem_class_lower or  # Class'ta "beden" varsa
                                    ('button' in elem_class_lower and ('size' in elem_class_lower or 'dot' in elem_class_lower))  # Size butonu
                                )
                                
                                if not is_real_size_element:
                                    print(f"  ⚠️ Yanlış element (beden elementi değil): Text='{elem_text[:20]}', Class='{elem_class[:50]}'")
                                    continue  # Bu elementi atla, bir sonrakine geç
                                
                                # ÖNEMLİ: Eğer div elementi ise, içindeki veya yanındaki button elementini kontrol et
                                # Çünkü div wrapper olabilir, asıl tıklanabilir element button olabilir
                                if elem_tag == 'div':
                                    # Div içinde button var mı?
                                    try:
                                        button_elem = elem.find_element(By.TAG_NAME, 'button')
                                        if button_elem and button_elem.is_displayed():
                                            # Button elementini kullan
                                            elem = button_elem
                                            elem_text = button_elem.text.strip()
                                            elem_class = button_elem.get_attribute('class') or ''
                                            elem_class_lower = elem_class.lower()
                                            elem_tag = 'button'
                                            print(f"  🔄 Div içinde button bulundu, button kullanılıyor: '{elem_text}'")
                                    except:
                                        # Button bulunamadıysa, parent'ta button var mı?
                                        try:
                                            parent = elem.find_element(By.XPATH, '..')
                                            button_elem = parent.find_element(By.TAG_NAME, 'button')
                                            if button_elem and button_elem.is_displayed():
                                                elem = button_elem
                                                elem_text = button_elem.text.strip()
                                                elem_class = button_elem.get_attribute('class') or ''
                                                elem_class_lower = elem_class.lower()
                                                elem_tag = 'button'
                                                print(f"  🔄 Parent'ta button bulundu, button kullanılıyor: '{elem_text}'")
                                        except:
                                            pass  # Button bulunamadıysa div'i kullan
                                
                                print(f"  🎯 Beden eşleşti: {beden} (Variant: {matched_variant}, Element: {elem_tag}, Text: '{elem_text}', Data-size: '{elem_data_size}')")
                                
                                # Disabled kontrolü - çok dikkatli
                                # ÖNEMLİ: Sadece kesin "disabled" işaretleri
                                is_disabled = (
                                    ('is-disabled' in elem_class_lower and 'enabled' not in elem_class_lower) or  # Kesin disabled
                                    (elem_tag == 'button' and not elem.is_enabled()) or  # Button disabled
                                    elem.get_attribute('disabled') is not None or  # Disabled attribute
                                    elem.get_attribute('aria-disabled') == 'true'  # Aria disabled
                                )
                                
                                # "unavailable", "out-of-stock" gibi class'lar sadece div'lerde olabilir, button'da değil
                                # Eğer button ise, sadece yukarıdaki kontrolleri yap
                                if elem_tag != 'button':
                                    is_disabled = is_disabled or (
                                        'unavailable' in elem_class_lower or
                                        'out-of-stock' in elem_class_lower or
                                        'not-available' in elem_class_lower
                                    )
                                
                                if is_disabled:
                                    print(f"  ❌ Beden disabled: {beden} (Class: {elem_class[:50]})")
                                    # Disabled beden bulundu - stokta yok
                                    driver.quit()
                                    return {
                                        'stok_durumu': 'stokta_yok',
                                        'urun_adi': urun_adi,
                                        'success': True,
                                        'message': f'Beden disabled/stokta yok: {beden}'
                                    }
                                
                                # Disabled değilse, bedeni seç
                                print(f"  ✅ Beden aktif, seçiliyor: {beden}")
                                # Bedeni seç
                                driver.execute_script("arguments[0].scrollIntoView(true);", elem)
                                time.sleep(0.5)
                                driver.execute_script("arguments[0].click();", elem)
                                time.sleep(3)  # Sayfanın güncellenmesi için daha uzun bekle
                                
                                # Seçildikten sonra tekrar kontrol et - gerçekten seçildi mi ve aktif mi?
                                # ÖNEMLİ: Beden tıklandıysa, seçilmiş kabul et (varsayılan olarak)
                                beden_secildi = True
                                print(f"  ✅ Beden tıklandı, seçilmiş kabul ediliyor: {beden} (Element: {elem_text[:20]})")
                                
                                # Ek doğrulama (opsiyonel - sadece log için)
                                try:
                                    updated_class = elem.get_attribute('class') or ''
                                    updated_data_selected = elem.get_attribute('data-selected') or ''
                                    updated_aria_selected = elem.get_attribute('aria-selected') or ''
                                    
                                    is_selected = (
                                        'selected' in updated_class.lower() or 
                                        'active' in updated_class.lower() or
                                        updated_data_selected.lower() == 'true' or
                                        updated_aria_selected.lower() == 'true'
                                    )
                                    
                                    if is_selected:
                                        print(f"  ✅ Beden seçili görünüyor (class/attribute kontrolü): {beden}")
                                except:
                                    pass
                                
                                break
                        except Exception as e:
                            print(f"  ⚠️ Beden seçim hatası: {str(e)}")
                            continue
                    
                    if not beden_secildi:
                        print(f"  ⚠️ Beden bulunamadı veya disabled: {beden}, stokta yok olarak işaretleniyor")
                        # Beden bulunamadıysa veya seçilemediyse, stokta yok
                        driver.quit()
                        return {
                            'stok_durumu': 'stokta_yok',
                            'urun_adi': urun_adi,
                            'success': True,
                            'message': f'Beden bulunamadı veya stokta yok: {beden}'
                        }
                except Exception as e:
                    print(f"  ⚠️ Beden seçme hatası: {str(e)}")
            
            # Stok durumunu kontrol et
            # Eğer belirli bir beden seçildiyse, o bedenin stok durumunu kontrol et
            if beden and beden_secildi:
                print(f"  🔍 Seçilen bedenin ({beden}) stok durumu kontrol ediliyor...")
                print(f"  📋 DEBUG: Beden seçimi başarılı, detaylı kontrol yapılıyor...")
                
                # Sayfanın güncellenmesi için bekle
                time.sleep(4)  # Daha uzun bekleme
                
                # Varsayılan: Stokta yok (güvenli yaklaşım - sadece kesin "stokta var" işaretleri görürsek "stokta var" deriz)
                stok_durumu_beden = 'stokta_yok'
                print(f"  📋 DEBUG: Varsayılan stok durumu: {stok_durumu_beden}")
                
                # ÖNCE: Seçilen beden elementinin disabled olup olmadığını kontrol et
                try:
                    print(f"  📋 DEBUG: Seçili beden elementini arıyorum...")
                    # Seçilen beden elementini bul - farklı yollarla
                    selected_elem = None
                    
                    # 1. "selected" veya "active" class'ı olan elementleri bul
                    selected_elements = driver.find_elements(By.CSS_SELECTOR, 
                        "[class*='selected'][class*='size'], "
                        "[class*='active'][class*='size'], "
                        "button[class*='size'][class*='selected'], "
                        "button[class*='size'][class*='active'], "
                        "button[class*='dot'][class*='selected'], "
                        "button[class*='dot'][class*='active']")
                    
                    print(f"  📋 DEBUG: {len(selected_elements)} seçili element bulundu")
                    
                    beden_variants_check = [beden.upper(), beden.lower()]
                    if beden in beden_mapping:
                        beden_variants_check.extend([v.upper() for v in beden_mapping[beden]])
                    
                    for idx, sel_elem in enumerate(selected_elements):
                        sel_text = sel_elem.text.strip().upper()
                        sel_data_size = sel_elem.get_attribute('data-size') or ''
                        sel_class = sel_elem.get_attribute('class') or ''
                        sel_tag = sel_elem.tag_name
                        
                        print(f"  📋 DEBUG: Seçili element [{idx}]: Tag={sel_tag}, Text='{sel_text}', Class='{sel_class[:50]}'")
                        
                        # Seçilen bedenle eşleşiyor mu?
                        for variant in beden_variants_check:
                            variant_upper = variant.upper()
                            if (variant_upper == sel_text or 
                                (variant_upper in sel_text and len(sel_text.split()) == 1) or
                                variant_upper == sel_data_size.upper()):
                                selected_elem = sel_elem
                                print(f"  ✅ Seçili beden elementi bulundu: {beden} (Tag: {sel_tag}, Text: '{sel_text}')")
                                break
                        if selected_elem:
                            break
                    
                    # Seçili beden elementi bulunduysa, disabled olup olmadığını kontrol et
                    if selected_elem:
                        sel_class = selected_elem.get_attribute('class') or ''
                        sel_tag = selected_elem.tag_name
                        sel_enabled = selected_elem.is_enabled()
                        sel_disabled_attr = selected_elem.get_attribute('disabled')
                        sel_aria_disabled = selected_elem.get_attribute('aria-disabled')
                        
                        print(f"  📋 DEBUG: Seçili element kontrolü:")
                        print(f"    - Tag: {sel_tag}")
                        print(f"    - Class: {sel_class[:80]}")
                        print(f"    - is_enabled(): {sel_enabled}")
                        print(f"    - disabled attr: {sel_disabled_attr}")
                        print(f"    - aria-disabled: {sel_aria_disabled}")
                        
                        sel_disabled = (
                            'is-disabled' in sel_class.lower() or
                            ('disabled' in sel_class.lower() and 'enabled' not in sel_class.lower()) or
                            'unavailable' in sel_class.lower() or
                            'out-of-stock' in sel_class.lower() or
                            (sel_tag == 'button' and not sel_enabled) or
                            sel_disabled_attr is not None or
                            sel_aria_disabled == 'true'
                        )
                        
                        print(f"  📋 DEBUG: Disabled kontrolü sonucu: {sel_disabled}")
                        
                        if sel_disabled:
                            print(f"  ❌ Seçili beden disabled: {beden} (Class: {sel_class[:50]})")
                            stok_durumu_beden = 'stokta_yok'
                        else:
                            print(f"  ✅ Seçili beden aktif görünüyor: {beden}")
                            stok_durumu_beden = 'stokta_var'  # İlk iyi işaret
                    else:
                        print(f"  ⚠️ Seçili beden elementi bulunamadı, buton kontrolüne geçiliyor")
                except Exception as e:
                    print(f"  ⚠️ Seçili beden kontrolü hatası: {str(e)}")
                    import traceback
                    traceback.print_exc()
                
                # İKİNCİ: "Sepete Ekle" butonunun durumunu kontrol et (EN ÖNEMLİ KONTROL)
                print(f"  📋 DEBUG: 'Sepete Ekle' butonu kontrol ediliyor...")
                try:
                    add_buttons = driver.find_elements(By.XPATH, 
                        "//button[contains(text(), 'Sepete Ekle')] | //button[contains(text(), 'Add to bag')] | //button[contains(text(), 'Add to cart')] | //button[contains(., 'Sepete')] | //button[contains(., 'Add to')]")
                    
                    print(f"  📋 DEBUG: {len(add_buttons)} 'Sepete Ekle' butonu bulundu")
                    
                    if len(add_buttons) > 0:
                        # Tüm butonlar disabled mı kontrol et
                        all_disabled = True
                        for idx, btn in enumerate(add_buttons):
                            btn_text = btn.text.strip()
                            btn_class = btn.get_attribute('class') or ''
                            btn_disabled_attr = btn.get_attribute('disabled')
                            btn_aria_disabled = btn.get_attribute('aria-disabled')
                            btn_enabled = btn.is_enabled()
                            btn_displayed = btn.is_displayed()
                            
                            print(f"  📋 DEBUG: Buton [{idx}]:")
                            print(f"    - Text: '{btn_text[:50]}'")
                            print(f"    - Class: '{btn_class[:80]}'")
                            print(f"    - is_enabled(): {btn_enabled}")
                            print(f"    - is_displayed(): {btn_displayed}")
                            print(f"    - disabled attr: {btn_disabled_attr}")
                            print(f"    - aria-disabled: {btn_aria_disabled}")
                            
                            # Buton aktif mi? Çok dikkatli kontrol
                            is_button_active = (
                                btn_enabled and 
                                btn_displayed and
                                btn_disabled_attr is None and
                                btn_aria_disabled != 'true'
                            )
                            
                            # Class kontrolü - sadece kesin "disabled" işaretleri
                            class_disabled = (
                                'disabled' in btn_class.lower() and 
                                'enabled' not in btn_class.lower() and
                                'is-disabled' in btn_class.lower()
                            )
                            
                            print(f"  📋 DEBUG: Buton aktif mi? {is_button_active}, Class disabled? {class_disabled}")
                            
                            if is_button_active and not class_disabled:
                                all_disabled = False
                                print(f"  ✅ 'Sepete Ekle' butonu aktif - {beden} bedeni stokta var")
                                stok_durumu_beden = 'stokta_var'
                                break
                            else:
                                print(f"  ⚠️ Buton aktif değil veya disabled")
                        
                        if all_disabled:
                            print(f"  ❌ TÜM 'Sepete Ekle' butonları disabled - {beden} bedeni stokta yok")
                            stok_durumu_beden = 'stokta_yok'
                    else:
                        print(f"  ⚠️ 'Sepete Ekle' butonu bulunamadı")
                        # Buton bulunamazsa, stokta yok kabul et (güvenli yaklaşım)
                        stok_durumu_beden = 'stokta_yok'
                except Exception as e:
                    print(f"  ⚠️ Buton kontrolü hatası: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    # Hata olursa, stokta yok kabul et (güvenli yaklaşım)
                    stok_durumu_beden = 'stokta_yok'
                
                # Sonuç
                if stok_durumu_beden == 'stokta_yok':
                    driver.quit()
                    return {
                        'stok_durumu': 'stokta_yok',
                        'urun_adi': urun_adi,
                        'success': True,
                        'message': f'Seçilen beden stokta yok: {beden}'
                    }
                else:
                    print(f"  ✅ {beden} bedeni stokta var")
                    # Beden seçildiyse ve kontroller geçtiyse, stokta var
                    driver.quit()
                    return {
                        'stok_durumu': 'stokta_var',
                        'urun_adi': urun_adi,
                        'success': True,
                        'message': f'Seçilen beden stokta var: {beden}'
                    }
            
            # Varsayılan: Stokta yok (güvenli yaklaşım) - sadece beden seçilmediyse
            stok_durumu = 'stokta_yok'
            
            # Eğer beden seçilmediyse, genel stok kontrolü yap
            if not beden or not beden_secildi:
                # İKİNCİ: Seçili beden elementinin disabled olup olmadığını kontrol et
                try:
                    # Seçili beden elementini bul
                    selected_size_elements = driver.find_elements(By.CSS_SELECTOR, 
                        "button[class*='size'][class*='selected'], "
                        "button[class*='size'][class*='active'], "
                        "div[class*='size'][class*='selected'], "
                        "div[class*='size'][class*='active'], "
                        "[class*='selected'][class*='size'], "
                        "[class*='active'][class*='size']")
                    
                    # Seçili bedenin disabled olup olmadığını kontrol et
                    beden_disabled = False
                    for elem in selected_size_elements:
                        elem_text = elem.text.strip()
                        elem_text_upper = elem_text.upper()
                        elem_class = elem.get_attribute('class') or ''
                        elem_data_size = elem.get_attribute('data-size') or ''
                        
                        # Seçilen bedenle eşleşiyor mu? TAM EŞLEŞME
                        beden_variants_check = [beden.upper(), beden.lower()]
                        if beden in beden_mapping:
                            beden_variants_check.extend([v.upper() for v in beden_mapping[beden]])
                        
                        for variant in beden_variants_check:
                            variant_upper = variant.upper()
                            # Tam eşleşme veya çok yakın eşleşme
                            if (variant_upper == elem_text_upper or  # Tam eşleşme
                                (variant_upper in elem_text_upper and len(elem_text_upper.split()) == 1) or  # Tek kelime
                                variant_upper == elem_data_size.upper()):
                                # Disabled mı kontrol et
                                is_elem_disabled = (
                                    'disabled' in elem_class.lower() or 
                                    'unavailable' in elem_class.lower() or
                                    'out-of-stock' in elem_class.lower() or
                                    not elem.is_enabled() or
                                    elem.get_attribute('disabled') is not None or
                                    elem.get_attribute('aria-disabled') == 'true'
                                )
                                
                                if is_elem_disabled:
                                    beden_disabled = True
                                    print(f"  ❌ Seçilen beden disabled: {beden} (Text: {elem_text[:20]}, Class: {elem_class[:50]})")
                                    break
                        if beden_disabled:
                            break
                    
                    if beden_disabled:
                        driver.quit()
                        return {
                            'stok_durumu': 'stokta_yok',
                            'urun_adi': urun_adi,
                            'success': True,
                            'message': f'Seçilen beden stokta yok: {beden}'
                        }
                except Exception as e:
                    print(f"  ⚠️ Seçili beden kontrolü hatası: {str(e)}")
            
            # Varsayılan: Stokta yok (güvenli yaklaşım)
            stok_durumu = 'stokta_yok'
            
            page_source = driver.page_source.lower()
            
            # 1. "Out of stock" veya "Stokta yok" mesajı - KESIN STOKTA YOK
            # AMA: Eğer belirli bir beden seçildiyse, sadece o beden için mesaj aramalıyız
            out_of_stock_patterns = [
                'out of stock',
                'stokta yok',
                'tükendi',
                'stok yok',
                'not available',
                'unavailable',
                'no longer available',
                'agotado',
                'stokta değil',
                'currently unavailable'
            ]
            
            # Eğer belirli bir beden seçildiyse, genel "stokta yok" mesajını görmezden gel
            # Sadece seçilen beden için özel mesaj varsa dikkate al
            if beden and beden_secildi:
                # Seçilen beden için özel "stokta yok" mesajı ara
                # (örneğin "36 beden stokta yok" gibi)
                beden_specific_out_of_stock = False
                for pattern in out_of_stock_patterns:
                    # Sayfada beden numarasıyla birlikte "stokta yok" mesajı var mı?
                    if f'{beden}'.lower() in page_source and pattern in page_source:
                        # Ama bu mesaj seçilen beden için mi?
                        # Daha spesifik kontrol yapalım - "Sepete Ekle" butonu disabled mı?
                        try:
                            add_buttons = driver.find_elements(By.XPATH, 
                                "//button[contains(text(), 'Sepete Ekle')] | //button[contains(text(), 'Add to bag')] | //button[contains(text(), 'Add to cart')]")
                            all_disabled = True
                            for btn in add_buttons:
                                if btn.is_enabled() and 'disabled' not in (btn.get_attribute('class') or '').lower():
                                    all_disabled = False
                                    break
                            if all_disabled and len(add_buttons) > 0:
                                beden_specific_out_of_stock = True
                                break
                        except:
                            pass
                
                if not beden_specific_out_of_stock:
                    # Genel "stokta yok" mesajlarını görmezden gel
                    print(f"  ℹ️ Belirli beden seçildi ({beden}), genel stok mesajları görmezden geliniyor")
            else:
                # Genel kontrol (beden seçilmediyse)
                for pattern in out_of_stock_patterns:
                    if pattern in page_source:
                        stok_durumu = 'stokta_yok'
                        print(f"  ❌ Stokta yok tespit edildi: {pattern}")
                        driver.quit()
                        return {
                            'stok_durumu': 'stokta_yok',
                            'urun_adi': urun_adi,
                            'success': True
                        }
            
            # 2. "Add to bag" veya "Sepete Ekle" butonu - KESIN STOKTA VAR (ama disabled olmamalı)
            try:
                # Tüm butonları bul
                all_buttons = driver.find_elements(By.TAG_NAME, 'button')
                active_add_button = False
                
                for button in all_buttons:
                    try:
                        button_text = button.text.lower()
                        button_class = button.get_attribute('class') or ''
                        button_disabled = button.get_attribute('disabled') is not None
                        button_enabled = button.is_enabled()
                        
                        # Buton metninde "sepete ekle" veya "add to bag" var mı?
                        if any(word in button_text for word in ['sepete ekle', 'add to bag', 'add to cart', 'buy now']):
                            # Buton aktif ve disabled değilse stokta var
                            if button_enabled and not button_disabled and 'disabled' not in button_class.lower():
                                stok_durumu = 'stokta_var'
                                active_add_button = True
                                print(f"  ✅ Aktif buton bulundu: {button_text[:50]}")
                                break
                    except:
                        continue
                
                # Eğer aktif buton bulunamadıysa, disabled buton var mı kontrol et
                if not active_add_button:
                    disabled_buttons = driver.find_elements(By.CSS_SELECTOR, 
                        "button[disabled], button.disabled, button[class*='disabled'], button[class*='unavailable']")
                    if len(disabled_buttons) > 0:
                        # Disabled buton varsa muhtemelen stokta yok
                        for db in disabled_buttons:
                            if any(word in db.text.lower() for word in ['sepete ekle', 'add to bag', 'add to cart']):
                                stok_durumu = 'stokta_yok'
                                print(f"  ❌ Disabled buton bulundu: {db.text[:50]}")
                                break
            except Exception as e:
                print(f"  ⚠️ Buton kontrolü hatası: {str(e)}")
            
            # 3. Beden seçenekleri kontrolü - Sadece aktif bedenler varsa stokta var
            # Eğer belirli bir beden seçildiyse, bu kontrolü atla (zaten yukarıda kontrol ettik)
            if stok_durumu != 'stokta_yok' and not (beden and beden_secildi):
                try:
                    size_elements = driver.find_elements(By.CSS_SELECTOR, 
                        "[class*='size'], [class*='beden'], [class*='talla'], button[class*='size'], div[class*='size'], a[class*='size']")
                    if size_elements:
                        available_sizes = []
                        disabled_sizes = []
                        for elem in size_elements:
                            try:
                                classes = elem.get_attribute('class') or ''
                                is_disabled = elem.get_attribute('disabled') is not None
                                is_enabled = elem.is_enabled() if hasattr(elem, 'is_enabled') else True
                                
                                if 'disabled' not in classes.lower() and 'unavailable' not in classes.lower() and not is_disabled:
                                    if elem.is_displayed():
                                        available_sizes.append(elem)
                                else:
                                    disabled_sizes.append(elem)
                            except:
                                pass
                        
                        # Eğer sadece disabled bedenler varsa stokta yok
                        if len(available_sizes) == 0 and len(disabled_sizes) > 0:
                            stok_durumu = 'stokta_yok'
                            print(f"  ❌ Sadece disabled bedenler var ({len(disabled_sizes)} adet)")
                        elif len(available_sizes) > 0:
                            stok_durumu = 'stokta_var'
                            print(f"  ✅ {len(available_sizes)} aktif beden seçeneği bulundu")
                except Exception as e:
                    print(f"  ⚠️ Beden kontrolü hatası: {str(e)}")
            
            print(f"  📊 Selenium sonucu: {stok_durumu}")
            
            driver.quit()
            
            return {
                'stok_durumu': stok_durumu,
                'urun_adi': urun_adi,
                'success': True
            }
            
        except Exception as e:
            driver.quit()
            raise e
        
    except ImportError:
        print("  ⚠️ Selenium import hatası")
        # Selenium yoksa, URL'den ürün adını çıkar
        url_match = re.search(r'/([^/]+)\.html', product_url)
        if url_match:
            urun_adi = url_match.group(1).replace('-', ' ').title()
        else:
            urun_adi = 'Ürün'
        return {
            'stok_durumu': 'hata',
            'urun_adi': urun_adi,
            'success': False,
            'error': 'Selenium kullanılamadı'
        }
    except Exception as e:
        error_msg = f"Selenium hatası: {str(e)}"
        print(f"  ❌ {error_msg}")
        try:
            driver.quit()
        except:
            pass
        # Hata olsa bile URL'den ürün adını çıkar
        url_match = re.search(r'/([^/]+)\.html', product_url)
        if url_match:
            urun_adi = url_match.group(1).replace('-', ' ').title()
        else:
            urun_adi = 'Ürün'
        return {
            'stok_durumu': 'hata',
            'urun_adi': urun_adi,
            'success': False,
            'error': error_msg
        }

# Email gönderme fonksiyonu
def send_email_notification(urun_adi, urun_url, kullanici_id=None):
    """Stok geldiğinde email bildirimi gönder"""
    # Kullanıcı ID varsa, kullanıcının email ayarlarını kullan
    if kullanici_id:
        conn = sqlite3.connect('stok.db')
        c = conn.cursor()
        c.execute('SELECT email, smtp_server, smtp_port, email_user, email_password FROM kullanicilar WHERE id = ?', (kullanici_id,))
        kullanici = c.fetchone()
        conn.close()
        
        if kullanici:
            recipient_email, smtp_server, smtp_port, email_user, email_password = kullanici
            smtp_server = smtp_server or 'smtp.gmail.com'
            smtp_port = int(smtp_port or 587)
        else:
            print(f"⚠️ Kullanıcı bulunamadı: {kullanici_id}")
            return False
    else:
        # Eski yöntem (global ayarlar)
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        email_user = os.getenv('EMAIL_USER', '')
        email_password = os.getenv('EMAIL_PASSWORD', '')
        recipient_email = os.getenv('RECIPIENT_EMAIL', email_user)
    
    if not email_user or not email_password:
        print(f"⚠️ Email ayarları yapılmamış. Bildirim gönderilemedi. (Kullanıcı: {kullanici_id})")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = recipient_email
        msg['Subject'] = f'🎉 Bershka Stok Geldi: {urun_adi}'
        
        # Beden bilgisini email'e ekle (eğer varsa)
        beden_bilgisi = ""
        if 'beden' in urun_adi.lower() or '[Beden:' in urun_adi:
            # Beden bilgisi zaten ürün adında var
            pass
        else:
            # URL'den beden bilgisini çıkar (eğer varsa)
            pass
        
        body = f"""
Merhaba,

🎉 İYİ HABER! Takip ettiğiniz Bershka ürünü stokta mevcut!

📦 Ürün Adı: {urun_adi}
🔗 Ürün Linki: {urun_url}

⚡ HEMEN KONTROL ETMEK İÇİN LİNKE TIKLAYIN!

⏰ Bildirim Zamanı: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

---
Bu otomatik bir bildirimdir. Stok durumu sürekli kontrol edilmektedir.
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_password)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Bildirim gönderildi: {urun_adi}")
        return True
    except Exception as e:
        print(f"❌ Email gönderme hatası: {str(e)}")
        return False

# Sürekli stok kontrolü - her ürün için ayrı thread
urun_threads = {}  # {urun_id: thread}

def check_single_product_continuous(urun_id, urun_url, urun_adi, kullanici_id=None, beden=None):
    """Tek bir ürünü sürekli kontrol eder (anında bildirim için)"""
    print(f"🔄 Sürekli kontrol başlatıldı: {urun_adi or urun_url} (ID: {urun_id})" + (f" [Beden: {beden}]" if beden else ""))
    
    while True:
        try:
            # Veritabanından güncel durumu al
            conn = sqlite3.connect('stok.db')
            c = conn.cursor()
            c.execute('SELECT stok_durumu, bildirim_gonderildi, kullanici_id, takip_edilen_beden FROM urunler WHERE id = ?', (urun_id,))
            result = c.fetchone()
            conn.close()
            
            if not result:
                # Ürün silinmiş, thread'i durdur
                print(f"  ⏹️ Ürün silindi, kontrol durduruluyor: {urun_id}")
                break
            
            eski_stok_durumu, bildirim_gonderildi, urun_kullanici_id, urun_beden = result
            # Kullanıcı ID'yi güncelle (eğer None ise)
            if kullanici_id is None:
                kullanici_id = urun_kullanici_id
            # Beden'i güncelle (eğer None ise)
            if beden is None:
                beden = urun_beden
            
            # Stok kontrolü yap
            check_result = check_bershka_stock(urun_url, beden=beden)
            
            if check_result.get('success'):
                yeni_stok_durumu = check_result['stok_durumu']
                guncel_urun_adi = check_result.get('urun_adi', urun_adi)
                
                # Veritabanını güncelle
                conn = sqlite3.connect('stok.db')
                c = conn.cursor()
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                beden_text = f" [Beden: {beden}]" if beden else ""
                
                # STOK DURUMU KONTROLÜ - ANINDA BİLDİRİM
                # 1. Stok durumu değişti mi? (stokta_yok -> stokta_var)
                # 2. VEYA stok varsa ve bildirim gönderilmemişse (ilk ekleme veya ilk kontrol)
                stok_geldi = False
                
                if eski_stok_durumu == 'stokta_yok' and yeni_stok_durumu == 'stokta_var':
                    stok_geldi = True
                    print(f"  🎉🎉🎉 STOK GELDİ! (Durum değişti: yok -> var): {guncel_urun_adi}{beden_text}")
                elif yeni_stok_durumu == 'stokta_var' and bildirim_gonderildi == 0:
                    # Stok varsa ve bildirim gönderilmemişse (ilk ekleme veya ilk kontrol)
                    stok_geldi = True
                    print(f"  🎉🎉🎉 STOK BULUNDU! (Stokta var ve bildirim gönderilmemiş): {guncel_urun_adi}{beden_text}")
                    print(f"  📋 DEBUG: Eski durum: '{eski_stok_durumu}', Yeni durum: '{yeni_stok_durumu}', Bildirim: {bildirim_gonderildi}")
                
                # STOK GELDİ! ANINDA BİLDİRİM GÖNDER
                if stok_geldi and bildirim_gonderildi == 0:
                    print(f"  📧📧📧 ANINDA EMAIL BİLDİRİMİ GÖNDERİLİYOR: {guncel_urun_adi}{beden_text} (Kullanıcı: {kullanici_id})")
                    try:
                        # Email gönderme işlemini thread'de yap ki bloklanmasın (ANINDA)
                        def send_email_async():
                            try:
                                # Beden bilgisini email'e ekle
                                urun_adi_with_beden = f"{guncel_urun_adi}{beden_text}" if beden_text else guncel_urun_adi
                                send_email_notification(urun_adi_with_beden, urun_url, kullanici_id)
                                print(f"  ✅✅✅ EMAIL BAŞARIYLA GÖNDERİLDİ: {guncel_urun_adi}{beden_text}")
                            except Exception as e:
                                print(f"  ❌ Email gönderme hatası: {str(e)}")
                                import traceback
                                traceback.print_exc()
                        
                        # Thread'de gönder (anında, bloklanmadan)
                        email_thread = threading.Thread(target=send_email_async, daemon=True)
                        email_thread.start()
                        
                        # Veritabanını güncelle (bildirim gönderildi olarak işaretle)
                        c.execute('UPDATE urunler SET bildirim_gonderildi = 1 WHERE id = ?', (urun_id,))
                        conn.commit()
                        print(f"  ✅ Bildirim bayrağı güncellendi (ID: {urun_id})")
                    except Exception as e:
                        print(f"  ❌ Bildirim gönderme işlemi başlatılamadı: {str(e)}")
                        import traceback
                        traceback.print_exc()
                
                # Stok tekrar tükendiğinde bildirim bayrağını sıfırla
                if yeni_stok_durumu == 'stokta_yok':
                    c.execute('UPDATE urunler SET bildirim_gonderildi = 0 WHERE id = ?', (urun_id,))
                
                # Ürün bilgilerini güncelle
                c.execute('''UPDATE urunler 
                            SET urun_adi = ?, stok_durumu = ?, son_kontrol_tarihi = ?, guncelleme_tarihi = ?
                            WHERE id = ?''',
                         (guncel_urun_adi, yeni_stok_durumu, now, now, urun_id))
                conn.commit()
                conn.close()
            
            # Çok sık kontrol için kısa bekleme (5 saniye - daha hızlı bildirim için)
            time.sleep(5)
            
        except Exception as e:
            print(f"  ❌ Kontrol hatası (ID: {urun_id}): {str(e)}")
            time.sleep(60)  # Hata durumunda daha uzun bekle

def start_product_monitoring(urun_id, urun_url, urun_adi, kullanici_id=None, beden=None):
    """Bir ürün için sürekli kontrol thread'i başlatır"""
    if urun_id in urun_threads:
        # Zaten çalışıyor
        return
    
    thread = threading.Thread(
        target=check_single_product_continuous,
        args=(urun_id, urun_url, urun_adi, kullanici_id, beden),
        daemon=True
    )
    thread.start()
    urun_threads[urun_id] = thread
    beden_text = f" [Beden: {beden}]" if beden else ""
    print(f"✅ Ürün takibi başlatıldı: {urun_adi or urun_url} (Kullanıcı: {kullanici_id}){beden_text}")

def stop_product_monitoring(urun_id):
    """Bir ürün için sürekli kontrol thread'ini durdurur"""
    if urun_id in urun_threads:
        del urun_threads[urun_id]
        print(f"⏹️ Ürün takibi durduruldu: {urun_id}")

def start_all_monitoring():
    """Tüm ürünler için sürekli kontrol başlatır"""
    conn = sqlite3.connect('stok.db')
    c = conn.cursor()
    c.execute('SELECT id, urun_url, urun_adi, kullanici_id, takip_edilen_beden FROM urunler')
    urunler = c.fetchall()
    conn.close()
    
    for urun_id, urun_url, urun_adi, kullanici_id, beden in urunler:
        start_product_monitoring(urun_id, urun_url, urun_adi, kullanici_id, beden)
    
    print(f"🔄 Tüm ürünler için sürekli kontrol başlatıldı ({len(urunler)} ürün)")

# Periyodik stok kontrolü (eski - artık kullanılmıyor ama manuel kontrol için kalsın)
def check_all_products():
    """Tüm ürünlerin stok durumunu kontrol eder (manuel kontrol için)"""
    print(f"🔍 Manuel stok kontrolü başlatılıyor... {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    conn = sqlite3.connect('stok.db')
    c = conn.cursor()
    c.execute('SELECT id, urun_url, urun_adi, stok_durumu, bildirim_gonderildi FROM urunler')
    urunler = c.fetchall()
    conn.close()
    
    for urun_id, urun_url, urun_adi, eski_stok_durumu, bildirim_gonderildi in urunler:
        try:
            print(f"  📦 Kontrol ediliyor: {urun_adi or urun_url}")
            result = check_bershka_stock(urun_url)
            
            if not result['success']:
                continue
            
            yeni_stok_durumu = result['stok_durumu']
            guncel_urun_adi = result['urun_adi']
            
            # Veritabanını güncelle
            conn = sqlite3.connect('stok.db')
            c = conn.cursor()
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Stok durumu değişti mi kontrol et
            if eski_stok_durumu == 'stokta_yok' and yeni_stok_durumu == 'stokta_var':
                # Stok geldi! Bildirim gönder
                if bildirim_gonderildi == 0:
                    print(f"  🎉 Stok geldi: {guncel_urun_adi}")
                    thread = threading.Thread(
                        target=send_email_notification,
                        args=(guncel_urun_adi, urun_url)
                    )
                    thread.start()
                    c.execute('UPDATE urunler SET bildirim_gonderildi = 1 WHERE id = ?', (urun_id,))
            
            # Stok tekrar tükendiğinde bildirim bayrağını sıfırla
            if yeni_stok_durumu == 'stokta_yok':
                c.execute('UPDATE urunler SET bildirim_gonderildi = 0 WHERE id = ?', (urun_id,))
            
            # Ürün bilgilerini güncelle
            c.execute('''UPDATE urunler 
                        SET urun_adi = ?, stok_durumu = ?, son_kontrol_tarihi = ?, guncelleme_tarihi = ?
                        WHERE id = ?''',
                     (guncel_urun_adi, yeni_stok_durumu, now, now, urun_id))
            conn.commit()
            conn.close()
            
            time.sleep(2)  # Rate limiting için bekle
            
        except Exception as e:
            print(f"  ❌ Hata: {str(e)}")
            continue
    
    print(f"✅ Manuel stok kontrolü tamamlandı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# API Endpoints

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'message': 'Bershka Otomatik Stok Takip API',
        'status': 'running',
        'endpoints': {
            'urunler': '/api/urunler',
            'stok_kontrol': '/api/stok-kontrol',
            'ayarlar': '/api/ayarlar'
        }
    })

# Kullanıcı API'leri
@app.route('/api/kullanicilar', methods=['POST'])
def kayit_ol():
    """Yeni kullanıcı kaydı"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        isim = data.get('isim', '').strip()
        
        if not email:
            return jsonify({'success': False, 'error': 'Email gerekli'}), 400
        
        conn = sqlite3.connect('stok.db')
        c = conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            c.execute('''INSERT INTO kullanicilar (email, isim, olusturma_tarihi)
                        VALUES (?, ?, ?)''', (email, isim, now))
            kullanici_id = c.lastrowid
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'id': kullanici_id,
                'email': email,
                'isim': isim
            }), 201
        except sqlite3.IntegrityError:
            conn.close()
            # Kullanıcı zaten varsa, ID'sini döndür
            c = sqlite3.connect('stok.db').cursor()
            c.execute('SELECT id, email, isim FROM kullanicilar WHERE email = ?', (email,))
            kullanici = c.fetchone()
            if kullanici:
                return jsonify({
                    'success': True,
                    'id': kullanici[0],
                    'email': kullanici[1],
                    'isim': kullanici[2],
                    'message': 'Kullanıcı zaten mevcut'
                }), 200
            return jsonify({'success': False, 'error': 'Kullanıcı oluşturulamadı'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/kullanicilar/<int:kullanici_id>/email-ayarlari', methods=['PUT'])
def email_ayarlari_guncelle(kullanici_id):
    """Kullanıcının email ayarlarını güncelle"""
    try:
        data = request.json
        conn = sqlite3.connect('stok.db')
        c = conn.cursor()
        
        c.execute('''UPDATE kullanicilar 
                    SET smtp_server = ?, smtp_port = ?, email_user = ?, email_password = ?
                    WHERE id = ?''',
                 (data.get('smtp_server', 'smtp.gmail.com'),
                  int(data.get('smtp_port', 587)),
                  data.get('email_user', ''),
                  data.get('email_password', ''),
                  kullanici_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Email ayarları güncellendi'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/kullanicilar/<int:kullanici_id>', methods=['GET'])
def get_kullanici(kullanici_id):
    """Kullanıcı bilgilerini getir"""
    conn = sqlite3.connect('stok.db')
    c = conn.cursor()
    c.execute('SELECT id, email, isim, smtp_server, smtp_port FROM kullanicilar WHERE id = ?', (kullanici_id,))
    kullanici = c.fetchone()
    conn.close()
    
    if not kullanici:
        return jsonify({'success': False, 'error': 'Kullanıcı bulunamadı'}), 404
    
    return jsonify({
        'success': True,
        'id': kullanici[0],
        'email': kullanici[1],
        'isim': kullanici[2],
        'smtp_server': kullanici[3],
        'smtp_port': kullanici[4]
    })

@app.route('/api/urunler', methods=['GET'])
def get_urunler():
    kullanici_id = request.args.get('kullanici_id', type=int)
    
    conn = sqlite3.connect('stok.db')
    c = conn.cursor()
    
    if kullanici_id:
        c.execute('SELECT * FROM urunler WHERE kullanici_id = ? ORDER BY guncelleme_tarihi DESC', (kullanici_id,))
    else:
        c.execute('SELECT * FROM urunler ORDER BY guncelleme_tarihi DESC')
    
    urunler = []
    for row in c.fetchall():
        # Yeni yapı: id, kullanici_id, urun_url, urun_adi, urun_kodu, takip_edilen_beden, stok_durumu, bildirim_gonderildi, son_kontrol_tarihi, olusturma_tarihi, guncelleme_tarihi
        if len(row) >= 11:
            urunler.append({
                'id': row[0],
                'kullanici_id': row[1],
                'urun_url': row[2],
                'urun_adi': row[3],
                'urun_kodu': row[4],
                'takip_edilen_beden': row[5],
                'stok_durumu': row[6],
                'bildirim_gonderildi': bool(row[7]),
                'son_kontrol_tarihi': row[8],
                'olusturma_tarihi': row[9],
                'guncelleme_tarihi': row[10]
            })
        else:
            # Eski yapı (migration için)
            urunler.append({
                'id': row[0],
                'kullanici_id': row[1],
                'urun_url': row[2],
                'urun_adi': row[3],
                'urun_kodu': row[4] if len(row) > 4 else None,
                'takip_edilen_beden': None,
                'stok_durumu': row[5] if len(row) > 5 else 'stokta_yok',
                'bildirim_gonderildi': bool(row[6]) if len(row) > 6 else False,
                'son_kontrol_tarihi': row[7] if len(row) > 7 else None,
                'olusturma_tarihi': row[8] if len(row) > 8 else None,
                'guncelleme_tarihi': row[9] if len(row) > 9 else None
            })
    conn.close()
    return jsonify(urunler)

@app.route('/api/urunler', methods=['POST'])
def add_urun():
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'Geçersiz istek'}), 400
        
        kullanici_id = data.get('kullanici_id')
        if not kullanici_id:
            return jsonify({'success': False, 'error': 'Kullanıcı ID gerekli'}), 400
            
        urun_url = data.get('urun_url', '').strip()
        takip_edilen_beden = data.get('takip_edilen_beden', '').strip() or None
        
        if not urun_url:
            return jsonify({'success': False, 'error': 'Ürün URL\'si gerekli'}), 400
        
        # URL'nin geçerli olup olmadığını kontrol et
        if 'bershka.com' not in urun_url.lower():
            return jsonify({'success': False, 'error': 'Geçerli bir Bershka URL\'si giriniz (örnek: https://www.bershka.com/tr/...)'}), 400
        
        # İlk stok kontrolü yap
        beden_text = f" [Beden: {takip_edilen_beden}]" if takip_edilen_beden else ""
        print(f"🔍 Yeni ürün ekleniyor, stok kontrolü yapılıyor: {urun_url}{beden_text}")
        try:
            result = check_bershka_stock(urun_url, beden=takip_edilen_beden)
            print(f"✅ Stok kontrolü tamamlandı: {result.get('stok_durumu', 'bilinmiyor')}")
        except Exception as e:
            print(f"❌ Stok kontrolü exception: {str(e)}")
            import traceback
            traceback.print_exc()
            result = {
                'urun_adi': 'Ürün adı alınamadı',
                'stok_durumu': 'hata',
                'success': False,
                'error': str(e)
            }
        
        # Hata olsa bile ürünü ekle (sürekli kontrol devam edecek)
        if not result.get('success', False):
            error_msg = result.get('error', 'Stok kontrolü yapılamadı')
            print(f"⚠️ Stok kontrolü başarısız ama ürün eklenecek: {error_msg}")
            # URL'den ürün adını çıkar
            url_match = re.search(r'/([^/]+)\.html', urun_url)
            if url_match:
                result['urun_adi'] = url_match.group(1).replace('-', ' ').title()
            if 'urun_adi' not in result:
                result['urun_adi'] = 'Ürün (Stok kontrolü yapılamadı)'
            if 'stok_durumu' not in result:
                result['stok_durumu'] = 'hata'
            # success=True yap ki ürün eklensin
            result['success'] = True
        
        # Ürün adını ve stok durumunu hazırla
        urun_adi = result.get('urun_adi', 'Ürün adı alınamadı')
        stok_durumu = result.get('stok_durumu', 'stokta_yok')
        
        # Eğer ürün adı alınamadıysa URL'den çıkar
        if not urun_adi or urun_adi == 'Ürün adı alınamadı' or urun_adi == 'Bilinmeyen Ürün':
            url_match = re.search(r'/([^/]+)\.html', urun_url)
            if url_match:
                urun_adi = url_match.group(1).replace('-', ' ').title()
            else:
                urun_adi = 'Ürün'
        
        conn = sqlite3.connect('stok.db')
        c = conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            beden_text = f" [Beden: {takip_edilen_beden}]" if takip_edilen_beden else ""
            print(f"💾 Veritabanına ekleniyor: {urun_adi} (Kullanıcı: {kullanici_id}){beden_text}")
            c.execute('''INSERT INTO urunler 
                        (kullanici_id, urun_url, urun_adi, takip_edilen_beden, stok_durumu, son_kontrol_tarihi, olusturma_tarihi, guncelleme_tarihi)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                     (kullanici_id, urun_url, urun_adi, takip_edilen_beden, stok_durumu, now, now, now))
            urun_id = c.lastrowid
            conn.commit()
            print(f"✅ Ürün veritabanına eklendi: ID={urun_id}")
            conn.close()
            
            # İLK EKLEME: Eğer stok varsa ve bildirim gönderilmemişse, ANINDA bildirim gönder
            if stok_durumu == 'stokta_var':
                beden_text = f" [Beden: {takip_edilen_beden}]" if takip_edilen_beden else ""
                print(f"  🎉🎉🎉 İLK EKLEME - STOK VAR! ANINDA BİLDİRİM: {urun_adi}{beden_text} (Kullanıcı: {kullanici_id})")
                try:
                    # Email gönderme işlemini thread'de yap ki bloklanmasın (ANINDA)
                    def send_email_async():
                        try:
                            urun_adi_with_beden = f"{urun_adi}{beden_text}" if beden_text else urun_adi
                            send_email_notification(urun_adi_with_beden, urun_url, kullanici_id)
                            print(f"  ✅✅✅ İLK EKLEME EMAIL BAŞARIYLA GÖNDERİLDİ: {urun_adi}{beden_text}")
                        except Exception as e:
                            print(f"  ❌ İlk ekleme email gönderme hatası: {str(e)}")
                            import traceback
                            traceback.print_exc()
                    
                    # Thread'de gönder (anında, bloklanmadan)
                    email_thread = threading.Thread(target=send_email_async, daemon=True)
                    email_thread.start()
                    
                    # Veritabanını güncelle (bildirim gönderildi olarak işaretle)
                    conn = sqlite3.connect('stok.db')
                    c = conn.cursor()
                    c.execute('UPDATE urunler SET bildirim_gonderildi = 1 WHERE id = ?', (urun_id,))
                    conn.commit()
                    conn.close()
                    print(f"  ✅ İlk ekleme bildirim bayrağı güncellendi (ID: {urun_id})")
                except Exception as e:
                    print(f"  ❌ İlk ekleme bildirim işlemi başlatılamadı: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
            # Sürekli kontrol başlat
            try:
                start_product_monitoring(urun_id, urun_url, urun_adi, kullanici_id, takip_edilen_beden)
            except Exception as e:
                print(f"⚠️ Sürekli kontrol başlatılamadı: {str(e)}")
            
            message = 'Ürün eklendi ve sürekli kontrol başlatıldı (her 5 saniyede bir)'
            if takip_edilen_beden:
                message += f' - Sadece {takip_edilen_beden} bedeni takip ediliyor'
            if stok_durumu == 'stokta_var':
                message += ' - Stokta var, bildirim gönderildi!'
            
            return jsonify({
                'success': True,
                'id': urun_id,
                'message': message,
                'stok_durumu': stok_durumu,
                'urun_adi': urun_adi,
                'takip_edilen_beden': takip_edilen_beden
            }), 201
        except sqlite3.IntegrityError as e:
            conn.close()
            error_msg = 'Bu ürün URL\'si sizin için zaten ekli'
            print(f"❌ {error_msg}")
            return jsonify({'success': False, 'error': error_msg}), 400
        except Exception as e:
            conn.close()
            error_msg = f'Veritabanı hatası: {str(e)}'
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': error_msg}), 500
    except Exception as e:
        print(f"❌ Genel hata: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Bir hata oluştu: {str(e)}'}), 500

@app.route('/api/urunler/<int:urun_id>', methods=['DELETE'])
def delete_urun(urun_id):
    try:
        # Kullanıcı ID kontrolü (güvenlik için)
        kullanici_id = request.args.get('kullanici_id', type=int)
        
        conn = sqlite3.connect('stok.db')
        c = conn.cursor()
        
        # Önce ürünün var olup olmadığını ve kullanıcıya ait olup olmadığını kontrol et
        if kullanici_id:
            c.execute('SELECT id FROM urunler WHERE id = ? AND kullanici_id = ?', (urun_id, kullanici_id))
        else:
            c.execute('SELECT id FROM urunler WHERE id = ?', (urun_id,))
        
        urun = c.fetchone()
        
        if not urun:
            conn.close()
            return jsonify({'success': False, 'error': 'Ürün bulunamadı veya bu ürünü silme yetkiniz yok'}), 404
        
        # Sürekli kontrolü durdur
        stop_product_monitoring(urun_id)
        
        # Veritabanından sil
        c.execute('DELETE FROM urunler WHERE id = ?', (urun_id,))
        conn.commit()
        conn.close()
        
        print(f"🗑️ Ürün silindi: ID={urun_id} (Kullanıcı: {kullanici_id})")
        return jsonify({'success': True, 'message': 'Ürün başarıyla silindi'})
    except Exception as e:
        print(f"❌ Ürün silme hatası: {str(e)}")
        return jsonify({'success': False, 'error': f'Ürün silinirken hata oluştu: {str(e)}'}), 500

@app.route('/api/stok-kontrol', methods=['POST'])
def manual_stok_kontrol():
    """Manuel stok kontrolü"""
    data = request.json
    urun_id = data.get('urun_id')
    kullanici_id = data.get('kullanici_id')
    
    if urun_id:
        # Tek ürün kontrolü
        conn = sqlite3.connect('stok.db')
        c = conn.cursor()
        if kullanici_id:
            c.execute('SELECT urun_url, urun_adi, kullanici_id FROM urunler WHERE id = ? AND kullanici_id = ?', (urun_id, kullanici_id))
        else:
            c.execute('SELECT urun_url, urun_adi, kullanici_id FROM urunler WHERE id = ?', (urun_id,))
        result = c.fetchone()
        conn.close()
        
        if not result:
            return jsonify({'success': False, 'error': 'Ürün bulunamadı'}), 404
        
        urun_url, urun_adi, urun_kullanici_id = result
        check_result = check_bershka_stock(urun_url)
        
        # Stok durumu değişti mi kontrol et ve bildirim gönder
        conn = sqlite3.connect('stok.db')
        c = conn.cursor()
        c.execute('SELECT stok_durumu, bildirim_gonderildi FROM urunler WHERE id = ?', (urun_id,))
        old_data = c.fetchone()
        
        if old_data:
            eski_stok, bildirim_gonderildi = old_data
            if eski_stok == 'stokta_yok' and check_result['stok_durumu'] == 'stokta_var':
                if bildirim_gonderildi == 0:
                    send_email_notification(check_result.get('urun_adi', urun_adi), urun_url, urun_kullanici_id)
                    c.execute('UPDATE urunler SET bildirim_gonderildi = 1 WHERE id = ?', (urun_id,))
        
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute('''UPDATE urunler 
                    SET stok_durumu = ?, son_kontrol_tarihi = ?, guncelleme_tarihi = ?
                    WHERE id = ?''',
                 (check_result['stok_durumu'], now, now, urun_id))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'stok_durumu': check_result['stok_durumu'],
            'urun_adi': check_result.get('urun_adi', urun_adi)
        })
    else:
        # Tüm ürünleri kontrol et (kullanıcı ID varsa sadece o kullanıcının ürünleri)
        if kullanici_id:
            conn = sqlite3.connect('stok.db')
            c = conn.cursor()
            c.execute('SELECT id, urun_url, urun_adi, stok_durumu, bildirim_gonderildi, kullanici_id, takip_edilen_beden FROM urunler WHERE kullanici_id = ?', (kullanici_id,))
            urunler = c.fetchall()
            conn.close()
            
            for urun_id, urun_url, urun_adi, eski_stok, bildirim_gonderildi, urun_kullanici_id, beden in urunler:
                try:
                    beden_text = f" [Beden: {beden}]" if beden else ""
                    print(f"  📦 Kontrol ediliyor: {urun_adi or urun_url}{beden_text}")
                    check_result = check_bershka_stock(urun_url, beden=beden)
                    if check_result.get('success'):
                        conn = sqlite3.connect('stok.db')
                        c = conn.cursor()
                        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        if eski_stok == 'stokta_yok' and check_result['stok_durumu'] == 'stokta_var':
                            if bildirim_gonderildi == 0:
                                send_email_notification(check_result.get('urun_adi', urun_adi), urun_url, urun_kullanici_id)
                                c.execute('UPDATE urunler SET bildirim_gonderildi = 1 WHERE id = ?', (urun_id,))
                        
                        c.execute('''UPDATE urunler 
                                    SET stok_durumu = ?, son_kontrol_tarihi = ?, guncelleme_tarihi = ?
                                    WHERE id = ?''',
                                 (check_result['stok_durumu'], now, now, urun_id))
                        conn.commit()
                        conn.close()
                except:
                    pass
        else:
            check_all_products()
        return jsonify({'success': True, 'message': 'Tüm ürünler kontrol edildi'})

@app.route('/api/ayarlar', methods=['GET'])
def get_ayarlar():
    """Kontrol aralığı gibi ayarları döndürür"""
    return jsonify({
        'kontrol_araligi_saniye': 30,  # Her 30 saniyede bir kontrol
        'kontrol_tipi': 'sürekli_anında',
        'aktif_urun_sayisi': len(urun_threads),
        'son_kontrol': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

if __name__ == '__main__':
    init_db()
    print("🚀 Bershka Otomatik Stok Takip Sistemi başlatılıyor...")
    print("📧 Email bildirimleri için .env dosyasını yapılandırın")
    print("⚡ ANINDA KONTROL: Her ürün için sürekli kontrol (her 5 saniyede bir)")
    print("🎯 Stok geldiğinde ANINDA bildirim gönderilecek!")
    
    # Mevcut tüm ürünler için sürekli kontrol başlat
    start_all_monitoring()
    
    # Port'u environment variable'dan al (deploy için)
    port = int(os.getenv('PORT', 5001))
    host = os.getenv('HOST', '127.0.0.1')
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    app.run(debug=debug, host=host, port=port, use_reloader=False)
