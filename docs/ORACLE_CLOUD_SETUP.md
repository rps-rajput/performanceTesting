# PerfTestpro on Oracle Cloud Always Free – Step-by-step

This guide gets both **API Performance Test** and **URL Performance Test** (Lighthouse) running on an Oracle Cloud Always Free Ubuntu VM. No code changes required beyond what’s already in the repo.

---

## 1. Create the VM

1. Sign up: [oracle.com/cloud/free](https://www.oracle.com/cloud/free/) (no card needed for always-free).
2. In Oracle Cloud Console: **Compute** → **Instances** → **Create Instance**.
3. Choose:
   - **Image:** Ubuntu 22.04
   - **Shape:** **VM.Standard.E2.1.Micro** (1 GB RAM, AMD) or **Ampere** (e.g. 2–4 GB) if you want more headroom for Lighthouse.
4. Add SSH key (or generate one) and create the instance.
5. **Networking:** In the instance’s **Subnet** → **Security List**, add an **Ingress** rule:
   - **Source:** `0.0.0.0/0`
   - **Destination port:** `8501`  
   (Keep port 22 for SSH.)

---

## 2. SSH in and install dependencies

Replace `your-instance-ip` with the instance’s public IP.

```bash
ssh ubuntu@your-instance-ip
```

Then run (copy-paste as a block):

```bash
sudo apt-get update
sudo apt-get install -y software-properties-common curl

# Python 3.11
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev

# Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Google Chrome (for Lighthouse)
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/google-linux-signing-key.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-signing-key.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update
sudo apt-get install -y google-chrome-stable

# Lighthouse
sudo npm install -g lighthouse
```

**On ARM (Ampere) instances:** Use Chromium instead of Chrome if the Chrome package isn’t available:

```bash
sudo apt-get install -y chromium-browser
# Lighthouse will use chromium; no code change needed if it’s on PATH as chromium.
```

If `lighthouse` expects `google-chrome` or `google-chrome-stable`, you can add a symlink (e.g. `sudo ln -sf /usr/bin/chromium-browser /usr/bin/google-chrome-stable`) so the app keeps working.

---

## 3. Clone the app and run

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/PerfTestpro.git
cd PerfTestpro

python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run (listens on 0.0.0.0:8501 so it's reachable from the internet)
chmod +x scripts/run-oracle-cloud.sh
./scripts/run-oracle-cloud.sh
```

Or without the script:

```bash
streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
```

Open **http://your-instance-ip:8501** in your browser. Both API and URL Performance tests should work; the app detects a Linux server without a display and uses the right Chrome flags for Lighthouse.

---

## 4. (Optional) Run as a service and on reboot

```bash
# Edit paths and user in the example unit, then:
sudo cp scripts/perftestpro.service.example /etc/systemd/system/perftestpro.service
sudo nano /etc/systemd/system/perftestpro.service   # set WorkingDirectory, User, ExecStart path to your venv
sudo systemctl daemon-reload
sudo systemctl enable perftestpro
sudo systemctl start perftestpro
sudo systemctl status perftestpro
```

---

## 5. Optional env vars

| Variable | Purpose |
|----------|--------|
| `PORT` | Override port (default 8501). Used by `run-oracle-cloud.sh`. |
| `LIGHTHOUSE_OUTPUT_DIR` | Directory for Lighthouse report files. If unset, a temp dir is used. |
| `PERFTESTPRO_HEADLESS=1` | Force server-style Chrome flags (normally auto-detected on Linux without DISPLAY). |

---

## Troubleshooting

- **Lighthouse fails (Chrome not found):** Install `google-chrome-stable` (or Chromium on ARM) and ensure `lighthouse --version` works. If you use Chromium, a symlink to `google-chrome-stable` can help.
- **Can’t open the app in browser:** Ensure the security list allows **ingress** on port **8501** from `0.0.0.0/0`.
- **Chrome crashes on Lighthouse run:** The app automatically adds `--no-sandbox --disable-dev-shm-usage` etc. on Linux when there’s no DISPLAY; if you still see issues, set `PERFTESTPRO_HEADLESS=1` and ensure at least 1 GB RAM (2–4 GB preferred for multiple URLs).
