import os
import requests
import time
import random
import sys
from dotenv import load_dotenv
from colorama import init, Fore, Style

# --- Initialize Colorama & Style Display ---
init(autoreset=True)

class Styles:
    HEADER = Fore.MAGENTA + Style.BRIGHT
    INFO = Fore.CYAN
    PROMPT = Fore.YELLOW + Style.BRIGHT
    SUCCESS = Fore.GREEN
    ERROR = Fore.RED
    WARNING = Fore.YELLOW
    RESET = Style.RESET_ALL

# --- Configuration and Initialization ---
load_dotenv(dotenv_path=".env.local")
YOUR_USERNAME = os.getenv("GITHUB_USERNAME")
YOUR_TOKEN = os.getenv("GITHUB_TOKEN")

if not YOUR_USERNAME or not YOUR_TOKEN:
    print(f"{Styles.ERROR}❌ Error: Make sure GITHUB_USERNAME and GITHUB_TOKEN are in the .env file")
    sys.exit(1)

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"token {YOUR_TOKEN}"
}

# --- Core Functions ---

def baca_target_users(nama_file="user_target.txt"):
    """Read the list of usernames from the target file."""
    if not os.path.exists(nama_file):
        print(f"{Styles.ERROR}❌ File '{nama_file}' not found! Please create the file first.")
        return None
    
    with open(nama_file, 'r') as f:
        targets = [line.strip() for line in f if line.strip()]
    
    print(f"{Styles.SUCCESS}✅ Successfully read {len(targets)} targets from '{nama_file}'.")
    return targets

def get_list_from_api(username, list_type="followers"):
    """Retrieve the list of followers or following from a user."""
    print(f"{Styles.INFO}   > Retrieving '{list_type}' list from '{username}'...", end="")
    data_list = set()
    page = 1
    while True:
        try:
            url = f"https://api.github.com/users/{username}/{list_type}?per_page=100&page={page}"
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            data = response.json()
            if not data:
                break
            sys.stdout.write(f"{Styles.INFO}.")
            sys.stdout.flush()
            for item in data:
                data_list.add(item['login'])
            page += 1
            time.sleep(0.2)
        except requests.exceptions.RequestException as e:
            print(f"\n{Styles.ERROR}   > Failed to retrieve data for {username}: {e}")
            return None
    
    print(f" {Styles.SUCCESS}(found {len(data_list)})")
    return data_list

def follow_user(username_to_follow):
    """Perform the follow action to a user, handling rate limits."""
    print(f"-> Trying to follow '{username_to_follow}'...", end="")
    url = f"https://api.github.com/user/following/{username_to_follow}"
    try:
        response = requests.put(url, headers=HEADERS)
        # Handle rate limit
        if response.status_code == 403 and "X-RateLimit-Remaining" in response.headers:
            remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
            reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
            if remaining == 0:
                wait_seconds = max(reset_time - int(time.time()), 0)
                print(f"\n{Styles.WARNING}⚠️ Rate limit reached. Waiting {wait_seconds} seconds until reset...")
                time.sleep(wait_seconds + 5)
                # Retry once after waiting
                response = requests.put(url, headers=HEADERS)
        if response.status_code == 204:
            print(f" {Styles.SUCCESS}✅ Success")
            return True
        else:
            print(f" {Styles.WARNING}⚠️ Failed (Status: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f" {Styles.ERROR}❌ Connection error: {e}")
        return False

{Styles.RESET}
 {Styles.INFO}Dibuat oleh    : {Styles.PROMPT}nhazlipse{Styles.RESET}
 {Styles.INFO}GitHub         : {Styles.PROMPT}https://github.com/Nhazlipse{Styles.RESET}
 {Styles.INFO}Pengguna Aktif : {Styles.PROMPT}{YOUR_USERNAME}{Styles.RESET}
"""
    print(banner)

    target_users = baca_target_users()
    if target_users is None:
        sys.exit(1)

    print(f"\n{Styles.HEADER}--- Fase 1: Mengumpulkan Target Followers ---")
    all_target_followers = set()
    for user in target_users:
        followers = get_list_from_api(user, "followers")
        if followers:
            all_target_followers.update(followers)
    
    if not all_target_followers:
        print(f"\n{Styles.ERROR}Tidak ada followers yang berhasil dikumpulkan dari semua target. Program berhenti.")
        sys.exit(1)
        
    print(f"\n{Styles.SUCCESS}Total {len(all_target_followers)} followers unik berhasil dikumpulkan.")

    print(f"\n{Styles.HEADER}--- Fase 2: Analisis & Filter ---")
    my_following = get_list_from_api(YOUR_USERNAME, "following")
    if my_following is None:
        print(f"\n{Styles.ERROR}Gagal mengambil daftar following Anda sendiri. Program berhenti.")
        sys.exit(1)
    
    users_to_follow = sorted(list(all_target_followers - my_following))

    if not users_to_follow:
        print(f"\n{Styles.SUCCESS}🎉 Hebat! Anda sudah mengikuti semua followers dari daftar target Anda.")
        sys.exit(1)
    
    print(f"💡 Ditemukan {len(users_to_follow)} akun baru untuk di-follow.")

    try:
        max_follow = int(input(f"{Styles.PROMPT}Berapa jumlah maksimal akun yang ingin di-follow dari daftar ini? (0 untuk batal): {Styles.RESET}"))
        if max_follow <= 0:
            print("Proses dibatalkan.")
            sys.exit(1)
        users_to_follow = users_to_follow[:max_follow]
    except ValueError:
        print("Input tidak valid. Proses dibatalkan.")
        sys.exit(1)
        
    confirmation = input(f"{Styles.WARNING}❓ Anda akan mencoba follow {len(users_to_follow)} akun. Lanjutkan? (y/n): {Styles.RESET}").lower().strip()
    if confirmation != 'y':
        print("Proses dibatalkan.")
        sys.exit(1)

    print(f"\n{Styles.HEADER}--- Fase 3: Memulai Proses Follow ---")
    followed_count = 0
    for i, user in enumerate(users_to_follow):
        print(f"\n({i+1}/{len(users_to_follow)})")
        if follow_user(user):
            followed_count += 1
        
        delay = random.randint(20, 30)
        
        # --- KODE YANG DIPERBAIKI ADA DI SINI ---
        # Logika Countdown Timer
        for remaining in range(delay, 0, -1):
            sys.stdout.write(f"\r   {Styles.INFO}Jeda keamanan: {remaining:02d} detik... ")
            sys.stdout.flush()
            time.sleep(1)
        
        # Membersihkan baris setelah countdown selesai
        sys.stdout.write(f"\r   {Styles.SUCCESS}Jeda selesai. Melanjutkan ke target berikutnya... \n")
        
    print(f"\n{Styles.HEADER}===================================")
    print(f"    ✨ Proses Selesai! ✨")
    print(f"{Styles.SUCCESS}  Berhasil follow {followed_count} dari {len(users_to_follow)} target akun.")
    print(f"{Styles.HEADER}===================================")

if __name__ == "__main__":
    try:
        run_bot()
    except KeyboardInterrupt:
        print(f"\n\n{Styles.WARNING}Program dihentikan oleh pengguna.")
        sys.exit(0)
# --- Main Program Flow ---

def run_bot():
    """Main function to run the entire bot logic."""
    banner = f"""
{Styles.HEADER}====================================================
          G H O S T F O L L O W E R  v2.0
     (Targeting Followers from User List)
{Styles.RESET}
 {Styles.INFO}Created by     : {Styles.PROMPT}nhazlipse{Styles.RESET}
 {Styles.INFO}GitHub         : {Styles.PROMPT}https://github.com/Nhazlipse{Styles.RESET}
 {Styles.INFO}Active User    : {Styles.PROMPT}{YOUR_USERNAME}{Styles.RESET}
"""
    print(banner)

    target_users = baca_target_users()
    if target_users is None:
        sys.exit(1)

    print(f"\n{Styles.HEADER}--- Phase 1: Collecting Target Followers ---")
    all_target_followers = set()
    for user in target_users:
        followers = get_list_from_api(user, "followers")
        if followers:
            all_target_followers.update(followers)
    
    if not all_target_followers:
        print(f"\n{Styles.ERROR}No followers were successfully collected from all targets. Program stopped.")
        sys.exit(1)
        
    print(f"\n{Styles.SUCCESS}A total of {len(all_target_followers)} unique followers were successfully collected.")

    print(f"\n{Styles.HEADER}--- Phase 2: Analysis & Filtering ---")
    my_following = get_list_from_api(YOUR_USERNAME, "following")
    if my_following is None:
        print(f"\n{Styles.ERROR}Failed to retrieve your own following list. Program stopped.")
        sys.exit(1)
    
    users_to_follow = sorted(list(all_target_followers - my_following))

    if not users_to_follow:
        print(f"\n{Styles.SUCCESS}🎉 Great! You are already following all followers from your target list.")
        sys.exit(1)
    
    print(f"💡 Found {len(users_to_follow)} new accounts to follow.")

    try:
        max_follow = int(input(f"{Styles.PROMPT}How many accounts do you want to follow from this list? (0 to cancel): {Styles.RESET}"))
        if max_follow <= 0:
            print("Process cancelled.")
            sys.exit(1)
        users_to_follow = users_to_follow[:max_follow]
    except ValueError:
        print("Invalid input. Process cancelled.")
        sys.exit(1)
        
    confirmation = input(f"{Styles.WARNING}❓ You are about to try following {len(users_to_follow)} accounts. Continue? (y/n): {Styles.RESET}").lower().strip()
    if confirmation != 'y':
        print("Process cancelled.")
        sys.exit(1)

    print(f"\n{Styles.HEADER}--- Phase 3: Starting Follow Process ---")
    followed_count = 0
    batch_size = 25
    for i, user in enumerate(users_to_follow):
        print(f"\n({i+1}/{len(users_to_follow)})")
        if follow_user(user):
            followed_count += 1

        delay = random.randint(20, 30)

        # Countdown Timer Logic
        for remaining in range(delay, 0, -1):
            sys.stdout.write(f"\r   {Styles.INFO}Safety pause: {remaining:02d} seconds... ")
            sys.stdout.flush()
            time.sleep(1)

        sys.stdout.write(f"\r   {Styles.SUCCESS}Pause finished. Continuing to next target... \n")

        # Batch pause after every 25 follows
        if (i + 1) % batch_size == 0 and (i + 1) < len(users_to_follow):
            print(f"\n{Styles.WARNING}Batch of {batch_size} follows completed. Pausing for 5 minutes to avoid rate limits...")
            for remaining in range(5 * 60, 0, -1):
                mins, secs = divmod(remaining, 60)
                sys.stdout.write(f"\r   {Styles.INFO}Batch cooldown: {mins:02d}:{secs:02d} remaining... ")
                sys.stdout.flush()
                time.sleep(1)
            sys.stdout.write(f"\r   {Styles.SUCCESS}Batch cooldown finished. Continuing...\n")

    print(f"\n{Styles.HEADER}===================================")
    print(f"    ✨ Process Finished! ✨")
    print(f"{Styles.SUCCESS}  Successfully followed {followed_count} out of {len(users_to_follow)} target accounts.")
    print(f"{Styles.HEADER}===================================")

if __name__ == "__main__":
    try:
        run_bot()
    except KeyboardInterrupt:
        print(f"\n\n{Styles.WARNING}Program stopped by user.")
        sys.exit(0)
====================================================
{Styles.RESET}
 {Styles.INFO}Dibuat oleh    : {Styles.PROMPT}nhazlipse{Styles.RESET}
 {Styles.INFO}GitHub         : {Styles.PROMPT}https://github.com/Nhazlipse{Styles.RESET}
 {Styles.INFO}Pengguna Aktif : {Styles.PROMPT}{YOUR_USERNAME}{Styles.RESET}
"""
    print(banner)

    target_users = baca_target_users()
    if target_users is None:
        sys.exit(1)

    print(f"\n{Styles.HEADER}--- Fase 1: Mengumpulkan Target Followers ---")
    all_target_followers = set()
    for user in target_users:
        followers = get_list_from_api(user, "followers")
        if followers:
            all_target_followers.update(followers)
    
    if not all_target_followers:
        print(f"\n{Styles.ERROR}Tidak ada followers yang berhasil dikumpulkan dari semua target. Program berhenti.")
        sys.exit(1)
        
    print(f"\n{Styles.SUCCESS}Total {len(all_target_followers)} followers unik berhasil dikumpulkan.")

    print(f"\n{Styles.HEADER}--- Fase 2: Analisis & Filter ---")
    my_following = get_list_from_api(YOUR_USERNAME, "following")
    if my_following is None:
        print(f"\n{Styles.ERROR}Gagal mengambil daftar following Anda sendiri. Program berhenti.")
        sys.exit(1)
    
    users_to_follow = sorted(list(all_target_followers - my_following))

    if not users_to_follow:
        print(f"\n{Styles.SUCCESS}🎉 Hebat! Anda sudah mengikuti semua followers dari daftar target Anda.")
        sys.exit(1)
    
    print(f"💡 Ditemukan {len(users_to_follow)} akun baru untuk di-follow.")

    try:
        max_follow = int(input(f"{Styles.PROMPT}Berapa jumlah maksimal akun yang ingin di-follow dari daftar ini? (0 untuk batal): {Styles.RESET}"))
        if max_follow <= 0:
            print("Proses dibatalkan.")
            sys.exit(1)
        users_to_follow = users_to_follow[:max_follow]
    except ValueError:
        print("Input tidak valid. Proses dibatalkan.")
        sys.exit(1)
        
    confirmation = input(f"{Styles.WARNING}❓ Anda akan mencoba follow {len(users_to_follow)} akun. Lanjutkan? (y/n): {Styles.RESET}").lower().strip()
    if confirmation != 'y':
        print("Proses dibatalkan.")
        sys.exit(1)

    print(f"\n{Styles.HEADER}--- Fase 3: Memulai Proses Follow ---")
    followed_count = 0
    for i, user in enumerate(users_to_follow):
        print(f"\n({i+1}/{len(users_to_follow)})")
        if follow_user(user):
            followed_count += 1
        
        delay = random.randint(20, 30)
        
        # --- KODE YANG DIPERBAIKI ADA DI SINI ---
        # Logika Countdown Timer
        for remaining in range(delay, 0, -1):
            sys.stdout.write(f"\r   {Styles.INFO}Jeda keamanan: {remaining:02d} detik... ")
            sys.stdout.flush()
            time.sleep(1)
        
        # Membersihkan baris setelah countdown selesai
        sys.stdout.write(f"\r   {Styles.SUCCESS}Jeda selesai. Melanjutkan ke target berikutnya... \n")
        
    print(f"\n{Styles.HEADER}===================================")
    print(f"    ✨ Proses Selesai! ✨")
    print(f"{Styles.SUCCESS}  Berhasil follow {followed_count} dari {len(users_to_follow)} target akun.")
    print(f"{Styles.HEADER}===================================")

if __name__ == "__main__":
    try:
        run_bot()
    except KeyboardInterrupt:
        print(f"\n\n{Styles.WARNING}Program dihentikan oleh pengguna.")
        sys.exit(0)
