import os
import ftplib
from dotenv import load_dotenv

def deploy():
    load_dotenv()
    
    host = os.getenv("FTP_HOST")
    user = os.getenv("FTP_USER")
    password = os.getenv("FTP_PASS")
    base_path = os.getenv("FTP_PATH")
    
    if not all([host, user, password, base_path]):
        print("Error: FTP credentials missing in .env file.")
        return

    # Files to upload
    files_to_upload = {
        "arena/reports/dashboard.html": "dashboard.html",
        "arena/reports/suppression_core.png": "suppression_core.png",
        "battle_analytics/personal_stats.html": "personal.html",
        "clan_monitor/clan_accountant_report.html": "clan.html" 
    }

    try:
        print(f"Connecting to {host}...")
        ftp = ftplib.FTP(host)
        ftp.login(user, password)
        
        # Ensure target directories exist
        dirs = base_path.split('/')
        current_dir = ""
        for d in dirs:
            current_dir += d + "/"
            try:
                ftp.mkd(current_dir)
                print(f"Created directory: {current_dir}")
            except:
                pass # Already exists
        
        ftp.cwd(base_path)
        
        for local_path, remote_name in files_to_upload.items():
            if os.path.exists(local_path):
                print(f"Uploading {local_path} as {remote_name}...")
                with open(local_path, "rb") as f:
                    ftp.storbinary(f"STOR {remote_name}", f)
            else:
                print(f"Warning: {local_path} not found, skipping.")
                
        # Upload squads
        squads_dir = "arena/reports/squads"
        if os.path.exists(squads_dir):
            try: ftp.mkd("squads")
            except: pass
            
            for fname in os.listdir(squads_dir):
                if fname.endswith('.html'):
                    local_path = os.path.join(squads_dir, fname)
                    with open(local_path, "rb") as f:
                        ftp.storbinary(f"STOR squads/{fname}", f)
            print(f"Uploaded squads HTML files.")

        # Upload Arena Data (Lazy loading JSONs)
        arena_data_dir = "arena/reports/data"
        if os.path.exists(arena_data_dir):
            try: ftp.mkd("data")
            except: pass
            for fname in os.listdir(arena_data_dir):
                if fname.endswith('.json'):
                    local_path = os.path.join(arena_data_dir, fname)
                    with open(local_path, "rb") as f:
                        ftp.storbinary(f"STOR data/{fname}", f)
            print(f"Uploaded Arena snapshot data files.")
        
        # Upload personal analytics (dossiers and battle reports)
        analytics_dir = "battle_analytics"
        if os.path.exists(analytics_dir):
            for nick in os.listdir(analytics_dir):
                nick_dir = os.path.join(analytics_dir, nick)
                if os.path.isdir(nick_dir) and not nick.startswith('__') and nick != 'snapshots':
                    # Create remote directory for the player
                    try: ftp.mkd(nick)
                    except: pass
                    
                    for fname in os.listdir(nick_dir):
                        if fname.endswith('.html'):
                            local_path = os.path.join(nick_dir, fname)
                            with open(local_path, "rb") as f:
                                ftp.storbinary(f"STOR {nick}/{fname}", f)
            
            # Upload Prowess Snapshots
            snap_dir = os.path.join(analytics_dir, "snapshots")
            if os.path.exists(snap_dir):
                try: ftp.mkd("snapshots")
                except: pass
                for fname in os.listdir(snap_dir):
                    if fname.endswith('.html'):
                        local_path = os.path.join(snap_dir, fname)
                        with open(local_path, "rb") as f:
                            ftp.storbinary(f"STOR snapshots/{fname}", f)

            print(f"Uploaded personal dossier, battle reports and snapshots.")

        ftp.quit()
        print("\nDeployment successful!")
        print(f"Reports available at: http://ovalhalla.ru/my/mech/arena.html")
        
    except Exception as e:
        print(f"Deployment error: {e}")

if __name__ == "__main__":
    deploy()
