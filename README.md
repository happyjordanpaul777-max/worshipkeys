# WorshipKeys — Local Shared Songbook

WorshipKeys runs locally on each Windows laptop at **http://127.0.0.1:8000**. Both laptop copies connect directly to the same PostgreSQL database in the cloud, so songs, lyrics, chords and keyboard settings are shared over the internet.

## How synchronization works

- The app runs locally on each laptop; it is not a public website.
- The cloud PostgreSQL database stores the shared songbook.
- The laptops do not need the same Wi-Fi network.
- Both laptops need internet access to see the latest saved songs.
- The local no-login editing API accepts requests only from the same laptop. The public Render app keeps its normal account protection.

## First laptop setup

1. Install Python 3.11 or newer from https://www.python.org/downloads/ (Python 3.14.7 is fine).
2. Download this repository ZIP and extract it into a normal folder.
3. Open the Render dashboard for the `worshipkeys-db` PostgreSQL database.
4. Open **Connect** and copy the **External Database URL**. Keep it private; it contains database credentials.
5. Double-click `run_worshipkeys.bat`. On first launch, it creates `.env` and opens it in Notepad.
6. Replace the DATABASE_URL placeholder with the External Database URL. Leave `LOCAL_SHARED_MODE=true`.
7. Save the file and close Notepad.
8. Double-click `run_worshipkeys.bat` again. WorshipKeys opens at http://127.0.0.1:8000.

## Second laptop

Repeat steps 1–8 on the second laptop. Use the exact same External Database URL and keep `LOCAL_SHARED_MODE=true`. The songs will appear on both laptops.

## Adding songs

- Click **Add song** to enter the title, lyrics, chords, key, tempo, BPM, beat, accompaniment style and notes.
- Click **Import .txt songs** to import one or more plain-text lyric files. Each filename becomes the song title; you can edit the song details afterward.
- Saved changes are stored in the shared database. The song list refreshes automatically every 20 seconds; use Refresh to check immediately.

## Important

- Never share or upload `.env`; it contains the database password.
- Keep the command window open while using WorshipKeys. Press Ctrl+C in that window to stop it.
- The laptops need internet access for synchronization. Offline editing and later sync are not supported.
- The current Render free PostgreSQL database is temporary and is scheduled to expire on **December 21, 2026**. Move to a persistent database before then or the shared songs may be lost.
