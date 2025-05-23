from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
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
        # print(f"{Y}Memastikan browser tetap aktif di logout.py...{W}")
        
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

def lakukan_logout(driver, url):
    """
    Fungsi untuk melakukan logout dari akun
    
    Args:
        driver: WebDriver Selenium
        url: URL saat ini
    """
    print(f"{Y}=== {G}Melakukan proses logout di {W}{url} {Y}===")
    
    try:
        # Cek koneksi sebelum melanjutkan
        if not cek_koneksi_browser(driver):
            print(f"{R}Koneksi ke browser terputus sebelum memulai proses logout{W}")
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
                    return lakukan_logout(driver, url)
        
        # Langkah 1: Cari dan klik elemen dengan data-hook="user-auth-logout"
        # print(f"{Y}Mencari elemen logout dengan data-hook='user-auth-logout'...{W}")
        
        # Cek koneksi sebelum mengambil HTML
        if not cek_koneksi_browser(driver):
            print(f"{R}Koneksi ke browser terputus sebelum mengambil HTML{W}")
            # Coba reconnect
            new_driver = coba_reconnect_browser(driver, url)
            if new_driver:
                driver = new_driver
                # Coba lagi dengan driver baru
                return lakukan_logout(driver, url)
            else:
                print(f"{R}Tidak dapat melanjutkan proses karena koneksi terputus{W}")
                return
        
        # Ambil HTML saat ini
        try:
            html_saat_ini = driver.page_source
        except Exception as e:
            print(f"{R}Gagal mendapatkan HTML halaman: {e}{W}")
            # Cek apakah koneksi terputus
            if not cek_koneksi_browser(driver):
                new_driver = coba_reconnect_browser(driver, url)
                if new_driver:
                    driver = new_driver
                    # Coba lagi dengan driver baru
                    return lakukan_logout(driver, url)
            else:
                # Jika koneksi masih aktif tapi gagal mendapatkan HTML, coba refresh
                try:
                    driver.refresh()
                    time.sleep(5)
                    return lakukan_logout(driver, url)
                except:
                    pass
        
        # Parse dengan BeautifulSoup
        soup = BeautifulSoup(html_saat_ini, 'html.parser')
        
        # Cari elemen dengan data-hook="user-auth-logout"
        elemen_logout_bs4 = soup.find(attrs={"data-hook": "user-auth-logout"})
        
        if elemen_logout_bs4:
            # print(f"{G}Elemen logout ditemukan!{W}")
            
            # Gunakan Selenium untuk menemukan elemen dan klik
            try:
                # Cek koneksi sebelum mencari elemen dengan Selenium
                if not cek_koneksi_browser(driver):
                    print(f"{R}Koneksi ke browser terputus sebelum mencari elemen logout{W}")
                    # Coba reconnect
                    new_driver = coba_reconnect_browser(driver, url)
                    if new_driver:
                        driver = new_driver
                        # Coba lagi dengan driver baru
                        return lakukan_logout(driver, url)
                    else:
                        print(f"{R}Tidak dapat melanjutkan proses karena koneksi terputus{W}")
                        return
                
                # Tunggu elemen muncul dan dapat diklik
                logout_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-hook="user-auth-logout"]'))
                )
                
                # Scroll ke elemen tersebut
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", logout_button)
                # print(f"{Y}Scrolling ke tombol logout{W}")
                time.sleep(1)
                
                # Cek koneksi sebelum mengklik
                if not cek_koneksi_browser(driver):
                    print(f"{R}Koneksi ke browser terputus sebelum mengklik tombol logout{W}")
                    # Coba reconnect
                    new_driver = coba_reconnect_browser(driver, url)
                    if new_driver:
                        driver = new_driver
                        # Coba lagi dengan driver baru
                        return lakukan_logout(driver, url)
                    else:
                        print(f"{R}Tidak dapat melanjutkan proses karena koneksi terputus{W}")
                        return
                
                # Klik tombol logout
                # print(f"{Y}Mengklik tombol logout...{W}")
                logout_button.click()
                print(f"{G}Tombol logout berhasil diklik!{W}")
                
                # Tunggu sebentar agar perubahan terjadi
                time.sleep(5)  # Tunggu lebih lama (5 detik) untuk memastikan halaman diperbarui
                
            except Exception as e:
                print(f"{R}Gagal mengklik tombol logout: {e}{W}")
                
                # Cek apakah error disebabkan oleh koneksi terputus
                if "Connection" in str(e) or "HTTPConnectionPool" in str(e):
                    print(f"{Y}Error koneksi terdeteksi, mencoba menghubungkan kembali...{W}")
                    new_driver = coba_reconnect_browser(driver, url)
                    if new_driver:
                        driver = new_driver
                        # Coba lagi dengan driver baru
                        return lakukan_logout(driver, url)
                
                # Coba alternatif dengan JavaScript click
                try:
                    # Cek koneksi sebelum menggunakan JavaScript
                    if not cek_koneksi_browser(driver):
                        print(f"{R}Koneksi ke browser terputus sebelum menggunakan JavaScript{W}")
                        # Coba reconnect
                        new_driver = coba_reconnect_browser(driver, url)
                        if new_driver:
                            driver = new_driver
                            # Coba lagi dengan driver baru
                            return lakukan_logout(driver, url)
                        else:
                            print(f"{R}Tidak dapat melanjutkan proses karena koneksi terputus{W}")
                            return
                    
                    print(f"{Y}Mencoba klik logout dengan JavaScript...{W}")
                    driver.execute_script("document.querySelector('[data-hook=\"user-auth-logout\"]').click();")
                    print(f"{G}Tombol logout berhasil diklik dengan JavaScript!{W}")
                    
                    # Tunggu sebentar agar perubahan terjadi
                    time.sleep(5)  # Tunggu lebih lama (5 detik)
                    
                except Exception as e2:
                    print(f"{R}Gagal mengklik tombol logout dengan JavaScript: {e2}{W}")
                    
                    # Cek apakah error disebabkan oleh koneksi terputus
                    if "Connection" in str(e2) or "HTTPConnectionPool" in str(e2):
                        print(f"{Y}Error koneksi terdeteksi, mencoba menghubungkan kembali...{W}")
                        new_driver = coba_reconnect_browser(driver, url)
                        if new_driver:
                            driver = new_driver
                            # Coba lagi dengan driver baru
                            return lakukan_logout(driver, url)
        else:
            print(f"{R}Elemen logout dengan data-hook='user-auth-logout' tidak ditemukan.{W}")
        
        # Cek koneksi sebelum melanjutkan ke langkah 2
        if not cek_koneksi_browser(driver):
            print(f"{R}Koneksi ke browser terputus sebelum melanjutkan ke langkah 2{W}")
            # Coba reconnect
            new_driver = coba_reconnect_browser(driver, url)
            if new_driver:
                driver = new_driver
                # Coba lagi dengan driver baru
                return lakukan_logout(driver, url)
            else:
                print(f"{R}Tidak dapat melanjutkan proses karena koneksi terputus{W}")
                return
        
        # Langkah 2: Cari dan klik elemen dengan data-hook="actions-menu-item"
        # print(f"{Y}Mencari elemen menu dengan data-hook='actions-menu-item'...{W}")
        
        # Ambil HTML saat ini (setelah klik logout)
        try:
            html_saat_ini = driver.page_source
        except Exception as e:
            print(f"{R}Gagal mendapatkan HTML halaman: {e}{W}")
            # Cek apakah koneksi terputus
            if not cek_koneksi_browser(driver):
                new_driver = coba_reconnect_browser(driver, url)
                if new_driver:
                    driver = new_driver
                    # Coba lagi dengan driver baru
                    return lakukan_logout(driver, url)
            else:
                # Jika koneksi masih aktif tapi gagal mendapatkan HTML, coba refresh
                try:
                    driver.refresh()
                    time.sleep(5)
                    return lakukan_logout(driver, url)
                except:
                    pass
        
        # Parse dengan BeautifulSoup
        soup = BeautifulSoup(html_saat_ini, 'html.parser')
        
        # Cari elemen dengan data-hook="actions-menu-item"
        elemen_menu_bs4 = soup.find(attrs={"data-hook": "actions-menu-item"})
        
        if elemen_menu_bs4:
            # print(f"{G}Elemen menu ditemukan!{W}")
            
            # Gunakan Selenium untuk menemukan elemen dan klik
            try:
                # Cek koneksi sebelum mencari elemen dengan Selenium
                if not cek_koneksi_browser(driver):
                    print(f"{R}Koneksi ke browser terputus sebelum mencari elemen menu{W}")
                    # Coba reconnect
                    new_driver = coba_reconnect_browser(driver, url)
                    if new_driver:
                        driver = new_driver
                        # Coba lagi dengan driver baru
                        return lakukan_logout(driver, url)
                    else:
                        print(f"{R}Tidak dapat melanjutkan proses karena koneksi terputus{W}")
                        return
                
                # Tunggu elemen muncul dan dapat diklik
                menu_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-hook="actions-menu-item"]'))
                )
                
                # Scroll ke elemen tersebut
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", menu_button)
                # print(f"{Y}Scrolling ke tombol menu{W}")
                time.sleep(1)
                
                # Cek koneksi sebelum mengklik
                if not cek_koneksi_browser(driver):
                    print(f"{R}Koneksi ke browser terputus sebelum mengklik tombol menu{W}")
                    # Coba reconnect
                    new_driver = coba_reconnect_browser(driver, url)
                    if new_driver:
                        driver = new_driver
                        # Coba lagi dengan driver baru
                        return lakukan_logout(driver, url)
                    else:
                        print(f"{R}Tidak dapat melanjutkan proses karena koneksi terputus{W}")
                        return
                
                # Klik tombol menu
                print(f"{Y}Mengklik tombol menu...{W}")
                menu_button.click()
                # print(f"{G}Tombol menu berhasil diklik!{W}")
                
                # Tunggu proses selesai
                # print(f"{Y}Menunggu proses selesai...{W}")
                time.sleep(3)
                
                print(f"{G}Proses logout berhasil dilakukan!\n")
                
            except Exception as e:
                print(f"{R}Gagal mengklik tombol menu: {e}{W}")
                
                # Cek apakah error disebabkan oleh koneksi terputus
                if "Connection" in str(e) or "HTTPConnectionPool" in str(e):
                    print(f"{Y}Error koneksi terdeteksi, mencoba menghubungkan kembali...{W}")
                    new_driver = coba_reconnect_browser(driver, url)
                    if new_driver:
                        driver = new_driver
                        # Coba lagi dengan driver baru
                        return lakukan_logout(driver, url)
                
                # Coba alternatif dengan JavaScript click
                try:
                    # Cek koneksi sebelum menggunakan JavaScript
                    if not cek_koneksi_browser(driver):
                        print(f"{R}Koneksi ke browser terputus sebelum menggunakan JavaScript{W}")
                        # Coba reconnect
                        new_driver = coba_reconnect_browser(driver, url)
                        if new_driver:
                            driver = new_driver
                            # Coba lagi dengan driver baru
                            return lakukan_logout(driver, url)
                        else:
                            print(f"{R}Tidak dapat melanjutkan proses karena koneksi terputus{W}")
                            return
                    
                    print(f"{Y}Mencoba klik menu dengan JavaScript...{W}")
                    driver.execute_script("document.querySelector('[data-hook=\"actions-menu-item\"]').click();")
                    print(f"{G}Tombol menu berhasil diklik dengan JavaScript!{W}")
                    
                    # Tunggu proses selesai
                    print(f"{Y}Menunggu proses selesai...{W}")
                    time.sleep(3)
                    
                    print(f"{G}Proses logout berhasil dilakukan!{W}")
                    
                except Exception as e2:
                    print(f"{R}Gagal mengklik tombol menu dengan JavaScript: {e2}{W}")
                    
                    # Cek apakah error disebabkan oleh koneksi terputus
                    if "Connection" in str(e2) or "HTTPConnectionPool" in str(e2):
                        print(f"{Y}Error koneksi terdeteksi, mencoba menghubungkan kembali...{W}")
                        new_driver = coba_reconnect_browser(driver, url)
                        if new_driver:
                            driver = new_driver
                            # Coba lagi dengan driver baru
                            return lakukan_logout(driver, url)
        else:
            print(f"{R}Elemen menu dengan data-hook='actions-menu-item' tidak ditemukan.{W}")
            print(f"{Y}Proses logout tidak dapat diselesaikan. Melanjutkan ke URL berikutnya...{W}")
    
    except Exception as e:
        print(f"{R}Terjadi kesalahan saat proses logout: {e}{W}")
        
        # Cek apakah error disebabkan oleh koneksi terputus
        if "Connection" in str(e) or "HTTPConnectionPool" in str(e):
            print(f"{Y}Error koneksi terdeteksi, mencoba menghubungkan kembali...{W}")
            new_driver = coba_reconnect_browser(driver, url)
            if new_driver:
                driver = new_driver
                # Coba lagi dengan driver baru
                return lakukan_logout(driver, url)
        
        print(f"{Y}Proses logout tidak dapat diselesaikan. Melanjutkan ke URL berikutnya...{W}")

# Jika file ini dijalankan langsung
if __name__ == "__main__":
    print(f"{Y}File ini tidak dapat dijalankan secara langsung.{W}")
    print(f"{Y}File ini harus diimpor dan fungsi lakukan_logout() dipanggil dari komentar.py{W}")
