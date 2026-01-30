import cv2
import frame_comparison as frmcp
import notification_n_sound as nns

cap = cv2.VideoCapture(2, cv2.CAP_DSHOW)  # OBS Virtual Camera

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

#to capture a frame form obs virtual camara <taken as temp_frame this is comapred agisnt refrence
def frame_capt():
    ret, frame = cap.read()
    if ret:
        cv2.imwrite("temp_frame_capture.png", frame)
        return True
    else:
        print("No frame grabbed")
        return False

def start_monitering():
    frame_capt()
    frmcp.refrence_selector()
    if frmcp.frame_comp():
        nns.alert()

#start_monitering()
