import cv2
import numpy as np


def refrence_selector():
    # Load reference image (UNCHANGED)
    img = cv2.imread("B.A_refrence_dia.png")
    assert img is not None, "reference.png not found"

    orig_h, orig_w = img.shape[:2]

    # --- scale for display only ---
    MAX_W, MAX_H = 1200, 800  # adjust if you want it bigger
    scale = min(MAX_W / orig_w, MAX_H / orig_h, 1.0)

    disp = cv2.resize(
        img,
        (int(orig_w * scale), int(orig_h * scale)),
        interpolation=cv2.INTER_AREA
    )

    # Select ROI on the scaled image
    roi = cv2.selectROI(
        "Select reference region (ENTER to confirm, ESC to cancel)",
        disp,
        fromCenter=False,
        showCrosshair=True
    )

    x, y, w, h = roi

    if w > 0 and h > 0:
        # Map ROI back to original image coordinates
        x0 = int(x / scale)
        y0 = int(y / scale)
        x1 = int((x + w) / scale)
        y1 = int((y + h) / scale)

        crop = img[y0:y1, x0:x1]
        cv2.imwrite("reference_crop.png", crop)

        print(f"Saved reference_crop.png ({x1-x0}x{y1-y0})")
    else:
        print("No region selected")

    cv2.destroyAllWindows()

def frame_comp():
    template = cv2.imread("reference_crop.png", cv2.IMREAD_GRAYSCALE)
    frame = cv2.imread("temp_frame_capture.png", cv2.IMREAD_GRAYSCALE)

    assert template is not None
    assert frame is not None

    # Edges to remove text/background noise
    template_e = cv2.Canny(template, 80, 160)
    frame_e = cv2.Canny(frame, 80, 160)

    th, tw = template_e.shape[:2]

    result = cv2.matchTemplate(
        frame_e,
        template_e,
        cv2.TM_CCOEFF_NORMED
    )

    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    print(f"Token match confidence: {max_val:.3f}")

    # MUCH higher threshold because token is distinctive
    THRESHOLD = 0.70

    if max_val >= THRESHOLD:
        x, y = max_loc

        # ---- POSITION FILTER ----
        h, w = frame.shape[:2]
        if y < h * 0.35:
            print("❌ Match ignored (too high on screen)")
            return False

        # Debug
        debug = cv2.cvtColor(frame_e, cv2.COLOR_GRAY2BGR)
        cv2.rectangle(debug, (x, y), (x+tw, y+th), (0, 255, 0), 2)
        cv2.imwrite("match_debug.png", debug)

        print("✅ Dialogue option detected via token")
        return True

    print("❌ No dialogue option")
    return False