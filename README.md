# WorshipKeys — Local Laptop App

WorshipKeys runs on your own Windows laptop at **http://127.0.0.1:8000**. Two or more laptops can use separate local copies while sharing one PostgreSQL database, so accounts, songs, lyrics, chords, accompaniment settings, ideas, comments and likes stay synchronized over the internet.

## What is local, and what is shared?

- The app and its web server run locally on each laptop.
- The PostgreSQL database is shared online.
- Both laptops must have an internet connection to sign in and synchronize changes.
- The app is not dependent on the public Render web-service URL. Render PostgreSQL is used only as the shared data store.

## First-time setup (Windows)

1. Install Python 3.11 or newer from https://www.python.org/downloads/. During setup, select **Add Python to PATH**.
2. Download this repository to each laptop (GitHub → Code → Download ZIP), then extract it to a normal folder such as `Documents\WorshipKeys`.
3. Open the Render dashboard for the `worshipkeys-db` PostgreSQL database.
4. Open **Connect** and copy the **External Database URL**. The external URL is needed because your laptops connect from outside Render. Keep it private; it contains database credentials.
5. Double-click `run_worshipkeys.bat`. On first launch it creates `.env` and opens it in Notepad.
6. In `.env`, replace the DATABASE_URL placeholder with the External Database URL. Set ADMIN_PASSWORD to a new, strong, unique password for the WorshipKeys administrator account. Do not use a password you use for email or other accounts.
7. Save `.env`, close Notepad, and double-click `run_worshipkeys.bat` again.
8. WorshipKeys opens at http://127.0.0.1:8000. Sign in with the administrator email and the ADMIN_PASSWORD you configured.

Repeat steps 1–5 on the second laptop. Copy the same DATABASE_URL and use the same administrator password only if that laptop is also intended to be an administrator device. Keep each laptop's `.env` file private.

## Members

Other users can create their own accounts from the sign-in screen. The administrator account is provisioned from `ADMIN_EMAIL` and `ADMIN_PASSWORD` in the private `.env` file and cannot be created through public registration.

## Important

- Never upload `.env` to GitHub or send the database URL/password in chat.
- Keep the command window open while using WorshipKeys; closing it stops the local app.
- To stop the app, focus the command window and press Ctrl+C.
- This setup requires internet access for shared accounts and synchronization. Offline editing and later sync are not included yet.
- The current Render free PostgreSQL database is temporary and is scheduled to expire on **December 21, 2026**. Migrate to a persistent database before that date or the shared data may be lost.
