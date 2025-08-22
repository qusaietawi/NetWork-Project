# Project1 — Task 1 (Mini HTTP Server + Bilingual Web) & Task 2 (UDP Number Game)

A tidy little two-part project:

- **Task 1:** A tiny, dependency-free HTTP server in Python that serves a bilingual (EN/AR) static website with a clean UI, dark-mode toggle, and animated sections.
- **Task 2:** A multiplayer **UDP number game** (server + client) where players try to survive by sending **unique numbers (1–100)** each round.

> **Ports note:** Both tasks default to **port 5012**. Because Task 1 binds TCP and Task 2 binds UDP **on the same port**, you **cannot run both at the same time** unless you change at least one port in the code.

---

## 📁 Project Structure

```text
Project1/
├─ Task1/                      # Static website + minimal HTTP server
│  ├─ css/
│  │  └─ style.css
│  ├─ html/
│  │  ├─ main_en.html
│  │  ├─ main_ar.html
│  │  ├─ event_details.html
│  │  └─ event_details_ar.html
│  ├─ imgs/                    # images + one demo mp4
│  └─ server.py                # TCP HTTP server (localhost:5012 by default)
│
└─ Task2/
   └─ UDP_Number_Game/
      ├─ server.py            # UDP game server (0.0.0.0:5012 by default)
      └─ client.py            # UDP game client (connects to localhost:5012)
