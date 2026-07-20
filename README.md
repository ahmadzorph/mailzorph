# 📧 MailZorph v2.0 - Advanced Email Intelligence Tool

<p align="center">
  <img src="https://img.shields.io/badge/Version-2.0-cyan.svg" alt="Version">
  <img src="https://img.shields.io/badge/Language-Python%203-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Termux%20%7C%20Linux-red.svg" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License">
</p>

**MailZorph** is a powerful, fast, and feature-rich Email Intelligence (OSINT) gathering tool designed for terminal environments (Termux / Linux). It provides rich visual output, dynamic loading animations, and comprehensive email security analysis.

---

## 🔥 Key Features

* **🔍 Format & Syntax Validation:** Checks email structure using robust regex patterns.
* **⚠️ Data Breach Lookup:** Checks if the target email has been compromised in known data leaks.
* **🛡️ Risk & Reputation Scoring:** Analyzes email risk factors and flags suspicious patterns.
* **👤 Gravatar Profile Finder:** Retrieves display names, locations, avatars, and associated profile data.
* **🌐 Domain & MX Record Inspection:** Verifies domain validity and mail server records.
* **🔗 Social Profile Scanner:** Generates potential public profile footprints across major social media networks.
* **🎨 Cyberpunk Terminal UI:** Next-level visual design built with vibrant colors and animated spinners.

---

## ⚡ Installation (Termux / Linux)

Run the following commands one by one in your terminal:

```bash
pkg update && pkg upgrade -y
pkg install git python -y
git clone [https://github.com/YOUR-USERNAME/mailzorph.git](https://github.com/YOUR-USERNAME/mailzorph.git)
cd mailzorph
pip install rich requests colorama dnspython
python main.py
