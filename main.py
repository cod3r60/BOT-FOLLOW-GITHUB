import os
import requests
import time
import random
import sys
from dotenv import load_dotenv
from colorama import init, Fore, Style

# --- Inisialisasi Colorama ---
init(autoreset=True)

# --- PERUBAHAN TAMPILAN: Kelas untuk mengelola gaya & warna ---
class Styles:
    HEADER = Fore.MAGENTA + Style.BRIGHT
    INFO = Fore.CYAN
    PROMPT = Fore.YELLOW + Style.BRIGHT
    SUCCESS = Fore.GREEN
    ERROR = Fore.RED
    WARNING = Fore.YELLOW
    RESET = Style.RESET_ALL

# --- Konfigurasi dan Inisialisasi ---
load_dotenv(dotenv_path=".env.local")

YOUR_USERNAME = os.getenv("GITHUB_USERNAME")
YOUR_TOKEN = os.getenv("GITHUB_TOKEN")

if not YOUR_USERNAME or not YOUR_TOKEN:
    print(f"{Styles.ERROR}❌ Error: Pastikan GITHUB_USERNAME dan GITHUB_TOKEN telah diatur di dalam file .env.local")
    sys.exit(1)

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"token {YOUR_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28"
}


# --- Fungsi-Fungsi Inti ---

def get_following_list(username):
    """Mengambil daftar lengkap 'following' dari seorang pengguna dengan visualisasi proses."""
    print(f"{Styles.INFO} Fase 1: Menganalisis akun '{username}'...")
    sys.stdout.write(f"{Styles.INFO} > Mengambil data following ")
    sys.stdout.flush()
    
    following_list = set()
    page = 1
    while True:
        try:
            url = f"https://api.github.com/users/{username}/following?per_page=100&page={page}"
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            data = response.json()
            if not data:
                break
            # PERUBAHAN TAMPILAN: Menampilkan titik sebagai progress
            sys.stdout.write(f"{Styles.INFO}.")
            sys.stdout.flush()
            for user in data:
                following_list.add(user['login'])
            page += 1
            time.sleep(0.1) # Jeda kecil antar request halaman
        except requests.exceptions.RequestException as e:
            print(f"\n{Styles.ERROR}  > Gagal mengambil data untuk {username}: {e}")
            return None
            
    print(f"\n{Styles.SUCCESS}✅ Selesai. Total {len(following_list)} akun yang di-follow oleh {username}.")
    return following_list

def follow_user(username_to_follow):
    """Menjalankan aksi PUT untuk follow seorang pengguna."""
    print(f"{Styles.INFO}   -> Mencoba follow '{username_to_follow}'...", end="")
    url = f"https://api.github.com/user/following/{username_to_follow}"
    try:
        response = requests.put(url, headers=HEADERS)
        if response.status_code == 204:
            print(f" {Styles.SUCCESS}✅ Sukses")
            return True
        else:
            print(f" {Styles.WARNING}⚠️ Gagal (Status: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f" {Styles.ERROR}❌ Error koneksi: {e}")
        return False

# --- Alur Utama Program ---

def run_bot():
    """Fungsi utama untuk menjalankan keseluruhan logika bot."""
    # PERUBAHAN TAMPILAN: Banner baru dengan copyright
    banner = f"""
{Styles.HEADER}====================================================
          G H O S T F O L L O W E R
        (GitHub Auto Follow Assistant)
====================================================
{Styles.RESET}
 {Styles.INFO}Dibuat oleh    : {Styles.PROMPT}nhazlipse{Styles.RESET}
 {Styles.INFO}GitHub         : {Styles.PROMPT}https://github.com/Nhazlipse{Styles.RESET}
 {Styles.INFO}Pengguna Aktif : {Styles.PROMPT}{YOUR_USERNAME}{Styles.RESET}
 
{Styles.WARNING} ⚠️  Gunakan dengan bijak dan tanggung jawab Anda sendiri.
"""
    print(banner)
    
    target_username = input(f"{Styles.PROMPT}❔ Masukkan username target (akun yang ingin ditiru): {Styles.RESET}").strip()
    if not target_username:
        print(f"{Styles.ERROR}Username target tidak boleh kosong. Program berhenti.")
        sys.exit(1)
        
    target_following = get_following_list(target_username)
    my_following = get_following_list(YOUR_USERNAME)
    
    if target_following is None or my_following is None:
        print(f"\n{Styles.ERROR}Tidak bisa melanjutkan karena gagal mengambil data awal.")
        sys.exit(1)
        
    users_to_follow = sorted(list(target_following - my_following))
    
    if not users_to_follow:
        print(f"\n{Styles.SUCCESS}🎉 Hebat! Anda sudah mengikuti semua akun yang juga diikuti oleh target.")
        sys.exit(1)
        
    print(f"\n{Styles.INFO} Fase 2: Analisis Selesai.")
    print(f"{Styles.SUCCESS}💡 Ditemukan {len(users_to_follow)} akun baru yang bisa Anda follow.")
    
    try:
        max_follow_str = input(f"{Styles.PROMPT}❔ Berapa jumlah maksimal akun yang ingin di-follow? (0 untuk batal): {Styles.RESET}")
        max_follow = int(max_follow_str)
        if max_follow <= 0:
            print(f"{Styles.INFO}Proses dibatalkan oleh pengguna.")
            sys.exit(1)
        users_to_follow = users_to_follow[:max_follow]
    except (ValueError, TypeError):
        print(f"{Styles.ERROR}Input tidak valid. Harap masukkan angka. Proses dibatalkan.")
        sys.exit(1)
        
    confirmation = input(f"{Styles.WARNING}❓ Anda akan mencoba follow {len(users_to_follow)} akun. Lanjutkan? (y/n): {Styles.RESET}").lower().strip()
    if confirmation != 'y':
        print(f"{Styles.INFO}Proses dibatalkan oleh pengguna.")
        sys.exit(1)
    
    print(f"\n{Styles.HEADER}--- Fase 3: Memulai Proses Follow ---")
    followed_count = 0
    for i, user in enumerate(users_to_follow):
        print(f"\n{Styles.INFO}[ {i+1} / {len(users_to_follow)} ]")
        if follow_user(user):
            followed_count += 1
        
        delay = random.randint(10, 25)
        # PERUBAHAN TAMPILAN: Timer countdown
        for remaining in range(delay, 0, -1):
            sys.stdout.write(f"\r   {Styles.INFO}Jeda keamanan: {remaining:02d} detik... ")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write(f"\r   {Styles.SUCCESS}Jeda keamanan: OK!          \n")

    print(f"\n{Styles.HEADER}===================================")
    print(f"    ✨ Proses Selesai! ✨")
    print(f"{Styles.SUCCESS}  Berhasil follow {followed_count} dari {len(users_to_follow)} target akun.")
    print(f"{Styles.HEADER}===================================")


if __name__ == "__main__":
    try:
        run_bot()
    except KeyboardInterrupt:
        print(f"\n\n{Styles.WARNING}Program dihentikan oleh pengguna (Ctrl+C). Selamat tinggal!")
        sys.exit(0)