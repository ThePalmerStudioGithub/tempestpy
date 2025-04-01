import os
import subprocess

REPO_URL = "https://github.com/ThePalmerStudioGithub/tempestpy"
FOLDER_NAME = "tempestpy"

def clone_or_update_repo():
    if not os.path.exists(FOLDER_NAME):
        print(f"📥 Cloning repository into '{FOLDER_NAME}'...")
        try:
            subprocess.run(["git", "clone", REPO_URL, FOLDER_NAME], check=True)
            print("✅ Clone completed.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to clone repository: {e}")
    else:
        print(f"🔄 Updating existing repository in '{FOLDER_NAME}'...")
        try:
            subprocess.run(["git", "-C", FOLDER_NAME, "pull"], check=True)
            print("✅ Update completed.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to update repository: {e}")

if __name__ == "__main__":
    clone_or_update_repo()
