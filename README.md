# WorshipKeys — Local Songbook

WorshipKeys runs locally on each Windows laptop at **http://127.0.0.1:8000**. Songs are stored in a local SQLite database file named `worshipkeys.db`.

## Move your songbook to another laptop

1. Open WorshipKeys on the laptop containing your songs.
2. Click **Export songbook**. It downloads one `.worshipkeys` backup file containing all song lyrics, chords, keys, transpose settings, tempo, BPM, beat, accompaniment style, categories and notes.
3. Send that file to the other laptop using WhatsApp.
4. On the receiving laptop, open WorshipKeys and click **Import backup**.
5. Select the `.worshipkeys` file and confirm.

**Import replaces the receiving laptop's current song list.** Export a backup first if you want to preserve songs already on that laptop.

## Setup

1. Install Python 3.11 or newer from https://www.python.org/downloads/ (Python 3.14.7 is fine).
2. Download this repository ZIP and extract it.
3. Double-click `run_worshipkeys.bat`.
4. WorshipKeys opens at http://127.0.0.1:8000.

The first launch installs the required Python packages. After that, songs are stored locally and the app works without internet.

## Add songs

- Click **Add song** to enter title, lyrics, chords, key, tempo, BPM, beat, accompaniment style and notes.
- Click **Import .txt** to import plain-text lyric files. Each filename becomes the song title.
- Click **Export songbook** regularly to make a portable backup.

## Important

- Each laptop has its own independent songbook. Changes do not sync automatically.
- Use Export on the first laptop and Import on the second whenever you want to transfer the latest collection.
- Import replaces the receiving laptop's current song list.
- Keep the `worshipkeys.db` file safe; it contains the local song collection.
- The local server listens only on your own laptop (127.0.0.1).
