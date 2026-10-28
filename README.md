# screen-change-alert

Point your laptop camera at another screen (a monitor, TV, lab instrument,
phone) and get a beep whenever what it shows changes.

The script grabs frames from the camera, converts them to blurred grayscale,
and compares each one to a reference image of the screen. When more than a
set percentage of the picture has changed, it plays a sound, prints the time,
and starts comparing against the new screen contents.

## Setup (Windows, PowerShell)

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
