try:
    import mss
    print("mss OK")
except: print("MSS ERROR")
try:
    from PIL import Image
    print("Pillow OK")
except: print("PIL error")