# screen-change-alert

Point a camera at another screen (a monitor, TV, lab instrument, phone) and
get a beep whenever what it shows changes.

There are two versions that work the same way:

- **Web page** (`index.html`): runs in a phone or laptop browser, with
  nothing to install. On a phone it uses the back camera.
- **Python script** (`screen_alert.py`): runs on a Windows computer with a
  webcam.

Both grab frames from the camera, convert them to blurred grayscale, and
compare each one to a reference image of the screen. When more than a set
percentage of the picture has changed, they play a sound, log the time, and
start comparing against the new screen contents.

## Web version

Open **https://rjw-create.github.io/screen-change-alert/** in your phone's
browser (Chrome on Android, Safari on iPhone) or on a laptop.

1. Press **Start** and allow camera access.
2. Point the camera at the screen and hold it steady. A stand or something to
   lean the phone against works best.
3. Press **Draw region** and drag a box around the screen, so movement around
   it is ignored.
4. Press **Test sound** to check you can hear the alert.
5. Watch the change number while the screen is idle, and set **Alert when
   this much changes** comfortably above it.

Settings are remembered in that browser. On Android the phone also vibrates
on each alert.

Things to know:

- **Keep the page open and the screen on.** Phones turn the camera off when
  the screen locks or you switch apps. The page asks the browser to keep the
  screen awake, but some browsers or battery saver modes refuse.
- **iPhone silent mode:** with the iPhone set to silent, the beep may not
  play. Turn silent mode off and the volume up.
- **Background tabs on a laptop:** if the page is in a tab you are not
  looking at, the browser slows it down, so alerts can be delayed by a
  second or more.
- **Camera access needs a secure address**: `https://`, or `localhost` on the
  same computer.

To run the web page locally on your laptop instead:

```powershell
python -m http.server 8000
```

Then open http://localhost:8000 in your browser.

## Python version: setup (Windows, PowerShell)

Requires Python 3.10 or newer.

```powershell
git clone https://github.com/rjw-create/screen-change-alert.git
```

```powershell
cd screen-change-alert
```

```powershell
python -m venv .venv
```

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Usage

Recommended first run: pick the screen area and watch the live change
percentage so you can tune the threshold.

```powershell
.\.venv\Scripts\python.exe screen_alert.py --select-region --preview
```

A window opens with the camera view. Drag a box around the screen you want to
watch and press Enter. Movement outside the box (people, your hands) is then
ignored. Stop with Ctrl+C, or Q in the preview window.

Once it is tuned, run it without the preview:

```powershell
.\.venv\Scripts\python.exe screen_alert.py --select-region
```

### Options

| Option | Default | What it does |
| --- | --- | --- |
| `--camera N` | `0` | Which camera to use. Try `1` for an external webcam. |
| `--threshold P` | `5.0` | Percent of the watched area that must change to alert. Lower is more sensitive. |
| `--pixel-delta D` | `25` | How much (0-255) a pixel's brightness must change to count. Raise it if camera noise causes false alerts. |
| `--cooldown S` | `3.0` | Seconds after an alert before another can fire. |
| `--select-region` | off | Draw a box around the screen at startup. |
| `--preview` | off | Show the camera view with the current change percentage. |
| `--sound FILE.wav` | beep | Play a `.wav` file instead of the default beep. |

### Tuning tips

- Run with `--preview` and watch the `change:` number while the screen is
  idle. Set `--threshold` comfortably above that idle number.
- A blinking cursor or clock on the watched screen can trigger alerts. Use
  `--select-region` to leave it out of the box, or raise `--threshold`.
- Keep the laptop still. Moving the camera changes the whole picture.
- Steady room lighting helps. Slow lighting drift is tracked automatically,
  but switching a lamp on will trigger an alert.

## Platform notes

Sound uses Python's built-in `winsound` module, which exists only on Windows.
On macOS or Linux the script falls back to the terminal bell, and `--sound`
has no effect.

If the camera will not open, close other apps that use it (Teams, Zoom, the
Camera app) and check Windows Settings > Privacy & security > Camera.

## License

MIT. See [LICENSE](LICENSE).
