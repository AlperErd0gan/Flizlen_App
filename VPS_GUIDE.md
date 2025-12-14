# 🚀 Flizlen App - Hostinger VPS Deployment Guide

Follow these steps to deploy your application to a Hostinger VPS (Ubuntu).

## Prerequisites
1.  **Hostinger VPS**: Clean install of **Ubuntu 20.04** or **22.04**.
2.  **SSH Access**: You should know the IP address and root password.

## 1. Connect to your VPS
Open your terminal (on Mac) and run:
```bash
ssh root@<YOUR_VPS_IP>
# Enter your password when prompted
```

## 2. Clone the Repository
Install git if needed (usually installed, but `setup_vps.sh` handles it too) and clone your code.
*(Note: Since your repo might be private, you may need to use a Personal Access Token or SSH key. For simplicity, we assume you can clone it)*.

```bash
cd /root
git clone <YOUR_GITHUB_REPO_URL> flizlen
cd flizlen
```
*If you haven't pushed code to GitHub yet, do that first!*

## 3. Run the Setup Script
This script installs Python, Nginx, and sets everything up.

```bash
# Give execution permission
chmod +x setup_vps.sh

# Run the script (Pass your IP as an argument for Nginx)
./setup_vps.sh <YOUR_VPS_IP>
```
*Example: `./setup_vps.sh 123.45.67.89`*

## 4. That's it!
Your app should now be accessible at `http://<YOUR_VPS_IP>`.

## 5. Maintenance Commands

-   **Check Status**: `systemctl status flizlen`
-   **View Logs**: `journalctl -u flizlen -f`
-   **Restart App**: `systemctl restart flizlen`
-   **Update Code**:
    ```bash
    cd /root/flizlen
    git pull
    systemctl restart flizlen
    ```

## ⚠️ Important Note on Database
Your `database.db` is now stored on the VPS disk. It will **NOT** be deleted when you restart the app.
HOWEVER, if you do `git pull` and the repo has a *newer* empty `database.db`, git might try to conflict.
**Recommendation**: Add `database.db` to `.gitignore` on the server or use `git checkout database.db` to discard local changes before pulling if you don't care about server data (but you do!).
**Best Practice**: The `database.db` on the server is the "Truth". Back it up periodically!
