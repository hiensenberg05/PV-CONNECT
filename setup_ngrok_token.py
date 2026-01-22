"""
Interactive ngrok token setup helper
This script helps you set up your ngrok auth token easily
"""

import subprocess
import sys
import webbrowser

def main():
    print("\n" + "="*80)
    print("🔑 NGROK AUTH TOKEN SETUP")
    print("="*80 + "\n")
    
    print("Step 1: Get your ngrok auth token")
    print("-" * 80)
    print("\nI'll open the ngrok dashboard in your browser...")
    print("If it doesn't open automatically, visit:")
    print("👉 https://dashboard.ngrok.com/get-started/your-authtoken\n")
    
    input("Press ENTER to open the browser...")
    
    try:
        webbrowser.open("https://dashboard.ngrok.com/get-started/your-authtoken")
        print("✅ Browser opened!\n")
    except:
        print("⚠️  Couldn't open browser automatically.")
        print("Please visit: https://dashboard.ngrok.com/get-started/your-authtoken\n")
    
    print("\n" + "="*80)
    print("Step 2: Copy your auth token from the dashboard")
    print("-" * 80)
    print("\nYou should see a token that looks like:")
    print("2abc123def456ghi789jkl0...")
    print("\nCopy the ENTIRE token.\n")
    
    token = input("Paste your ngrok auth token here: ").strip()
    
    if not token:
        print("\n❌ No token provided. Exiting.")
        sys.exit(1)
    
    print("\n" + "="*80)
    print("Step 3: Configuring ngrok...")
    print("-" * 80 + "\n")
    
    try:
        # Run ngrok config command
        result = subprocess.run(
            ["ngrok", "config", "add-authtoken", token],
            capture_output=True,
            text=True,
            check=True
        )
        
        print("✅ SUCCESS! Your ngrok auth token has been configured!\n")
        print("="*80)
        print("🎉 YOU'RE ALL SET!")
        print("="*80)
        print("\nYou can now run:")
        print("  python run_with_ngrok.py")
        print("\nOr:")
        print("  python simple_ngrok.py")
        print("\n")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error configuring ngrok: {e}")
        print("\nTry running this command manually:")
        print(f"  ngrok config add-authtoken {token}")
        sys.exit(1)
    
    except FileNotFoundError:
        print("❌ ngrok command not found!")
        print("\nAlternative: I'll add the token directly to the script...")
        
        print("\n" + "="*80)
        print("MANUAL SETUP INSTRUCTIONS")
        print("="*80)
        print("\nOption 1: Install ngrok CLI")
        print("  Download from: https://ngrok.com/download")
        print("  Then run: ngrok config add-authtoken " + token)
        
        print("\nOption 2: Use token in code (I can do this for you)")
        print("  I'll modify the scripts to include your token directly.")
        print()
        
        choice = input("Would you like me to add the token to the scripts? (y/n): ").strip().lower()
        
        if choice == 'y':
            print("\n✅ I'll update the scripts with your token...")
            return token
        else:
            print("\n⚠️  Please install ngrok CLI and run the setup again.")
            sys.exit(1)
    
    return None

if __name__ == "__main__":
    token = main()
    
    # If token is returned, it means we need to add it to the scripts
    if token:
        print(f"\n📝 Your token: {token}")
        print("I'll help you add this to the scripts in the next step.")
