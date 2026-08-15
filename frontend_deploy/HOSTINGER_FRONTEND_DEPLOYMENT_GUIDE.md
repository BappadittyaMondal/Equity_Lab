# Step 1 Deployment Guide — Hostinger Business Frontend Upload

Follow these quick 4 steps to deploy your **IERL Stitch UI** to your Hostinger Business Hosting account right now:

---

## 📁 Files Included in Deployment Package (`frontend_deploy/`)

- `index.html` — Production-ready HTML5 dark-mode institutional terminal.
- `style.css` — Required production stylesheet.

---

## 🚀 Step-by-Step Upload Instructions (Takes 2 Minutes)

### Step 1: Log in to Hostinger hPanel
1. Open [Hostinger hPanel](https://hpanel.hostinger.com/) in your web browser.
2. Click on **Websites** and select your domain (e.g., `yourdomain.com`).

### Step 2: Open File Manager
1. In your domain dashboard, search for **File Manager** (or click **Files -> File Manager**).
2. Click **Access Files of yourdomain.com**.

### Step 3: Upload `index.html` to `public_html`
1. Double-click the **`public_html`** directory to open it.
2. If there is a default Hostinger `default.php` or `index.php` placeholder, you can rename or delete it.
3. In `index.html`, set the `ierl-api-base` meta tag to your HTTPS backend URL (for example, your Render service URL). Do not leave it blank on a static Hostinger deployment.
4. Click the **Upload** button (top right corner icon with an arrow pointing up).
5. Upload both `index.html` and `style.css` from `frontend_deploy/` to `public_html`.
6. Configure the backend `ALLOWED_ORIGIN` to include your Hostinger domain.

### Step 4: Verify Your Website is Live!
1. Open `https://yourdomain.com` in your browser.
2. You will see your **IERL Institutional Command Center** live with dark mode, strategy buttons, regime indicators, and AI Assistant query panel!

---

## 🎯 What Happens Next?

- The interface is live once both files are uploaded, but analytical features require a separately deployed backend.
- There is no simulated-analysis fallback: failed live requests are displayed as failures.
- Configure and test the backend before presenting the site as an active research product.
