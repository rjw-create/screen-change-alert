"""Watch a screen through the webcam and beep when what it shows changes.

Run `python screen_alert.py --help` for options.
"""

import argparse
import sys
import time

import cv2

try:
    import winsound
except ImportError:
    winsound = None

# Auto-exposure takes a few seconds to settle after the camera opens, and
# comparing against those frames triggers false alerts. Wait until brightness
# stops moving, but never longer than the limit.
WARMUP_STABLE_FRAMES = 30
WARMUP_MAX_SECONDS = 10

# How quickly the reference image follows gradual change (lighting, exposure
# adjustments). Measured on a laptop camera, 0.1 kept exposure drift below 2%
# while a sudden screen change still shows up in full on the first frame.
DRIFT_RATE = 0.1


def parse_args():
    parser = argparse.ArgumentParser(
        description="Play a sound when the screen in front of the camera changes."
    )
    parser.add_argument("--camera", type=int, default=0,
                        help="camera index (default: 0, the built-in camera)")
    parser.add_argument("--threshold", type=float, default=5.0,
                        help="percent of the watched area that must change to "
                             "trigger an alert (default: 5.0)")
    parser.add_argument("--pixel-delta", type=int, default=25,
                        help="brightness difference (0-255) for a pixel to count "
                             "as changed; raise it if camera noise causes "
                             "false alerts (default: 25)")
    parser.add_argument("--cooldown", type=float, default=3.0,
                        help="seconds to wait after an alert before the next "
                             "one (default: 3.0)")
    parser.add_argument("--select-region", action="store_true",
                        help="draw a box around the screen at startup so "
                             "movement elsewhere in view is ignored")
    parser.add_argument("--preview", action="store_true",
                        help="show the camera view and live change percentage")
    parser.add_argument("--sound", metavar="WAV",
                        help="path to a .wav file to play instead of a beep "
                             "(Windows only)")
    return parser.parse_args()


def open_camera(index):
    # DirectShow opens much faster than the default backend on Windows.
    backend = cv2.CAP_DSHOW if sys.platform == "win32" else cv2.CAP_ANY
    cap = cv2.VideoCapture(index, backend)
    if not cap.isOpened():
        sys.exit(f"Could not open camera {index}. Check that no other app is "
                 "using it and that camera access is allowed in Windows "
                 "Settings > Privacy & security > Camera.")
    return cap


def read_frame(cap):
    ok, frame = cap.read()
    if not ok:
        sys.exit("Lost the camera feed.")
    return frame


def wait_for_exposure(cap):
    print("Letting the camera adjust...")
    recent = []
    deadline = time.monotonic() + WARMUP_MAX_SECONDS
    while time.monotonic() < deadline:
        gray = cv2.cvtColor(read_frame(cap), cv2.COLOR_BGR2GRAY)
        recent = (recent + [gray.mean()])[-WARMUP_STABLE_FRAMES:]
        if len(recent) == WARMUP_STABLE_FRAMES and max(recent) - min(recent) < 2:
            return


def prepare(frame, region):
    if region:
        x, y, w, h = region
        frame = frame[y:y + h, x:x + w]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Blurring smooths out sensor noise and screen flicker so only real
    # content changes stand out.
    return cv2.GaussianBlur(gray, (21, 21), 0)


def changed_percent(reference, current, pixel_delta):
    diff = cv2.absdiff(reference, current)
    _, mask = cv2.threshold(diff, pixel_delta, 255, cv2.THRESH_BINARY)
    return 100.0 * cv2.countNonZero(mask) / mask.size


def alert(sound_path):
    if winsound is None:
        print("\a", end="", flush=True)
    elif sound_path:
        winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
    else:
        winsound.Beep(1000, 300)


def main():
    args = parse_args()
    cap = open_camera(args.camera)

    wait_for_exposure(cap)

    region = None
    if args.select_region:
        frame = read_frame(cap)
        print("Drag a box around the screen, then press Enter or Space. "
              "Press C to cancel and watch the whole view.")
        x, y, w, h = cv2.selectROI("Select screen", frame, showCrosshair=False)
        cv2.destroyWindow("Select screen")
        if w and h:
            region = (x, y, w, h)

    reference = prepare(read_frame(cap), region)
    last_alert = 0.0
    print(f"Watching for changes over {args.threshold}% "
          "(Ctrl+C to stop" + (", or Q in the preview window)." if args.preview else ")."))

    try:
        while True:
            frame = read_frame(cap)
            current = prepare(frame, region)
            percent = changed_percent(reference, current, args.pixel_delta)

            now = time.monotonic()
            if now - last_alert < args.cooldown:
                # Keep following the screen while it finishes changing, so
                # one change (like a page loading) produces one alert.
                reference = current
            elif percent >= args.threshold:
                print(f"{time.strftime('%H:%M:%S')}  change detected ({percent:.1f}%)")
                alert(args.sound)
                last_alert = now
                reference = current
            else:
                # Track slow lighting drift so it never adds up to an alert.
                reference = cv2.addWeighted(reference, 1 - DRIFT_RATE,
                                            current, DRIFT_RATE, 0)

            if args.preview:
                if region:
                    x, y, w, h = region
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"change: {percent:.1f}%", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.imshow("Screen alert", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
