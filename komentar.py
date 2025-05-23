from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time
import os
import random
import re
from colorama import Fore, init
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# Inisialisasi Colorama
init(autoreset=True)

# Warna untuk teks terminal
B = Fore.BLUE
W = Fore.WHITE
R = Fore.RED
G = Fore.GREEN
Y = Fore.YELLOW

def pastikan_browser_tetap_aktif(driver):
    """
    Fungsi untuk memastikan browser tetap aktif meskipun tidak di foreground
    """
    try:
        # print(f"{Y}Memastikan browser tetap aktif di komentar.py...{W}")
        
        # Tambahkan script untuk mencegah throttling saat tab tidak aktif
        anti_throttle_script = """
        // Simpan referensi ke fungsi requestAnimationFrame asli
        const originalRAF = window.requestAnimationFrame;
        
        // Buat fungsi untuk memastikan browser tetap aktif
        function keepBrowserActive() {
            // Panggil requestAnimationFrame untuk menjaga aktivitas browser
            originalRAF(keepBrowserActive);
            
            // Tambahkan sedikit aktivitas DOM untuk mencegah throttling
            if (!window._lastActiveTime || Date.now() - window._lastActiveTime > 500) {
                window._lastActiveTime = Date.now();
                
                // Buat elemen dummy dan hapus untuk memaksa aktivitas DOM
                const dummy = document.createElement('div');
                document.body.appendChild(dummy);
                document.body.removeChild(dummy);
                
                // Log aktivitas (opsional, untuk debugging)
                console.log('Menjaga browser tetap aktif: ' + new Date().toISOString());
            }
        }
        
        // Mulai loop untuk menjaga aktivitas
        keepBrowserActive();
        
        // Tambahkan listener untuk Page Visibility API
        document.addEventListener('visibilitychange', function() {
            if (document.hidden) {
                console.log('Halaman tidak terlihat, memastikan tetap aktif');
                // Tingkatkan frekuensi aktivitas saat halaman tidak terlihat
                window._lastActiveTime = 0;
            }
        });
        
        return "Script anti-throttling berhasil diterapkan";
        """
        
        result = driver.execute_script(anti_throttle_script)
        print(f"{G}Browser akan tetap aktif meskipun tidak di foreground: {result}{W}")
        return True
    except Exception as e:
        print(f"{R}Gagal menerapkan script anti-throttling: {e}{W}")
        return False

def jaga_fokus_browser(driver):
    """
    Fungsi untuk menjaga fokus browser secara periodik
    """
    try:
        # Gunakan JavaScript untuk memfokuskan window
        driver.execute_script("""
        // Fokuskan window
        window.focus();
        
        // Klik pada body untuk memastikan fokus
        if (document.body) {
            document.body.click();
        }
        
        // Scroll sedikit untuk memicu aktivitas
        window.scrollBy(0, 1);
        window.scrollBy(0, -1);
        
        return "Browser difokuskan";
        """)
        
        return True
    except Exception as e:
        print(f"{R}Gagal menjaga fokus browser: {e}{W}")
        return False

def cek_koneksi_browser(driver, timeout=5):
    """
    Memeriksa apakah koneksi ke browser masih aktif
    
    Args:
        driver: WebDriver Selenium
        timeout: Timeout dalam detik
        
    Returns:
        True jika koneksi aktif, False jika terputus
    """
    try:
        # Coba operasi sederhana dengan timeout
        driver.execute_script("return navigator.userAgent;")
        return True
    except Exception as e:
        if "Connection" in str(e) or "HTTPConnectionPool" in str(e):
            return False
        # Jika error bukan masalah koneksi, anggap koneksi masih aktif
        return True

def coba_reconnect_browser(driver, url, max_attempts=3):
    """
    Fungsi untuk mencoba menghubungkan kembali browser jika koneksi terputus
    
    Args:
        driver: WebDriver Selenium
        url: URL terakhir yang dibuka
        max_attempts: Jumlah maksimum percobaan reconnect
        
    Returns:
        driver baru jika berhasil, None jika gagal
    """
    print(f"{Y}Koneksi ke browser terputus. Mencoba menghubungkan kembali...{W}")
    
    for attempt in range(max_attempts):
        try:
            print(f"{Y}Percobaan reconnect ke-{attempt+1}/{max_attempts}...{W}")
            
            # Coba tutup driver yang ada (mungkin sudah tidak responsif)
            try:
                driver.quit()
            except:
                pass
            
            # Inisialisasi driver baru
            try:
                from main import inisialisasi_driver
                new_driver = inisialisasi_driver()
            except ImportError:
                print(f"{R}Tidak dapat mengimpor inisialisasi_driver dari main.py{W}")
                # Implementasi fallback jika import gagal
                import undetected_chromedriver as uc
                options = uc.ChromeOptions()
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                new_driver = uc.Chrome(options=options)
            
            # Buka URL terakhir
            new_driver.get(url)
            print(f"{G}Berhasil menghubungkan kembali dan membuka URL: {url}{W}")
            
            # Pastikan browser tetap aktif
            pastikan_browser_tetap_aktif(new_driver)
            
            return new_driver
            
        except Exception as e:
            print(f"{R}Gagal menghubungkan kembali pada percobaan ke-{attempt+1}: {e}{W}")
            time.sleep(3)  # Tunggu sebentar sebelum mencoba lagi
    
    print(f"{R}Gagal menghubungkan kembali setelah {max_attempts} percobaan{W}")
    return None

def lanjutkan_komentar(driver, url):
    """
    Fungsi untuk melanjutkan proses komentar setelah pendaftaran berhasil
    """
    try:
        print(f"{Y}=== {G}Memulai proses komentar untuk URL: {W}{url} {Y}===")
        
        # Cek koneksi sebelum melanjutkan
        if not cek_koneksi_browser(driver):
            print(f"{R}Koneksi ke browser terputus sebelum memulai proses komentar{W}")
            # Coba reconnect
            new_driver = coba_reconnect_browser(driver, url)
            if new_driver:
                driver = new_driver
            else:
                print(f"{R}Tidak dapat melanjutkan proses karena koneksi terputus{W}")
                return
        
        # Terapkan anti-throttling dengan penanganan error
        try:
            pastikan_browser_tetap_aktif(driver)
        except Exception as e:
            print(f"{Y}Peringatan: Gagal menerapkan anti-throttling: {e}{W}")
            # Cek apakah koneksi terputus
            if not cek_koneksi_browser(driver):
                new_driver = coba_reconnect_browser(driver, url)
                if new_driver:
                    driver = new_driver
                    # Coba lagi dengan driver baru
                    return lanjutkan_komentar(driver, url)
        
        # Jaga fokus browser dengan penanganan error
        try:
            jaga_fokus_browser(driver)
        except Exception as e:
            print(f"{Y}Peringatan: Gagal menjaga fokus browser: {e}{W}")
            # Cek apakah koneksi terputus
            if not cek_koneksi_browser(driver):
                new_driver = coba_reconnect_browser(driver, url)
                if new_driver:
                    driver = new_driver
                    # Coba lagi dengan driver baru
                    return lanjutkan_komentar(driver, url)
        
        # Tunggu sebentar untuk memastikan halaman dimuat sepenuhnya
        time.sleep(5)
        
        # Cek koneksi sebelum mengambil HTML
        if not cek_koneksi_browser(driver):
            print(f"{R}Koneksi ke browser terputus sebelum mengambil HTML{W}")
            # Coba reconnect
            new_driver = coba_reconnect_browser(driver, url)
            if new_driver:
                driver = new_driver
                # Coba lagi dengan driver baru
                return lanjutkan_komentar(driver, url)
            else:
                print(f"{R}Tidak dapat melanjutkan proses karena koneksi terputus{W}")
                return
        
        # Dapatkan HTML halaman
        try:
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
        except Exception as e:
            print(f"{R}Gagal mendapatkan HTML halaman: {e}{W}")
            # Cek apakah koneksi terputus
            if not cek_koneksi_browser(driver):
                new_driver = coba_reconnect_browser(driver, url)
                if new_driver:
                    driver = new_driver
                    # Coba lagi dengan driver baru
                    return lanjutkan_komentar(driver, url)
            else:
                # Jika koneksi masih aktif tapi gagal mendapatkan HTML, coba refresh
                try:
                    driver.refresh()
                    time.sleep(5)
                    return lanjutkan_komentar(driver, url)
                except:
                    pass
        
        # Cari elemen <p> dengan class yang diminta
        kotak_komentar = soup.find('p', class_='tAaif jkMRy is-editor-empty')
        
        if kotak_komentar:
            # print(f"{G}Kotak komentar ditemukan!{W}")
            
            # Cari elemen yang sama di Selenium
            try:
                selector = "p.tAaif.jkMRy.is-editor-empty"
                elemen_komentar = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                
                # Klik pada kotak komentar
                # print(f"{Y}Mengklik kotak komentar...{W}")
                elemen_komentar.click()
                print(f"{G}Kotak komentar berhasil diklik{W}")
                time.sleep(2)
                
                # Proses komentar dengan elemen yang ditemukan
                proses_komentar(driver, elemen_komentar)
                
            except TimeoutException:
                print(f"{R}Timeout: Tidak dapat menemukan kotak komentar dengan Selenium{W}")
            except Exception as e:
                print(f"{R}Terjadi kesalahan saat mengklik kotak komentar: {e}{W}")
        else:
            print(f"{R}Kotak komentar dengan class='tAaif jkMRy is-editor-empty' tidak ditemukan{W}")
            
            # Coba cari dengan pendekatan alternatif
            try:
                print(f"{Y}Mencari elemen dengan data-placeholder='Write a comment...'...{W}")
                comment_placeholder = driver.find_element(By.CSS_SELECTOR, "[data-placeholder='Write a comment...']")
                print(f"{G}Elemen dengan data-placeholder ditemukan!{W}")
                
                comment_placeholder.click()
                print(f"{G}Elemen berhasil diklik{W}")
                time.sleep(2)
                
                # Proses komentar dengan elemen yang ditemukan
                proses_komentar(driver, comment_placeholder)
                
            except Exception as e:
                print(f"{R}Pendekatan alternatif gagal: {e}{W}")
                
                # Jika semua pendekatan gagal, tetap simpan URL ke komen-done.txt
                # untuk menandai bahwa URL ini sudah dicoba
                simpan_url_ke_file(driver)
    
    except Exception as e:
        print(f"{R}Terjadi kesalahan dalam proses komentar: {e}{W}")
        
        # Cek apakah error disebabkan oleh koneksi terputus
        if "Connection" in str(e) or "HTTPConnectionPool" in str(e):
            print(f"{Y}Error koneksi terdeteksi, mencoba menghubungkan kembali...{W}")
            new_driver = coba_reconnect_browser(driver, url)
            if new_driver:
                driver = new_driver
                # Coba lagi dengan driver baru
                return lanjutkan_komentar(driver, url)
        
        # Jika terjadi kesalahan, tetap simpan URL ke komen-done.txt
        # untuk menandai bahwa URL ini sudah dicoba
        try:
            simpan_url_ke_file(driver)
        except:
            pass

def proses_komentar(driver, elemen_komentar):
    """
    Fungsi untuk memproses komentar setelah menemukan dan mengklik kotak komentar
    """
    # Jaga fokus browser
    jaga_fokus_browser(driver)
    
    # Baca pesan dari file komen.txt
    if not os.path.exists('komen.txt'):
        print(f"{R}File komen.txt tidak ditemukan{W}")
        return
        
    with open('komen.txt', 'r', encoding='utf-8') as file:
        pesan_list = file.readlines()
        
    # Bersihkan pesan dari whitespace
    pesan_list = [pesan.strip() for pesan in pesan_list if pesan.strip()]
    
    if not pesan_list:
        print(f"{R}File komen.txt kosong{W}")
        return
        
    # Pilih pesan secara acak
    pesan_original = random.choice(pesan_list)
    
    # Cari pola [url]kata[link:URL] dalam pesan
    url_pattern = r'\[url\](.*?)\[link:(.*?)\]'
    url_matches = re.findall(url_pattern, pesan_original)
    
    # Jika ada pola URL yang ditemukan
    if url_matches:
        print(f"{G}Format URL khusus ditemukan dalam pesan{W}")
        
        # Simpan informasi kata dan URL yang akan dilink
        kata_untuk_link = []
        url_untuk_link = []
        
        for match in url_matches:
            kata = match[0]
            url_link = match[1]
            kata_untuk_link.append(kata)
            url_untuk_link.append(url_link)
            print(f"{Y}Kata yang akan diberi link: {kata} -> {url_link}{W}")
        
        # Hapus format khusus dari pesan
        pesan_untuk_tampil = re.sub(url_pattern, r'\1', pesan_original)
        print(f"{Y}Pesan yang akan dimasukkan: {pesan_untuk_tampil}{W}")
        
        # Masukkan pesan ke kotak komentar
        actions = ActionChains(driver)
        actions.click(elemen_komentar)
        actions.send_keys(pesan_untuk_tampil)
        actions.perform()
        print(f"{G}Pesan berhasil dimasukkan{W}")
        
        # Proses setiap kata yang perlu diberi link
        for i, kata in enumerate(kata_untuk_link):
            url_link = url_untuk_link[i]
            print(f"{Y}Memproses kata '{kata}' untuk diberi link '{url_link}'...{W}")
            time.sleep(2)
            
            # Klik pada elemen komentar untuk memastikan fokus
            actions = ActionChains(driver)
            actions.click(elemen_komentar)
            actions.perform()
            time.sleep(1)
            
            # Blok teks yang akan diberi link
            if blok_teks(driver, elemen_komentar, kata):
                # Klik tombol link
                if klik_tombol_link(driver):
                    # Masukkan URL
                    if masukkan_url(driver, url_link):
                        # Klik toggle switch
                        if klik_toggle_switch(driver):
                            # Klik tombol save
                            if klik_tombol_save(driver):
                                # Klik tombol underline
                                klik_tombol_underline(driver)
    else:
        # Jika tidak ada format khusus, gunakan pesan asli
        print(f"{Y}Tidak ada format URL khusus dalam pesan. Menggunakan pesan asli.{W}")
        actions = ActionChains(driver)
        actions.click(elemen_komentar)
        actions.send_keys(pesan_original)
        actions.perform()
        print(f"{G}Pesan berhasil dimasukkan{W}")

def blok_teks(driver, elemen, kata):
    """
    Fungsi untuk memblok teks tertentu dalam elemen
    """
    # Jaga fokus browser sebelum operasi penting
    jaga_fokus_browser(driver)
    
    print(f"{Y}Memilih teks '{kata}' dengan JavaScript...{W}")
    select_script = """
    var element = arguments[0];
    var text = element.textContent || element.innerText;
    var searchText = arguments[1];
    
    // Buat selection range
    var range = document.createRange();
    var sel = window.getSelection();
    
    // Cari text node yang berisi kata yang dicari
    var found = false;
    function findTextNode(node, searchText) {
        if (node.nodeType === 3) { // Text node
            var content = node.textContent;
            var idx = content.indexOf(searchText);
            if (idx !== -1) {
                range.setStart(node, idx);
                range.setEnd(node, idx + searchText.length);
                sel.removeAllRanges();
                sel.addRange(range);
                return true;
            }
        } else if (node.nodeType === 1) { // Element node
            for (var i = 0; i < node.childNodes.length; i++) {
                if (findTextNode(node.childNodes[i], searchText)) {
                    return true;
                }
            }
        }
        return false;
    }
    
    found = findTextNode(element, searchText);
    return found;
    """
    
    selection_successful = driver.execute_script(select_script, elemen, kata)
    
    if selection_successful:
        print(f"{G}Teks '{kata}' berhasil diblok{W}")
        time.sleep(2)
        return True
    else:
        print(f"{R}Gagal memblok teks '{kata}'{W}")
        return False

def klik_tombol_link(driver):
    """
    Fungsi untuk mengklik tombol link
    """
    # Jaga fokus browser sebelum operasi penting
    jaga_fokus_browser(driver)
    
    # print(f"{Y}Mencari tombol link...{W}")
    try:
        link_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-hook="text-button-link"]'))
        )
        
        # print(f"{Y}Mengklik tombol link...{W}")
        link_button.click()
        print(f"{G}Tombol link berhasil diklik{W}")
        time.sleep(2)
        return True
    except Exception as e:
        print(f"{R}Gagal menemukan atau mengklik tombol link: {e}{W}")
        return False

def masukkan_url(driver, url_link):
    """
    Fungsi untuk memasukkan URL ke dalam input
    """
    # Jaga fokus browser sebelum operasi penting
    jaga_fokus_browser(driver)
    
    try:
        # print(f"{Y}Mencari elemen modal link dengan data-hook='link-modal-url-input'...{W}")
        
        # Tunggu sebentar agar dialog muncul sepenuhnya
        time.sleep(2)
        
        # Cari div parent dengan data-hook="link-modal-url-input"
        link_modal_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-hook="link-modal-url-input"]'))
        )
        # print(f"{G}Elemen modal link ditemukan!{W}")
        
        # Klik pada div parent terlebih dahulu (opsional, tergantung kebutuhan)
        link_modal_div.click()
        print(f"{G}Modal link berhasil diklik{W}")
        time.sleep(1)
        
        # Cari input di dalam div parent
        url_input = link_modal_div.find_element(By.CSS_SELECTOR, 'input[data-hook="wsr-input"]')
        # print(f"{G}Input URL ditemukan!{W}")
        
        # Klik pada input URL
        url_input.click()
        # print(f"{G}Input URL berhasil diklik{W}")
        time.sleep(1)
        
        # Clear dan masukkan URL
        url_input.clear()
        url_input.send_keys(url_link)
        print(f"{G}URL {Y}'{url_link}' {G}berhasil dimasukkan")
        
        # Tunggu sebentar
        time.sleep(2)
        return True
        
    except Exception as e:
        print(f"{R}Gagal menemukan atau berinteraksi dengan input URL: {e}{W}")
        # Coba pendekatan alternatif jika pendekatan utama gagal
        try:
            print(f"{Y}Mencoba pendekatan alternatif untuk menemukan input URL...{W}")
            # Cari langsung input dengan data-hook="wsr-input"
            url_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-hook="wsr-input"]'))
            )
            
            # Klik pada input URL
            url_input.click()
            print(f"{G}Input URL berhasil diklik dengan pendekatan alternatif{W}")
            time.sleep(1)
            
            # Clear dan masukkan URL
            url_input.clear()
            url_input.send_keys(url_link)
            print(f"{G}URL '{url_link}' berhasil dimasukkan dengan pendekatan alternatif{W}")
            
            # Tunggu sebentar
            time.sleep(2)
            return True
        except Exception as e2:
            print(f"{R}Pendekatan alternatif juga gagal: {e2}{W}")
            return False

def klik_toggle_switch(driver):
    """
    Fungsi untuk mengklik toggle switch pada index 1
    """
    # print(f"{Y}Mencari toggle switch dengan data-hook='toggle-switch-input' (index 1)...{W}")
    try:
        # Cari semua toggle switch
        toggle_switches = driver.find_elements(By.CSS_SELECTOR, '[data-hook="toggle-switch-input"]')
        
        if len(toggle_switches) >= 2:
            # Klik pada toggle switch dengan index 1 (elemen kedua)
            toggle_switches[1].click()
            print(f"{G}Toggle switch pada index 1 berhasil diklik{W}")
            time.sleep(1)
            return True
        elif len(toggle_switches) == 1:
            print(f"{Y}Hanya ditemukan 1 toggle switch, mengklik yang tersedia...{W}")
            toggle_switches[0].click()
            print(f"{G}Toggle switch tunggal berhasil diklik{W}")
            time.sleep(1)
            return True
        else:
            print(f"{R}Tidak ditemukan toggle switch{W}")
            
            # Coba pendekatan alternatif dengan JavaScript
            print(f"{Y}Mencoba pendekatan JavaScript untuk toggle switch...{W}")
            toggle_script = """
            var toggles = document.querySelectorAll('[data-hook="toggle-switch-input"]');
            if (toggles.length >= 2) {
                toggles[1].click();
                return "Berhasil mengklik toggle switch pada index 1";
            } else if (toggles.length == 1) {
                toggles[0].click();
                return "Berhasil mengklik toggle switch tunggal";
            }
            return "Tidak ditemukan toggle switch";
            """
            result = driver.execute_script(toggle_script)
            print(f"{G}Hasil JavaScript: {result}{W}")
            return "Berhasil" in result
            
    except Exception as toggle_error:
        print(f"{R}Gagal menemukan atau mengklik toggle switch: {toggle_error}{W}")
        
        # Coba pendekatan alternatif untuk toggle switch
        try:
            print(f"{Y}Mencoba pendekatan alternatif untuk toggle switch...{W}")
            # Coba cari dengan JavaScript yang lebih spesifik
            toggle_script = """
            // Coba temukan semua toggle switch
            var toggles = document.querySelectorAll('[data-hook="toggle-switch-input"]');
            console.log("Jumlah toggle switch ditemukan:", toggles.length);
            
            if (toggles.length >= 2) {
                // Coba klik yang kedua
                try {
                    toggles[1].click();
                    return "Berhasil mengklik toggle switch pada index 1";
                } catch(e) {
                    // Jika gagal, coba klik parent element
                    try {
                        toggles[1].parentNode.click();
                        return "Berhasil mengklik parent dari toggle switch pada index 1";
                    } catch(e2) {
                        return "Gagal mengklik toggle switch dan parent: " + e2.message;
                    }
                }
            } else if (toggles.length == 1) {
                // Jika hanya ada satu, klik yang ada
                try {
                    toggles[0].click();
                    return "Berhasil mengklik toggle switch tunggal";
                } catch(e) {
                    return "Gagal mengklik toggle switch tunggal: " + e.message;
                }
            }
            return "Tidak ditemukan toggle switch";
            """
            result = driver.execute_script(toggle_script)
            print(f"{G}Hasil JavaScript alternatif: {result}{W}")
            return "Berhasil" in result
        except Exception as js_error:
            print(f"{R}Pendekatan JavaScript untuk toggle switch gagal: {js_error}{W}")
            return False

def klik_tombol_save(driver):
    """
    Fungsi untuk mengklik tombol save
    """
    # print(f"{Y}Mencari tombol save dengan data-hook='link-modal-save-button'...{W}")
    try:
        # Cari tombol save
        save_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-hook="link-modal-save-button"]'))
        )
        
        # Klik tombol save
        save_button.click()
        print(f"{G}Tombol save berhasil diklik{W}")
        time.sleep(2)
        print(f"{G}Proses komentar berhasil dijalankan{W}")
        return True
        
    except Exception as save_error:
        print(f"{R}Gagal menemukan atau mengklik tombol save: {save_error}{W}")
        
        # Coba pendekatan alternatif dengan JavaScript
        try:
            print(f"{Y}Mencoba pendekatan JavaScript untuk tombol save...{W}")
            save_script = """
            var saveButton = document.querySelector('[data-hook="link-modal-save-button"]');
            if (saveButton) {
                saveButton.click();
                return "Berhasil mengklik tombol save dengan JavaScript";
            }
            return "Tombol save tidak ditemukan dengan JavaScript";
            """
            result = driver.execute_script(save_script)
            print(f"{G}Hasil JavaScript untuk tombol save: {result}{W}")
            
            if "Berhasil" in result:
                time.sleep(2)
                print(f"{G}Proses komentar berhasil dijalankan dengan JavaScript{W}")
                return True
            return False
            
        except Exception as js_save_error:
            print(f"{R}Pendekatan JavaScript untuk tombol save gagal: {js_save_error}{W}")
            return False

def klik_tombol_underline(driver):
    """
    Fungsi untuk mengklik tombol underline
    """
    # print(f"{Y}Mencari tombol underline dengan data-hook='text-button-underline active'...{W}")
    try:
        # Tunggu sebentar setelah klik tombol save
        time.sleep(2)
        
        # Cari tombol underline
        underline_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-hook="text-button-underline active"]'))
        )
        
        # Klik tombol underline
        underline_button.click()
        print(f"{G}Tombol underline berhasil diklik{W}")
        time.sleep(1)
        
        # Setelah mengklik tombol underline, klik tombol post komentar
        klik_tombol_post(driver)
        return True
        
    except Exception as underline_error:
        print(f"{R}Gagal menemukan atau mengklik tombol underline: {underline_error}{W}")
        
        # Coba pendekatan alternatif dengan JavaScript
        try:
            print(f"{Y}Mencoba pendekatan JavaScript untuk tombol underline...{W}")
            underline_script = """
            var underlineButton = document.querySelector('[data-hook="text-button-underline active"]');
            if (underlineButton) {
                underlineButton.click();
                return "Berhasil mengklik tombol underline dengan JavaScript";
            }
            
            // Coba cari dengan selector yang lebih fleksibel jika yang pertama gagal
            var altButtons = document.querySelectorAll('[data-hook*="text-button-underline"]');
            if (altButtons.length > 0) {
                altButtons[0].click();
                return "Berhasil mengklik tombol underline alternatif dengan JavaScript";
            }
            
            return "Tombol underline tidak ditemukan dengan JavaScript";
            """
            result = driver.execute_script(underline_script)
            print(f"{G}Hasil JavaScript untuk tombol underline: {result}{W}")
            
            if "Berhasil" in result:
                # Jika berhasil mengklik tombol underline dengan JavaScript, klik tombol post
                klik_tombol_post(driver)
                return True
            return False
            
        except Exception as js_underline_error:
            print(f"{R}Pendekatan JavaScript untuk tombol underline gagal: {js_underline_error}{W}")
            
            # Meskipun gagal mengklik tombol underline, tetap coba klik tombol post
            klik_tombol_post(driver)
            return False

def klik_tombol_post(driver):
    """
    Fungsi untuk mengklik tombol post komentar
    """
    # print(f"{Y}Mencari tombol post komentar dengan data-hook='primary-btn'...{W}")
    try:
        # Tunggu sebentar
        time.sleep(2)
        
        # Cari tombol post
        post_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-hook="primary-btn"]'))
        )
        
        # Klik tombol post
        post_button.click()
        print(f"{G}Tombol post komentar berhasil diklik{W}")
        
        # Tunggu sebentar untuk memastikan komentar terkirim
        time.sleep(5)
        
        # Simpan URL browser ke komen-done.txt
        simpan_url_ke_file(driver)
        
        return True
        
    except Exception as post_error:
        print(f"{R}Gagal menemukan atau mengklik tombol post komentar: {post_error}{W}")
        
        # Coba pendekatan alternatif dengan JavaScript
        try:
            print(f"{Y}Mencoba pendekatan JavaScript untuk tombol post komentar...{W}")
            post_script = """
            var postButton = document.querySelector('[data-hook="primary-btn"]');
            if (postButton) {
                postButton.click();
                return "Berhasil mengklik tombol post komentar dengan JavaScript";
            }
            return "Tombol post komentar tidak ditemukan dengan JavaScript";
            """
            result = driver.execute_script(post_script)
            print(f"{G}Hasil JavaScript untuk tombol post komentar: {result}{W}")
            
            if "Berhasil" in result:
                # Tunggu sebentar untuk memastikan komentar terkirim
                time.sleep(5)
                
                # Simpan URL browser ke komen-done.txt
                simpan_url_ke_file(driver)
                
                return True
            return False
            
        except Exception as js_post_error:
            print(f"{R}Pendekatan JavaScript untuk tombol post komentar gagal: {js_post_error}{W}")
            return False

def simpan_url_ke_file(driver):
    """
    Fungsi untuk menyimpan URL browser saat ini ke file komen-done.txt
    """
    try:
        # Dapatkan URL saat ini
        current_url = driver.current_url
        
        # Simpan URL ke file komen-done.txt
        with open('komen-done.txt', 'a', encoding='utf-8') as file:
            file.write(current_url + '\n')
            
        print(f"{G}URL {W}'{current_url}' {G}berhasil disimpan ke komen-done.txt")
        
        # Lanjutkan ke modul logout.py
        try:
            print(f"\n{W}Melanjutkan proses ke modul logout.py...")
            import logout
            logout.lakukan_logout(driver, current_url)
        except ImportError:
            print(f"{R}Modul logout.py tidak ditemukan. Pastikan file logout.py ada di direktori yang sama.{W}")
        except Exception as e:
            print(f"{R}Terjadi kesalahan saat menjalankan modul logout.py: {e}{W}")
        
    except Exception as e:
        print(f"{R}Gagal menyimpan URL ke komen-done.txt: {e}{W}")

# Jika file ini dijalankan langsung (bukan diimpor)
if __name__ == "__main__":
    print(f"{Y}File ini dirancang untuk diimpor oleh daftar.py{W}")
    print(f"{Y}Jalankan main.py untuk memulai proses lengkap.{W}")