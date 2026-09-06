# 🗓️ Weekly App

A modern desktop and web application designed for managing weekly schedules, tasks, and priorities. Built using **HTML, CSS, and JavaScript** for the UI, packaged into a desktop application using **Python (CustomTkinter)**, and fully deployable to **Vercel** for web access.

---

## ✨ Features

* **🌐 Web & Desktop Ready:** Works natively as a desktop app on **macOS** & **Windows**, or instantly in any browser via Vercel.
* **🎨 Modern Web UI:** Designed with HTML5, CSS3, and JavaScript featuring sleek animations and dark mode styling.
* **📅 Weekly Task Scheduler:** Organize tasks, set priorities, and manage your weekly layout effortlessly.
* **💾 Local Storage Persistence:** Saves your schedule locally in the browser/app so your data persists across restarts.

---

## 🛠️ Tech Stack

* **Frontend:** HTML5, CSS3, JavaScript (ES6+)
* **Desktop Wrapper:** Python 3.10+, CustomTkinter, `tkinterweb` / `pywebview`
* **Web Hosting:** Vercel
* **Executable Build Tool:** PyInstaller

---

## 🌐 Live Web Version

You can access the live web application directly without installing anything:

👉 **[Launch Weekly App on Vercel](https://your-vercel-app-name.vercel.app)** *(Replace with your deployed URL)*

---

## 🚀 Web Deployment (Vercel)

Deploy your web files (`index.html`, `style.css`, `script.js`) to Vercel in a few clicks.

### Option A: Import via GitHub (Recommended)

<Sequence>
  <Step title="Connect GitHub to Vercel" subtitle="Initial integration">
    Log in to [Vercel](https://vercel.com/) with your GitHub account.
  </Step>
  <Step title="Add New Project" subtitle="Select repository">
    Click **Add New...** -> **Project** on your Vercel Dashboard, then select `RenzyyyCursors/Weekly-app-`.
  </Step>
  <Step title="Configure Root Directory" subtitle="Ensure index.html is detected">
    If your `index.html` is inside a folder (e.g., `src/`), set the **Root Directory** setting on Vercel to `src`. If it's at the root of your repo, leave it as `./`.
  </Step>
  <Step title="Deploy" subtitle="Automated CI/CD setup">
    Click **Deploy**. Vercel will generate your live `.vercel.app` URL and automatically redeploy whenever you push changes to GitHub.
  </Step>
</Sequence>

### Option B: Deploy using Vercel CLI

```bash
# 1. Install Vercel CLI globally
npm i -g vercel

# 2. Login to Vercel from terminal
vercel login

# 3. Deploy directly from your project directory
vercel
