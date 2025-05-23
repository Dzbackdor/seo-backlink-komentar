from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import random
import string
from colorama import Fore, init
from bs4 import BeautifulSoup

# Initialize Colorama
init(autoreset=True)

# Colors for terminal text
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
        # print(f"{Y}Memastikan browser tetap aktif di daftar.py...{W}")
        
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

def lanjutkan_proses(driver, url):
    """
    Fungsi untuk melanjutkan proses pendaftaran setelah klik elemen signup.
    
    Args:
        driver: WebDriver Selenium
        url: URL saat ini
    """
    print(f"{Y}=== {G}Melanjutkan proses pendaftaran di {W}{url} {Y}===")
    
    # Cek koneksi sebelum melanjutkan
    if not cek_koneksi_browser(driver):
        print(f"{R}Koneksi ke browser terputus sebelum memulai proses pendaftaran{W}")
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
                return lanjutkan_proses(driver, url)
    
    # Jaga fokus browser
    jaga_fokus_browser(driver)
    
    # Menggunakan BeautifulSoup untuk mencari elemen dengan ID yang mengandung "googleSM_ROOT"
    # print(f"{Y}Mencari elemen dengan ID yang mengandung 'googleSM_ROOT' menggunakan BeautifulSoup...{W}")
    
    # Ambil HTML saat ini
    html_saat_ini = driver.page_source
    
    # Parse dengan BeautifulSoup
    soup = BeautifulSoup(html_saat_ini, 'html.parser')
    
    # Cari elemen dengan ID yang mengandung "googleSM_ROOT"
    elemen_bs4 = soup.find(lambda tag: tag.has_attr('id') and 'googleSM_ROOT' in tag['id'])
    
    if elemen_bs4:
        # Jika elemen ditemukan dengan BeautifulSoup, dapatkan ID lengkapnya
        elemen_id = elemen_bs4['id']
        print(f"{G}Elemen dengan ID yang mengandung 'googleSM_ROOT' ditemukan: {elemen_id}{W}")
        
        # Gunakan Selenium untuk menemukan elemen dengan ID yang sama dan klik
        try:
            elemen_selenium = driver.find_element(By.ID, elemen_id)
            
            # Scroll ke elemen tersebut
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemen_selenium)
            # print(f"{Y}Scrolling ke elemen target{W}")
            time.sleep(1)
            
            # Klik elemen
            # print(f"{Y}Mengklik elemen dengan ID '{elemen_id}'...{W}")
            elemen_selenium.click()
            print(f"{G}Elemen dengan ID '{elemen_id}' berhasil diklik!")
            
            # Tunggu sebentar setelah klik
            time.sleep(2)
            
            # Proses login Google pada popup
            handle_google_login(driver, "email-anda", "password-anda") # Gunakan email baru dan jangan menggunakan fitur 2fa
            
        except Exception as e:
            print(f"{R}Gagal mengklik elemen dengan ID '{elemen_id}': {e}{W}")
            
            # Coba alternatif dengan JavaScript click
            try:
                print(f"{Y}Mencoba klik dengan JavaScript...{W}")
                driver.execute_script("arguments[0].click();", driver.find_element(By.ID, elemen_id))
                print(f"{G}Elemen dengan ID '{elemen_id}' berhasil diklik dengan JavaScript!{W}")
                time.sleep(2)
                
                # Proses login Google pada popup
                handle_google_login(driver, "email-anda", "password-anda") # Gunakan email baru dan jangan menggunakan fitur 2fa
                
            except Exception as e2:
                print(f"{R}Gagal mengklik elemen dengan JavaScript: {e2}{W}")
    else:
        print(f"{R}Elemen dengan ID yang mengandung 'googleSM_ROOT' tidak ditemukan.{W}")

def handle_google_login(driver, email, password):
    """
    Fungsi untuk menangani login Google pada popup dengan penanganan koneksi terputus.
    
    Args:
        driver: WebDriver Selenium
        email: Email untuk login
        password: Password untuk login
    """
    try:
        print(f"{Y}Menunggu popup login Google muncul...")
        
        # Tunggu dan beralih ke window popup
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        window_handles = driver.window_handles
        
        print(f"{G}Popup terdeteksi, beralih ke window popup...{W}")
        driver.switch_to.window(window_handles[1])
        # Tambahan untuk atur posisi & ukuran popup
        driver.set_window_size(100, 100)
        driver.set_window_position(0, 0)
        
        # Cek koneksi sebelum melanjutkan
        if not cek_koneksi_browser(driver):
            print(f"{R}Koneksi ke browser terputus setelah beralih ke popup{W}")
            # Coba reconnect
            new_driver = coba_reconnect_browser(driver, driver.current_url)
            if new_driver:
                driver = new_driver
                # Mulai ulang proses login
                return handle_google_login(driver, email, password)
            else:
                raise Exception("Tidak dapat menghubungkan kembali browser")
        
        # Terapkan anti-throttling pada popup
        try:
            pastikan_browser_tetap_aktif(driver)
        except Exception as e:
            print(f"{Y}Peringatan: Gagal menerapkan anti-throttling: {e}{W}")
            # Lanjutkan meskipun anti-throttling gagal
        
        # Jaga fokus browser pada popup
        try:
            jaga_fokus_browser(driver)
        except Exception as e:
            print(f"{Y}Peringatan: Gagal menjaga fokus browser: {e}{W}")
            # Lanjutkan meskipun gagal menjaga fokus
        
        # Setelah beralih ke popup
        # print(f"{Y}Menunggu form email muncul...{W}")
        
        # Cek koneksi sebelum mencari elemen
        if not cek_koneksi_browser(driver):
            print(f"{R}Koneksi ke browser terputus sebelum mencari form email{W}")
            # Coba reconnect
            new_driver = coba_reconnect_browser(driver, driver.current_url)
            if new_driver:
                driver = new_driver
                # Mulai ulang proses login
                return handle_google_login(driver, email, password)
            else:
                raise Exception("Tidak dapat menghubungkan kembali browser")
        
        # Setelah beralih ke popup
        # print(f"{Y}Menunggu form email muncul...{W}")
        email_input = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='email']"))
        )
        
        print(f"{G}Form email ditemukan, mengisi email...{W}")
        email_input.clear()
        email_input.send_keys(email)
        time.sleep(1)  # Tunggu sebentar setelah mengisi email
        
        print(f"{Y}Mengklik tombol Next setelah mengisi email...{W}")
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "identifierNext"))
        )
        next_button.click()
        
        # Tunggu password field muncul dengan waktu tunggu lebih lama
        # print(f"{Y}Menunggu form password muncul...{W}")
        
        # Tunggu lebih lama untuk halaman password dimuat sepenuhnya
        time.sleep(3)
        
        # Coba dengan selector yang lebih spesifik dan tunggu hingga elemen dapat diklik
        try:
            # Menggunakan aria-label="Enter your password" sesuai permintaan
            password_input = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[aria-label="Enter your password"]'))
            )
        except:
            # Coba dengan selector alternatif jika yang pertama gagal
            password_input = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='password']"))
            )
        
        # Scroll ke elemen password untuk memastikan terlihat
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", password_input)
        time.sleep(1)
        
        print(f"{G}Form password ditemukan, mengisi password...{W}")
        
        # Coba beberapa metode untuk mengisi password
        try:
            # Metode 1: Clear dan send_keys langsung
            password_input.clear()
            password_input.send_keys(password)
        except Exception as e1:
            print(f"{Y}Metode 1 gagal: {e1}, mencoba metode 2...{W}")
            try:
                # Metode 2: Gunakan JavaScript untuk mengisi nilai
                driver.execute_script("arguments[0].value = arguments[1];", password_input, password)
            except Exception as e2:
                print(f"{Y}Metode 2 gagal: {e2}, mencoba metode 3...{W}")
                try:
                    # Metode 3: Klik dulu, lalu isi
                    password_input.click()
                    time.sleep(1)
                    password_input.send_keys(password)
                except Exception as e3:
                    print(f"{R}Semua metode gagal mengisi password: {e3}{W}")
                    raise
        
        time.sleep(1)  # Tunggu sebentar setelah mengisi password
        
        print(f"{Y}Mengklik tombol Next setelah mengisi password...{W}")
        try:
            password_next = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "passwordNext"))
            )
            password_next.click()
        except Exception as e:
            print(f"{Y}Klik normal gagal: {e}, mencoba dengan JavaScript...{W}")
            # Coba dengan JavaScript click
            driver.execute_script("document.getElementById('passwordNext').click();")
        
        # Tunggu proses login selesai
        print(f"{Y}Menunggu proses login selesai...{W}")
        time.sleep(5)
        
        # Kembali ke window utama
        print(f"{Y}Kembali ke window utama...{W}")
        driver.switch_to.window(window_handles[0])
        
        print(f"{G}Login Google berhasil!{W}")
        
        # Lanjutkan dengan modul komentar.py
        try:
            print(f"\n{W}Melanjutkan proses ke modul komentar.py...{W}")
            import komentar
            komentar.lanjutkan_komentar(driver, driver.current_url)
        except ImportError:
            print(f"{R}Modul komentar.py tidak ditemukan. Pastikan file komentar.py ada di direktori yang sama.{W}")
        except Exception as e:
            print(f"{R}Terjadi kesalahan saat menjalankan modul komentar.py: {e}{W}")
        
    except TimeoutException as e:
        print(f"{R}Timeout saat menunggu elemen pada popup login Google: {e}{W}")
        
        # Coba kembali ke window utama
        try:
            if len(driver.window_handles) > 1:
                driver.switch_to.window(driver.window_handles[0])
        except:
            pass
        
        # Cek apakah login berhasil dengan mencari elemen user-auth-logout
        print(f"{Y}Memeriksa apakah login berhasil dengan mencari elemen user-auth-logout...{W}")
        
        # Tunggu sebentar untuk memastikan halaman dimuat sepenuhnya
        time.sleep(5)
        
        # Ambil HTML saat ini
        html_saat_ini = driver.page_source
        
        # Parse dengan BeautifulSoup
        soup = BeautifulSoup(html_saat_ini, 'html.parser')
        
        # Cari elemen dengan data-hook="user-auth-logout"
        elemen_logout = soup.find(attrs={"data-hook": "user-auth-logout"})
        
        if elemen_logout:
            print(f"{G}Elemen user-auth-logout ditemukan! Login berhasil meskipun popup tidak terdeteksi.{W}")
            print(f"{G}Login Google berhasil!{W}")
            
            # Lanjutkan dengan modul komentar.py
            try:
                print(f"\n{W}Melanjutkan proses ke modul komentar.py...{W}")
                import komentar
                komentar.lanjutkan_komentar(driver, driver.current_url)
            except ImportError:
                print(f"{R}Modul komentar.py tidak ditemukan. Pastikan file komentar.py ada di direktori yang sama.{W}")
            except Exception as e:
                print(f"{R}Terjadi kesalahan saat menjalankan modul komentar.py: {e}{W}")
        else:
            print(f"{R}Elemen user-auth-logout tidak ditemukan. Login mungkin gagal.{W}")
            
    except Exception as e:
        print(f"{R}Terjadi kesalahan saat proses login Google: {e}{W}")
        
        # Coba reconnect jika error disebabkan oleh koneksi terputus
        if "Connection" in str(e) or "HTTPConnectionPool" in str(e):
            print(f"{Y}Error koneksi terdeteksi, mencoba menghubungkan kembali...{W}")
            new_driver = coba_reconnect_browser(driver, driver.current_url)
            if new_driver:
                driver = new_driver
                # Coba login lagi dengan driver baru
                return handle_google_login(driver, email, password)
        
        # Coba kembali ke window utama
        try:
            if len(driver.window_handles) > 1:
                driver.switch_to.window(driver.window_handles[0])
        except:
            pass
        
        # Cek apakah login berhasil dengan mencari elemen user-auth-logout
        print(f"{Y}Memeriksa apakah login berhasil dengan mencari elemen user-auth-logout...{W}")
        
        # Tunggu sebentar untuk memastikan halaman dimuat sepenuhnya
        time.sleep(5)
        
        # Ambil HTML saat ini
        html_saat_ini = driver.page_source
        
        # Parse dengan BeautifulSoup
        soup = BeautifulSoup(html_saat_ini, 'html.parser')
        
        # Cari elemen dengan data-hook="user-auth-logout"
        elemen_logout = soup.find(attrs={"data-hook": "user-auth-logout"})
        
        if elemen_logout:
            print(f"{G}Elemen user-auth-logout ditemukan! Login berhasil meskipun terjadi error.{W}")
            print(f"{G}Login Google berhasil!{W}")
            
            # Lanjutkan dengan modul komentar.py
            try:
                print(f"\n{Y}Melanjutkan proses ke modul komentar.py...{W}")
                import komentar
                komentar.lanjutkan_komentar(driver, driver.current_url)
            except ImportError:
                print(f"{R}Modul komentar.py tidak ditemukan. Pastikan file komentar.py ada di direktori yang sama.{W}")
            except Exception as e:
                print(f"{R}Terjadi kesalahan saat menjalankan modul komentar.py: {e}{W}")
        else:
            print(f"{R}Elemen user-auth-logout tidak ditemukan. Login mungkin gagal.{W}")

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
            from main import inisialisasi_driver
            new_driver = inisialisasi_driver()
            
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
        driver.execute_script("return navigator.userAgent;", timeout)
        return True
    except Exception as e:
        if "Connection" in str(e) or "HTTPConnectionPool" in str(e):
            return False
        # Jika error bukan masalah koneksi, anggap koneksi masih aktif
        return True