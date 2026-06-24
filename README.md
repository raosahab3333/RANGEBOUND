# RangeBound Scanner 📊

A premium range-bound trading strategy scanner for NSE India stocks.

Automatically scans **Nifty 500 + custom stocks** daily for institutional trading ranges using swing detection, zone clustering, and alternating pivot validation.

## 🚀 Features

- **Smart Detection**: ATR-adaptive swing detection with 15% minimum move enforcement
- **Alternating Pivots**: Strict S→R→S→R validation with zone clustering
- **Confidence Score**: 0-100 composite score from 10 quality factors
- **Trade Score**: 1-10 actionable trade rating
- **Fundamental Filter**: Auto-checks net profit & revenue growth via Screener.in
- **Premium Dashboard**: Dark-themed interactive HTML report with charts
- **Mobile PWA**: Install on Android as a native-like app

## 📱 Access on Mobile

This scanner runs automatically every weekday morning via GitHub Actions and deploys the report to GitHub Pages.

### Install as App on Android:
1. Open the GitHub Pages URL in **Chrome**
2. Tap the **⋮** menu (3 dots)
3. Tap **"Add to Home Screen"**
4. Done! The app icon appears on your home screen

## ⚙️ Setup (One-Time)

### 1. Create GitHub Repository
1. Go to [github.com](https://github.com) and sign in
2. Click **"New Repository"**
3. Name it `rangebound` (or any name you like)
4. Set to **Public** (required for free GitHub Pages)
5. Click **"Create repository"**

### 2. Push Code
```bash
cd range-bound-strategy
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/rangebound.git
git push -u origin main
```

### 3. Enable GitHub Pages
1. Go to your repo → **Settings** → **Pages**
2. Under **Source**, select **GitHub Actions**
3. Save

### 4. Run First Scan
1. Go to repo → **Actions** tab
2. Click **"Range Bound Scanner"** workflow
3. Click **"Run workflow"** → **"Run workflow"**
4. Wait ~7-10 minutes for the scan to complete
5. Your report will be live at: `https://YOUR_USERNAME.github.io/rangebound/`

### 5. Install on Phone
1. Open the URL on your Android phone in Chrome
2. Tap ⋮ → **"Add to Home Screen"**
3. App icon appears — opens full screen like a native app!

## 🔄 Automatic Daily Scans

The scanner runs automatically at **9:30 AM IST** (4:00 AM UTC) every weekday via GitHub Actions. No PC needed!

You can also trigger a manual scan anytime from the **Actions** tab on GitHub.

## 📄 License

Personal use only. Created by Vishal Yadav.
