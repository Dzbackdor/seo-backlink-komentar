import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
import os
import logging
import sys
from colorama import Fore, init
import atexit
# Initialize Colorama
init(autoreset=True)

# Colors for terminal text
B = Fore.BLUE
W = Fore.WHITE
R = Fore.RED
G = Fore.GREEN
Y = Fore.YELLOW



banner = f"""

{R}╔═════════════════════════════════╗
{R}║{Y}   _           _   _ _     _     {R}║    
{R}║{Y}  | |_ ___ ___| |_| |_|___| |_   {R}║    
{R}║{Y}  | . | .'|  _| '_| | |   | '_|  {R}║ 
{R}║{Y}  |___|__,|___|_,_|_|_|_|_|_,_|  {R}║ 
{R}║     🐍 {W}PYTHON SEO TOOLS 🐍      {R}║                 
{R}╚═════════════════════════════════╝
"""

def pastikan_browser_tetap_aktif(driver):
    """
    Fungsi untuk memastikan browser tetap aktif meskipun tidak di foreground
    """
    try:
        # print(f"{Y}Memastikan browser tetap fokus...{W}")
        
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
        print(f"{W}Browser akan tetap aktif meskipun tidak di foreground: {result}{W}")
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
        result = driver.execute_script("""
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

def inisialisasi_driver():
    options = uc.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    # Tambahkan flag untuk mencegah throttling
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument('--disable-renderer-backgrounding')
    
    # Flag lain yang sudah ada
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-infobars')
    options.add_argument('--lang=en-US')
    
    # Tambahkan opsi ini untuk meningkatkan stabilitas
    options.add_argument('--disable-features=NetworkService')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--disable-web-security')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    
    # Tambahkan penanganan error yang tepat
    try:
        print(f"{Y}Menginisialisasi Chrome driver...{W}")
        driver = uc.Chrome(options=options)
        
        # Dapatkan resolusi layar
        screen_width = driver.execute_script("return window.screen.width")
        screen_height = driver.execute_script("return window.screen.height")
        
        # Atur ukuran jendela browser menjadi setengah layar
        window_width = int(screen_width * 0.8)  # 50% dari lebar layar
        window_height = screen_height
        
        # Atur posisi jendela (opsional, untuk menempatkan jendela di tengah)
        position_x = 0
        position_y = int((screen_height - window_height) / 2)
        
        # Atur ukuran dan posisi jendela
        driver.set_window_size(window_width, window_height)
        driver.set_window_position(position_x, position_y)
        
        # Uji driver dengan perintah sederhana
        driver.execute_script("return navigator.userAgent")
        print(f"{G}Chrome driver berhasil diinisialisasi.{W}")
        return driver
    except Exception as e:
        print(f"{R}Error inisialisasi Chrome driver: {e}{W}")
        print(f"{Y}Mencoba lagi dengan konfigurasi berbeda...{W}")
        
        # Coba dengan konfigurasi berbeda
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        
        # Tambahkan flag anti-throttling di sini juga
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        
        try:
            print(f"{Y}Mencoba inisialisasi dengan konfigurasi alternatif...{W}")
            driver = uc.Chrome(options=options)
            
            # Atur ukuran jendela browser menjadi setengah layar
            screen_width = driver.execute_script("return window.screen.width")
            screen_height = driver.execute_script("return window.screen.height")
            window_width = int(screen_width * 0.8)
            window_height = int(screen_height * 10)
            position_x = int((screen_width - window_width) / 2)
            position_y = int((screen_height - window_height) / 2)
            driver.set_window_size(window_width, window_height)
            driver.set_window_position(position_x, position_y)
            
            print(f"{G}Chrome driver berhasil diinisialisasi dengan konfigurasi alternatif.{W}")
            return driver
        except Exception as e2:
            print(f"{R}Percobaan kedua gagal: {e2}{W}")
            raise Exception(f"Tidak dapat menginisialisasi Chrome driver setelah beberapa percobaan: {e2}")

# Fungsi untuk membaca URL dari file list.txt
def baca_url_dari_file(nama_file="list.txt"):
    try:
        with open(nama_file, 'r') as file:
            urls = [line.strip() for line in file if line.strip()]
        return urls
    except FileNotFoundError:
        print(f"{R}File {nama_file} tidak ditemukan.{W}")
        return []
    except Exception as e:
        print(f"{R}Terjadi kesalahan saat membaca file: {e}{W}")
        return []

# Fungsi untuk menampilkan loading bar
def tampilkan_loading_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='\r')
    if iteration == total:
        print()

# Fungsi untuk menangani pop-up
def tangani_popup(driver, max_attempts=5):
    # print(f"{Y}Menangani pop-up awal...{W}")
    
    # Pastikan browser tetap aktif
    pastikan_browser_tetap_aktif(driver)
    
    # Daftar selector umum untuk tombol tutup pop-up
    popup_selectors = [
        # Tombol close dengan class yang mengandung 'close'
        "button.close", ".close", "[class*='close']", 
        # Tombol close dengan class yang mengandung 'dismiss'
        ".dismiss", "[class*='dismiss']",
        # Tombol close dengan icon X
        ".fa-times", ".icon-close", "[aria-label='Close']", "[title='Close']",
        # Tombol dengan teks 'No thanks', 'Tidak', 'Tutup', dll
        "button:contains('No thanks')", "button:contains('Tidak')", "button:contains('Tutup')",
        "button:contains('Close')", "button:contains('Cancel')", "button:contains('Batal')",
        # Tombol dengan ID yang mengandung 'close'
        "[id*='close']", "[id*='dismiss']",
        # Overlay pop-up
        ".modal-backdrop", ".overlay", ".popup-overlay"
    ]
    
    popup_found = False
    attempts = 0
    
    # Inisialisasi loading bar
    total_attempts = max_attempts
    
    while attempts < max_attempts:
        # Jaga fokus browser sebelum operasi penting
        jaga_fokus_browser(driver)
        
        current_popup_found = False
        
        # Update loading bar
        tampilkan_loading_bar(attempts, total_attempts, prefix=f'{Y}Memeriksa pop-up:{W}', suffix='Selesai', length=50)
        
        # Coba setiap selector
        for selector in popup_selectors:
            try:
                # Coba temukan elemen dengan selector ini
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed():
                        try:
                            # Jaga fokus browser sebelum klik
                            jaga_fokus_browser(driver)
                            
                            element.click()
                            current_popup_found = True
                            popup_found = True
                            time.sleep(0.5)  # Tunggu sebentar setelah menutup pop-up
                        except:
                            pass
            except:
                continue
        
        # Jika tidak ada popup yang ditemukan pada iterasi ini, coba tekan Escape
        if not current_popup_found:
            try:
                # Jaga fokus browser sebelum mengirim keys
                jaga_fokus_browser(driver)
                
                actions = ActionChains(driver)
                actions.send_keys(Keys.ESCAPE).perform()
                time.sleep(0.5)
            except:
                pass
        
        # Jika tidak ada popup yang ditemukan pada iterasi ini, keluar dari loop
        if not current_popup_found:
            attempts += 1
        else:
            attempts = 0  # Reset attempts jika popup ditemukan
    
    # Tampilkan loading bar 100%
    tampilkan_loading_bar(total_attempts, total_attempts, prefix=f'{Y}Memeriksa pop-up:{W}', suffix='Selesai', length=50)
    
    print(f"{G}Pop-up awal telah ditangani, melanjutkan ke pencarian elemen...")


# Fungsi untuk klik elemen dengan ID
def klik_elemen_dengan_id(driver, elemen_id):
    try:
        # Jaga fokus browser sebelum operasi penting
        jaga_fokus_browser(driver)
        
        # print(f"{Y}Mengklik elemen root-comment-box-start...{W}")
        elemen = driver.find_element(By.ID, elemen_id)
        elemen.click()
        # print(f"{G}Elemen root-comment-box-start berhasil diklik.{W}")
        time.sleep(2)  # Tunggu sebentar setelah klik
        return True
    except Exception as e:
        print(f"{R}Gagal mengklik elemen root-comment-box-start: {e}{W}")
        # Coba alternatif dengan JavaScript click
        try:
            # Jaga fokus browser sebelum JavaScript click
            jaga_fokus_browser(driver)
            
            print(f"{Y}Mencoba klik dengan JavaScript...{W}")
            driver.execute_script("arguments[0].click();", driver.find_element(By.ID, elemen_id))
            print(f"{G}Elemen root-comment-box-start berhasil diklik dengan JavaScript.{W}")
            time.sleep(2)
            return True
        except Exception as e2:
            print(f"{R}Gagal mengklik elemen root-comment-box-start dengan JavaScript: {e2}{W}")
            return False

# Fungsi untuk klik elemen login
def klik_elemen_login(driver):
    try:
        # Jaga fokus browser sebelum operasi penting
        jaga_fokus_browser(driver)
        
        # print(f"{Y}Menunggu elemen login-as-member-text-button muncul...{W}")
        
        # Tunggu elemen login muncul tanpa loading bar
        elemen_login = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-hook="login-as-member-text-button"]'))
        )
        # print(f"{G}Elemen login-as-member-text-button ditemukan{W}")
        
        # Jaga fokus browser sebelum klik
        jaga_fokus_browser(driver)
        
        # Klik elemen login
        try:
            # print(f"{Y}Mengklik elemen login-as-member-text-button...{W}")
            elemen_login.click()
            # print(f"{G}Elemen login-as-member-text-button berhasil diklik.{W}")
            time.sleep(2)  # Tunggu sebentar setelah klik
            return True
        except Exception as e:
            print(f"{R}Gagal mengklik elemen login-as-member-text-button: {e}{W}")
            # Coba alternatif dengan JavaScript click
            try:
                # Jaga fokus browser sebelum JavaScript click
                jaga_fokus_browser(driver)
                
                print(f"{Y}Mencoba klik dengan JavaScript...{W}")
                driver.execute_script("arguments[0].click();", elemen_login)
                print(f"{G}Elemen login-as-member-text-button berhasil diklik dengan JavaScript.{W}")
                time.sleep(2)
                return True
            except Exception as e2:
                print(f"{R}Gagal mengklik elemen login-as-member-text-button dengan JavaScript: {e2}{W}")
                return False
            
    except TimeoutException:
        print(f"{R}Elemen dengan data-hook='login-as-member-text-button' tidak muncul dalam waktu yang ditentukan. Proses dihentikan.{W}")
        return False
    except Exception as e:
        print(f"{R}Terjadi kesalahan saat mencari elemen login: {e}{W}")
        return False

# Fungsi untuk klik elemen signup
def klik_elemen_signup(driver):
    try:
        # Jaga fokus browser sebelum operasi penting
        jaga_fokus_browser(driver)
        
        # print(f"{Y}Menunggu elemen switchToSignUp muncul...{W}")
        
        # Tunggu elemen signup muncul tanpa loading bar
        elemen_signup = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="switchToSignUp"]'))
        )
        # print(f"{G}Elemen switchToSignUp ditemukan{W}")
        
        # Jaga fokus browser sebelum klik
        jaga_fokus_browser(driver)
        
        # Klik elemen signup
        try:
            # print(f"{Y}Mengklik elemen switchToSignUp...{W}")
            elemen_signup.click()
            # print(f"{G}Elemen switchToSignUp berhasil diklik.{W}")
            time.sleep(2)  # Tunggu sebentar setelah klik
            return True
        except Exception as e:
            print(f"{R}Gagal mengklik elemen switchToSignUp: {e}{W}")
            # Coba alternatif dengan JavaScript click
            try:
                # Jaga fokus browser sebelum JavaScript click
                jaga_fokus_browser(driver)
                
                print(f"{Y}Mencoba klik dengan JavaScript...{W}")
                driver.execute_script("arguments[0].click();", elemen_signup)
                print(f"{G}Elemen switchToSignUp berhasil diklik dengan JavaScript.{W}")
                time.sleep(2)
                return True
            except Exception as e2:
                print(f"{R}Gagal mengklik elemen switchToSignUp dengan JavaScript: {e2}{W}")
                return False
            
    except TimeoutException:
        print(f"{R}Elemen dengan data-testid='switchToSignUp' tidak muncul dalam waktu yang ditentukan. Proses dihentikan.{W}")
        return False
    except Exception as e:
        print(f"{R}Terjadi kesalahan saat mencari elemen signup: {e}{W}")
        return False

def cari_elemen_dengan_bs4_dan_scroll(driver, timeout=300, wait_time=0.5):
    """
    Fungsi untuk mencari elemen dengan ID yang mengandung 'root-comment-box-start' sambil scroll.
    Scroll terus dilakukan sampai benar-benar tidak bisa scroll lagi, baru kemudian menunggu 5 menit.
    
    Args:
        driver: WebDriver Selenium
        timeout: Batas waktu maksimum dalam detik (default: 300 detik)
        wait_time: Waktu tunggu setelah setiap scroll dalam detik (default: 0.5 detik)
    
    Returns:
        ID elemen jika ditemukan, None jika tidak ditemukan
    """
    # print(f"{Y}Mulai mencari elemen root-comment-box-start sambil scroll...{W}")
    # print(f"{Y}Timeout: {timeout} detik, waktu tunggu per scroll: {wait_time} detik{W}")
    
    # Pastikan browser tetap aktif
    pastikan_browser_tetap_aktif(driver)
    
    # Waktu mulai
    start_time = time.time()
    
    # Waktu terakhir menjaga fokus
    last_focus_time = time.time()
    
    # Jumlah percobaan scroll penuh
    scroll_attempts = 0
    max_scroll_attempts = 3  # Maksimal 3 kali scroll penuh
    
    while scroll_attempts < max_scroll_attempts:
        # Reset posisi scroll untuk percobaan baru
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        print(f"{Y}Percobaan scroll ke-{scroll_attempts + 1}...{W}")
        
        # Posisi scroll awal
        posisi_scroll = 0
        # Jumlah scroll per langkah (pixel)
        langkah_scroll = 600
        
        # Variabel untuk mendeteksi jika sudah tidak bisa scroll lagi
        posisi_scroll_terakhir = -1
        
        # Scroll sampai benar-benar tidak bisa scroll lagi
        while True:
            # Periksa apakah perlu menjaga fokus (setiap 5 detik)
            current_time = time.time()
            if current_time - last_focus_time > 5:
                jaga_fokus_browser(driver)
                last_focus_time = current_time
            
            # Periksa apakah timeout tercapai
            if time.time() - start_time > timeout:
                print(f"{R}Timeout tercapai ({timeout} detik). Menghentikan pencarian.{W}")
                return None
            
            # Dapatkan tinggi halaman saat ini
            tinggi_halaman = driver.execute_script("return document.body.scrollHeight")
            
            # Perkiraan total langkah scroll
            total_langkah = (tinggi_halaman // langkah_scroll) + 1
            
            # Update loading bar
            tampilkan_loading_bar(min(posisi_scroll // langkah_scroll, total_langkah), total_langkah, 
                                 prefix=f'{Y}Mencari elemen:{W}', suffix=f'Scrolling (Percobaan {scroll_attempts + 1})', length=50)
            
            # Scroll ke posisi baru
            driver.execute_script(f"window.scrollTo(0, {posisi_scroll});")
            
            # Tunggu sedikit agar konten dimuat
            time.sleep(wait_time)
            
            # Dapatkan posisi scroll aktual setelah scroll
            posisi_scroll_aktual = driver.execute_script("return window.pageYOffset || document.documentElement.scrollTop;")
            
            # Ambil HTML saat ini
            html_saat_ini = driver.page_source
            
            # Parse dengan BeautifulSoup
            soup = BeautifulSoup(html_saat_ini, 'html.parser')
            
            # Cari elemen yang mengandung "root-comment-box-start" dalam ID
            elemen_bs4 = soup.find(lambda tag: tag.has_attr('id') and 'root-comment-box-start' in tag['id'])
            
            if elemen_bs4:
                # Jika elemen ditemukan dengan BeautifulSoup, dapatkan ID lengkapnya
                elemen_id = elemen_bs4['id']
                
                # Tampilkan loading bar 100%
                tampilkan_loading_bar(total_langkah, total_langkah, 
                prefix=f'{Y}Mencari elemen:{W}', suffix=f'{G}Ditemukan!{W}', length=50)
                # print(f"\n{G}BeautifulSoup menemukan elemen dengan ID: {elemen_id}{W}")
                
                # Jaga fokus browser sebelum operasi penting
                jaga_fokus_browser(driver)
                
                # Gunakan Selenium untuk menemukan elemen dengan ID yang sama
                try:
                    elemen_selenium = driver.find_element(By.ID, elemen_id)
                    
                    # Scroll ke elemen tersebut
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemen_selenium)
                    # print(f"{Y}Scrolling ke elemen target{W}")
                    time.sleep(1)
                    
                    return elemen_id  # Mengembalikan ID elemen
                except Exception as e:
                    print(f"{R}Elemen ditemukan dengan BeautifulSoup tetapi tidak dengan Selenium: {e}{W}")
                    # Lanjutkan pencarian
            
            # Cek apakah sudah tidak bisa scroll lagi (posisi scroll tidak berubah)
            if posisi_scroll_aktual == posisi_scroll_terakhir:
                print(f"\n{Y}Tidak bisa scroll lagi. Sudah mencapai batas bawah halaman.{W}")
                break
            
            # Simpan posisi scroll saat ini untuk perbandingan berikutnya
            posisi_scroll_terakhir = posisi_scroll_aktual
            
            # Tambah posisi scroll untuk langkah berikutnya
            posisi_scroll += langkah_scroll
            
            # Perbarui tinggi halaman (mungkin berubah karena lazy loading)
            tinggi_halaman_baru = driver.execute_script("return document.body.scrollHeight")
            if tinggi_halaman_baru > tinggi_halaman:
                tinggi_halaman = tinggi_halaman_baru
        
        # Jika sampai di sini, berarti sudah benar-benar tidak bisa scroll lagi
        print(f"\n{Y}Scroll sudah mencapai batas. Menunggu 5 menit...{W}")
        
        # Menunggu 5 menit (300 detik)
        waktu_tunggu_batas = 300  # 5 menit dalam detik
        waktu_mulai_tunggu = time.time()
        
        # Tampilkan loading bar untuk waktu tunggu
        while time.time() - waktu_mulai_tunggu < waktu_tunggu_batas:
            waktu_berlalu = time.time() - waktu_mulai_tunggu
            tampilkan_loading_bar(min(int(waktu_berlalu), waktu_tunggu_batas), waktu_tunggu_batas, 
                                 prefix=f'{Y}Menunggu:{W}', suffix=f'Sisa {int(waktu_tunggu_batas - waktu_berlalu)} detik', length=50)
            
            # Cek elemen setiap 10 detik selama menunggu
            if int(waktu_berlalu) % 10 == 0:
                # Jaga fokus browser
                jaga_fokus_browser(driver)
                
                # Ambil HTML saat ini
                html_saat_ini = driver.page_source
                
                # Parse dengan BeautifulSoup
                soup = BeautifulSoup(html_saat_ini, 'html.parser')
                
                # Cari elemen yang mengandung "root-comment-box-start" dalam ID
                elemen_bs4 = soup.find(lambda tag: tag.has_attr('id') and 'root-comment-box-start' in tag['id'])
                
                if elemen_bs4:
                    # Jika elemen ditemukan dengan BeautifulSoup, dapatkan ID lengkapnya
                    elemen_id = elemen_bs4['id']
                    
                    # Tampilkan loading bar 100%
                    tampilkan_loading_bar(waktu_tunggu_batas, waktu_tunggu_batas, 
                                         prefix=f'{Y}Menunggu:{W}', suffix=f'{G}Elemen ditemukan!{W}', length=50)
                    print(f"\n{G}BeautifulSoup menemukan elemen dengan ID: {elemen_id}{W}")
                    
                    # Gunakan Selenium untuk menemukan elemen dengan ID yang sama
                    try:
                        elemen_selenium = driver.find_element(By.ID, elemen_id)
                        
                        # Scroll ke elemen tersebut
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemen_selenium)
                        # print(f"{Y}Scrolling ke elemen target{W}")
                        time.sleep(1)
                        
                        return elemen_id  # Mengembalikan ID elemen
                    except Exception as e:
                        print(f"{R}Elemen ditemukan dengan BeautifulSoup tetapi tidak dengan Selenium: {e}{W}")
            
            time.sleep(1)  # Tunggu 1 detik antara update loading bar
        
        print(f"\n{Y}Selesai menunggu 5 menit.{W}")
        
        # Jika elemen tidak ditemukan setelah menunggu 5 menit
        print(f"{Y}Elemen tidak ditemukan pada percobaan ke-{scroll_attempts + 1}. Menunggu sebentar...{W}")
        
        # Tunggu lebih lama sebelum mencoba lagi
        time.sleep(5)
        
        # Jaga fokus browser sebelum refresh
        jaga_fokus_browser(driver)
        
        # Refresh halaman jika ini bukan percobaan terakhir
        if scroll_attempts < max_scroll_attempts - 1:
            print(f"{Y}Me-refresh halaman untuk percobaan berikutnya...{W}")
            driver.refresh()
            time.sleep(5)  # Tunggu halaman dimuat setelah refresh
            
            # Pastikan browser tetap aktif setelah refresh
            pastikan_browser_tetap_aktif(driver)
        
        # Increment percobaan
        scroll_attempts += 1
    
    # Tampilkan loading bar 100%
    tampilkan_loading_bar(100, 100, 
                         prefix=f'{Y}Mencari elemen:{W}', suffix=f'{R}Tidak ditemukan{W}', length=50)
    
    # Jika sampai di sini, elemen tidak ditemukan setelah beberapa percobaan
    print(f"\n{R}Elemen root-comment-box-start tidak ditemukan setelah {max_scroll_attempts} percobaan scroll{W}")
    return None

def buka_url_dari_list():
    # Inisialisasi driver Chrome dengan ukuran setengah layar
    driver = inisialisasi_driver()
    
    # Daftarkan fungsi untuk menutup driver saat program berakhir
    def close_driver():
        try:
            driver.quit()
        except:
            pass
    
    atexit.register(close_driver)
    
    # Terapkan script anti-throttling
    pastikan_browser_tetap_aktif(driver)
    
    # Baca URL dari file list.txt
    urls = baca_url_dari_file("list.txt")
    
    if not urls:
        print(f"{R}Tidak ada URL yang ditemukan di file list.txt{W}")
        driver.quit()
        return
    
    # Buka setiap URL dari list
    for i, url in enumerate(urls, 1):
        try:
            print(f"{Y}[{W}{i}/{len(urls)}{Y}] {W}Membuka URL: {Y}{url}")
            driver.get(url)
            
            # Tunggu beberapa detik agar halaman dimuat dengan sempurna
            time.sleep(3)
            
            # Pastikan browser tetap aktif setelah membuka URL baru
            pastikan_browser_tetap_aktif(driver)
            
            # Tangani popup setelah halaman dimuat
            tangani_popup(driver)
            
            # Cari elemen root-comment-box-start
            # print(f"{Y}Mencari elemen root-comment-box-start...{W}")
            elemen_id = cari_elemen_dengan_bs4_dan_scroll(driver)
            
            # Jika elemen ditemukan, klik elemen tersebut
            if elemen_id:
                print(f"{G}Elemen root-comment-box-start ditemukan dengan ID: {elemen_id}{W}")
                
                # Langkah 1: Klik elemen root-comment-box-start
                if klik_elemen_dengan_id(driver, elemen_id):
                    print(f"{G}Berhasil mengklik elemen root-comment-box-start")
                    
                    # Langkah 2: Klik elemen login
                    print(f"{Y}Langkah 2: Mencari dan mengklik elemen login")
                    if klik_elemen_login(driver):
                        print(f"{G}Berhasil mengklik elemen login")
                        
                        # Langkah 3: Klik elemen signup
                        print(f"{Y}Langkah 3: Mencari dan mengklik elemen signup")
                        if klik_elemen_signup(driver):
                            print(f"{G}Berhasil mengklik elemen signup")
                            # print(f"{G}Semua langkah berhasil dilakukan!")
                            
                            # Panggil modul daftar.py untuk melanjutkan proses
                            try:
                                print(f"\n{W}Melanjutkan proses ke modul daftar.py...")
                                import daftar
                                daftar.lanjutkan_proses(driver, url)
                            except ImportError:
                                print(f"{R}Modul daftar.py tidak ditemukan. Pastikan file daftar.py ada di direktori yang sama.{W}")
                            except Exception as e:
                                print(f"{R}Terjadi kesalahan saat menjalankan modul daftar.py: {e}{W}")
                        else:
                            print(f"{R}Gagal mengklik elemen signup{W}")
                    else:
                        print(f"{R}Gagal mengklik elemen login{W}")
                else:
                    print(f"{R}Gagal mengklik elemen root-comment-box-start{W}")
            else:
                print(f"{R}Elemen root-comment-box-start tidak ditemukan{W}")
            
            # print(f"{G}Berhasil membuka URL: {url}{W}")
            
            # Tunggu sebentar sebelum melanjutkan ke URL berikutnya
            time.sleep(3)
            
        except Exception as e:
            print(f"{R}Gagal membuka URL {url}: {e}{W}")
    
    # Setelah semua URL diproses, tutup browser dan keluar
    print(f"{G}Semua URL telah diproses. Menutup browser...{W}")
    try:
        driver.quit()
        print(f"{G}Browser berhasil ditutup. Program selesai.{W}")
    except Exception as e:
        print(f"{Y}Info: Browser sudah ditutup atau terjadi error saat menutup: {e}{W}")
    
    # Keluar dari program
    print(f"{G}Program selesai dijalankan.{W}")
    sys.exit(0)

# Jalankan fungsi jika file ini dijalankan langsung
if __name__ == "__main__":
    # sys('cls')
    print(banner)
    # exit()
    buka_url_dari_list()
