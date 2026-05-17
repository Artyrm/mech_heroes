import ftplib
import sys

def test_ftp():
    host = "89.169.30.106"
    user = "ovalhall"
    # Credentials are used directly here for a one-time test, 
    # but will NOT be stored in any persistent file.
    password = "iOi15p8I0z"
    
    print(f"Connecting to {host}...")
    try:
        ftp = ftplib.FTP(host)
        ftp.login(user, password)
        print("Login successful!")
        
        print("\nDirectory listing:")
        ftp.retrlines('LIST')
        
        ftp.quit()
        print("\nConnection closed.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_ftp()
