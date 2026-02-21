# Deploying PerfTestpro on Render

## Yes, you can host this project on Render.

Use the config below. **API Performance Test** (Manual Entry + File Upload) works out of the box. **URL Performance Test** (Lighthouse) needs Chrome/Node on the server—see caveat below.

---

## Option A: Render Dashboard (no Blueprint)

1. **Render** → [dashboard](https://dashboard.render.com) → **New** → **Web Service**.
2. Connect your GitHub repo (`PerfTestpro`).
3. Set:
   - **Name:** `perftestpro` (or any name)
   - **Region:** e.g. Oregon
   - **Branch:** `main` (or your deploy branch)
   - **Runtime:** `Python 3`
   - **Build Command:**  
     `pip install -r requirements.txt`
   - **Start Command:**  
     `streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`
4. **Create Web Service**. Render will build and deploy.

Your app will be at: `https://<service-name>.onrender.com`

---

## Option B: Render Blueprint (render.yaml)

If your repo has the included `render.yaml`:

1. **Render** → **New** → **Blueprint**.
2. Connect the repo; Render will read `render.yaml` and create the web service with the same build/start commands.

The `render.yaml` in this repo is already set up with:

- **Build:** `pip install -r requirements.txt`
- **Start:** `streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`

---

## Config summary

| Item            | Value |
|-----------------|--------|
| Build command   | `pip install -r requirements.txt` |
| Start command   | `streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0` |
| Root directory  | (leave default, repo root) |

- `$PORT` is provided by Render; do not replace it.
- `--server.address=0.0.0.0` is required so the app is reachable from the internet.

---

## URL Performance Test (Lighthouse) on Render

The **URL Performance Test** feature runs the Lighthouse CLI and needs:

- **Node.js** (for `lighthouse`)
- **Chrome/Chromium** (headless)

The default Render Python environment does not include Chrome or Node, so **URL Performance Test will not work** on a standard Render Python web service.

Options:

1. **Use only API Performance Test** on Render (Manual Entry + File Upload). No extra setup.
2. **Use Docker on Render:** Add a `Dockerfile` that installs Node, Chrome/Chromium, and Lighthouse, then run your Streamlit app there. Render can build and run that image.
3. **Keep URL Performance Test for local use only** and use Render for API testing.

---

## Optional: env vars

- `LIGHTHOUSE_OUTPUT_DIR` – optional; if set, URL tester writes reports here (e.g. for debugging). If unset, a temp directory is used (including on Render).

---

## Free tier notes (Render)

- Service may spin down after inactivity; first load after idle can take ~30–60 seconds.
- 512 MB RAM on free tier; fine for Streamlit + API tests. If you add Lighthouse in Docker, consider a paid instance for more memory.

---

## Free hosting that supports BOTH features (API + URL Performance)

Render’s free tier is **512 MB RAM**. Running Streamlit + Chrome + Lighthouse in one container often needs **~1 GB+**, so URL Performance can be slow or OOM on Render free. If you want **free-only** hosting and **both** API and URL Performance to work reliably, use one of these instead.

### Best option: Oracle Cloud Always Free

**Why:** You get real **always-free VMs** (no expiry, no credit card for the always-free tier). You install whatever you want: Python, Node, Chrome, Lighthouse, Streamlit. No 512 MB limit—you choose the VM shape.

| Resource | Always Free allowance |
|----------|------------------------|
| **AMD** | 2× VM.Standard.E2.1.Micro → **1 GB RAM, 1/8 OCPU each** |
| **ARM (Ampere)** | 4× VMs using **3,000 OCPU-hours + 18,000 GB-hours/month** (e.g. 1× 4 GB VM or 2× 2 GB) |

- **AMD (1 GB)**: Enough for Streamlit + Lighthouse if you keep usage light (e.g. one URL at a time).
- **ARM (e.g. 4 GB)**: More comfortable for both API and URL Performance; recommended if you use Lighthouse often.

**Steps (high level):**

1. Sign up: [oracle.com/cloud/free](https://www.oracle.com/cloud/free/) (no card needed for always-free).
2. Create a compute instance: **Ubuntu 22.04**, shape **VM.Standard.E2.1.Micro** (AMD, 1 GB) or an **Ampere A1** shape (ARM, e.g. 2–4 GB).
3. Open ports: allow **22** (SSH) and **8501** (Streamlit) in the VM’s security list / ingress rules.
4. SSH in and install Python 3.11, Node.js 20, Google Chrome (or Chromium), and `lighthouse` (see **[Oracle Cloud setup guide](docs/ORACLE_CLOUD_SETUP.md)** for copy-paste commands).
5. Clone the repo, `pip install -r requirements.txt`, then run:
   ```bash
   ./scripts/run-oracle-cloud.sh
   ```
   or: `streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0`
6. (Optional) Use the example systemd unit in `scripts/perftestpro.service.example` so the app restarts on reboot.

**No code changes needed for Oracle Cloud.** The app detects a Linux server without a display and uses the correct Chrome flags for Lighthouse. Full step-by-step: **[docs/ORACLE_CLOUD_SETUP.md](docs/ORACLE_CLOUD_SETUP.md)**.

**Docs:** [Always Free Resources](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm). Community: [Deploying Streamlit on Oracle Cloud Always Free](https://discuss.streamlit.io/t/deploying-on-oracle-cloud-always-free-instance/24478).

---

### Other free(ish) options (short summary)

| Platform | Free tier | Both features? | Notes |
|----------|-----------|-----------------|--------|
| **Oracle Cloud Always Free** | 1–4 GB VM(s), no time limit | ✅ Yes | Best for “free forever” + both; you manage the server. |
| **Render** | 512 MB | ⚠️ Tight with Docker + Chrome | API tests fine; URL Performance may OOM or be slow. |
| **Koyeb** | 512 MB, 1 web service | ⚠️ Same as Render | Docker supported; Chrome in 512 MB is tight. |
| **Fly.io** | 3× 256 MB or short trial | ❌ No | Free VMs too small for Chrome; trial is time-limited. |
| **Railway** | Credit-based ($5 trial, then usage) | ⚠️ Possible | Not “free forever”; need to stay within credits. |
| **Streamlit Community Cloud** | Python apps only | ❌ No | No Docker, no Chrome/Node; API tests only. |
| **Google Cloud Run** | Usage-based free tier | ⚠️ Possible | Billing account required; can run Docker + Chrome if within free quota. |

**Takeaway:** For **free only** and **both API + URL Performance**, use **Oracle Cloud Always Free** (and optionally this repo’s Dockerfile as a reference for installing Node + Chrome + Lighthouse on the VM).
