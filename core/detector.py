import cv2
import os
import time
from core.profiles import get_profile_dirs

# ---- dialogue state ----
_active_dialogue = None        # name of reference currently active
_last_seen_time = 0.0          # last time dialogue was visible
EXIT_TIMEOUT = 0.6             # seconds dialogue must disappear to reset

_debug_counter = 0


def refrence_selector(profile_name):
    dirs = get_profile_dirs(profile_name)

    frames_dir = dirs["frames"]
    base_frames = [f for f in os.listdir(frames_dir) if f.lower().endswith(".png")]
    assert base_frames, "No base frames found for this profile"

    base_path = os.path.join(frames_dir, base_frames[0])
    img = cv2.imread(base_path)
    assert img is not None, "Base frame could not be loaded"

    orig_h, orig_w = img.shape[:2]
    scale = min(1200 / orig_w, 800 / orig_h, 1.0)

    disp = cv2.resize(
        img,
        (int(orig_w * scale), int(orig_h * scale)),
        interpolation=cv2.INTER_AREA
    )

    roi = cv2.selectROI(
        "Select reference region (ENTER to confirm, ESC to cancel)",
        disp,
        fromCenter=False,
        showCrosshair=True
    )

    x, y, w, h = roi
    if w <= 0 or h <= 0:
        cv2.destroyAllWindows()
        return

    x0, y0 = int(x / scale), int(y / scale)
    x1, y1 = int((x + w) / scale), int((y + h) / scale)
    crop = img[y0:y1, x0:x1]

    ref_dir = dirs["references"]
    existing = [f for f in os.listdir(ref_dir) if f.endswith(".png")]
    ref_path = os.path.join(ref_dir, f"ref_{len(existing) + 1}.png")

    cv2.imwrite(ref_path, crop)
    cv2.destroyAllWindows()


def frame_comp(profile_name):
    global _active_dialogue, _last_seen_time, _debug_counter

    dirs = get_profile_dirs(profile_name)
    frame_path = os.path.join(dirs["captures"], "latest.png")

    if not os.path.exists(frame_path):
        return False

    frame = cv2.imread(frame_path, cv2.IMREAD_GRAYSCALE)
    if frame is None:
        return False

    frame_e = cv2.Canny(frame, 80, 160)
    now = time.time()

    matched_ref = None
    match_bbox = None

    for ref in os.listdir(dirs["references"]):
        ref_path = os.path.join(dirs["references"], ref)
        template = cv2.imread(ref_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            continue

        template_e = cv2.Canny(template, 80, 160)
        result = cv2.matchTemplate(frame_e, template_e, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val < 0.70:
            continue

        x, y = max_loc
        h, w = template_e.shape[:2]

        # stabilize position to kill jitter
        GRID = 8
        x = (x // GRID) * GRID
        y = (y // GRID) * GRID

        matched_ref = ref
        match_bbox = (x, y, w, h)
        break  # first valid match is enough

    # -------- STATE LOGIC --------

    if matched_ref is not None:
        _last_seen_time = now

        # same dialogue still active → do nothing
        if _active_dialogue == matched_ref:
            return True

        # NEW dialogue detected
        _active_dialogue = matched_ref
        _debug_counter += 1

        debug = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        x, y, w, h = match_bbox
        cv2.rectangle(debug, (x, y), (x + w, y + h), (0, 255, 0), 2)

        debug_path = os.path.join(
            dirs["debug"],
            f"match_{_debug_counter:04d}.png"
        )
        cv2.imwrite(debug_path, debug)

        return True

    # no match this frame → check for exit
    if _active_dialogue and now - _last_seen_time > EXIT_TIMEOUT:
        _active_dialogue = None

    return False
def crop_existing_reference(profile_name, ref_name):
    from core.profiles import get_profile_dirs
    import cv2
    import os

    dirs = get_profile_dirs(profile_name)
    ref_path = os.path.join(dirs["references"], ref_name)

    img = cv2.imread(ref_path)
    if img is None:
        return False

    roi = cv2.selectROI(
        "Select crop (ENTER to confirm, ESC to cancel)",
        img,
        fromCenter=False,
        showCrosshair=True
    )

    x, y, w, h = roi
    if w <= 0 or h <= 0:
        cv2.destroyAllWindows()
        return False

    crop = img[y:y+h, x:x+w]

    existing = [
        f for f in os.listdir(dirs["references"])
        if f.startswith(ref_name.replace(".png", "_crop"))
    ]

    crop_name = f"{ref_name.replace('.png', '')}_crop{len(existing)+1}.png"
    crop_path = os.path.join(dirs["references"], crop_name)

    cv2.imwrite(crop_path, crop)
    cv2.destroyAllWindows()
    return True
