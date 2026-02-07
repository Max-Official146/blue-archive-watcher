# FrameTrace >.<

**Visual state monitoring & detection tool**  
by **Stella Group** ✨

> “Stop staring at the screen. Let FrameTrace do it.”

---

## 👀 What is FrameTrace?

FrameTrace is a **profile-based visual monitoring desktop application**.

It watches a live video input (typically via **OBS Virtual Camera**), compares what it sees against **user-defined visual references**, and alerts you when a specific visual state appears on screen.

Everything runs **locally**:
- no cloud services
- no accounts
- no background uploads
- no hidden automation

---

## ✨ Design Philosophy

FrameTrace is intentionally:

- 🧠 **Deterministic** — no black-box AI, no mystery behavior  
- 🧱 **Modular** — clear separation between UI, detection, and data  
- 🧹 **Safe with files** — user data is never overwritten during updates  
- 😴 **Boring to extend** — predictable code paths by design  

FrameTrace is **not game-specific**, **not cloud-based**, and **not AI hype**.  
It’s a local, power-user tool for people who want control.

---

## 🎯 Detection & Artifact Persistence

- Monitoring runs detection directly against **in-memory camera frames** using  
  `frame_comp_from_array`, avoiding per-cycle disk round-trips.
- File-based detection (`frame_comp`) remains available for manual and debug
  workflows that intentionally operate on `captures/latest.png`.

### Capture & Debug Retention

Artifact persistence is **optional, throttled, and bounded**.

Retention behavior is configured in `core/detector.py`:

- `capture_snapshot_interval_s` — minimum interval between capture snapshots  
- `capture_retention_count` — maximum retained `captures/snapshot_*.png` files  
- `debug_retention_count` — maximum retained `debug/match_*.png` files  

Additional behavior:
- A forced capture snapshot is recorded when a **new detection event starts**
- Retention rules are enforced immediately after capture

This guarantees:
- no unbounded disk growth
- predictable storage usage
- safe long-running sessions

---

## 💾 Data & Updates

All user data is stored in the `Data/` folder next to the executable: