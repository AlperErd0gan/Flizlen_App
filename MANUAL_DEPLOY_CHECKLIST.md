# 🟢 AWS EC2 Manual Deployment Checklist

This is your master checklist for the **"Clean Deployment"** strategy.

### ⚡️ Quick Answer: "Does it keep running if I close terminal?"
**YES.** That is exactly what `tmux` does.
*   It creates a "virtual terminal" session on the server.
*   When you "detach" (`CTRL+B` then `D`), the session stays alive in the background.
*   You can disconnect SSH, shut down your laptop, and the app runs 24/7.
*   You can reconnect later with `tmux attach -t flizlen`.

---

### 1️⃣ Launch & Connect
*   [ ] Launch **New** EC2 Instance (Ubuntu 22.04 LTS).
*   [ ] Allow Ports in Security Group: `22` (SSH), `8000` (API), `8501` (UI).
*   [ ] SSH into instance:
    ```bash
    ssh -i /path/to/key.pem ubuntu@<PUBLIC_IP>
    ```

### 2️⃣ One-Time Setup
*Run these commands once on the new server:*
```bash
# Update & Install Tools
sudo apt-get update && sudo apt-get install -y python3-venv python3-pip git tmux

# Clone Repo
git clone https://github.com/AlperErd0gan/Flizlen_App flizlen
cd flizlen

# Setup Python Environment
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# Permissions
chmod +x start_monolith.sh
```

### 3️⃣ Start the App (The "Tmux" Way)
*   [ ] Start a new persistent session:
    ```bash
    tmux new -s flizlen
    ```
*   [ ] **(Inside Tmux)** Set your API Key:
    ```bash
    export GEMINI_API_KEY="AIzaSy..."  # Replace with REAL key
    ```
*   [ ] **(Inside Tmux)** Run the Monolith Script:
    ```bash
    ./start_monolith.sh
    ```
    *(You should see "Starting Backend" and "Starting Frontend" logs)*

### 4️⃣ Detach & Leave
*   [ ] **Detach** from session (Leave it running):
    *   Press `CTRL + B`, release both, then press `D`.
    *   (You are now back in the main terminal, but app is running).
*   [ ] Close SSH connection: `exit`

### 📋 Maintenance Commands
*   **Check Status:** `tmux attach -t flizlen`
*   **Stop App:** Attach, then `CTRL+C` (stops script), or kill session: `tmux kill-session -t flizlen`
*   **Update Code:**
    ```bash
    cd ~/flizlen
    git pull
    # Then restart the script inside tmux
    ```
