from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import os
import threading
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Application(Tk):

    def __init__(self):
        super(Application, self).__init__()
        # variables
        self.width = 1280
        self.height = 600
        self.position_x = ( self.winfo_screenwidth() - self.width ) / 2
        self.position_y = ( self.winfo_screenheight() - self.height ) / 23
        self.capture = None
        self.mode = False
        self.last_image = None
        self.tracker_object = None
        # configure
        self["padx"] = 15
        self["pady"] = 15
        self.title("Tracker")
        self.geometry("%dx%d+%d+%d" % (self.width, self.height, self.position_x, self.position_y))
        self.resizable(False, False)
        self.wm_protocol("WM_DELETE_WINDOW", self.close)
        
        self.design()

    def design(self):
        self.frame_left = Frame(self)
        self.frame_left.pack(side="left", fill='y')
        self.frame_control = Frame(self.frame_left, padx=10, pady=5, bd=2, relief="groove")
        self.frame_control.pack(fill='both', expand=1)
        # style
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("TButton", font=(None, 13))
        # state tracker
        self.frame_state_tracker = Frame(self.frame_control, height=5, bg="#f00")
        self.frame_state_tracker.pack(fill="both", expand=1, pady=5)
        # buttons
        self.btarget = ttk.Button(self.frame_control, text="Target", takefocus=False, state="disabled", command=self.selectObject)
        self.btarget.pack(fill="both", expand=1, pady=5)
        self.bstart = ttk.Button(self.frame_control, text="Start", command=self.start, takefocus=False)
        self.bstart.pack(fill="both", expand=1, pady=5)
        self.bstop = ttk.Button(self.frame_control, text="Stop", state="disabled", command=self.stop, takefocus=False)
        self.bstop.pack(fill="both", expand=1, pady=5)
        # logo
        self.logo = self.photoimage(os.path.join(BASE_DIR, "logo.png"), (218, 270))
        self.lbl_logo = Label(self.frame_left, image=self.logo, bd=2, relief="groove")
        self.lbl_logo.pack(pady=15)
        # display
        self.lbl_display = Label(self)
        self.lbl_display.pack(fill="both", expand=1, side="left", padx=(10, 0))
        self.lbl_display.update()
    
    def photoimage(self, img, size: tuple[int,int]=None):
        img = Image.open(img)
        if size:
            img = img.resize(size)
        img = ImageTk.PhotoImage(img)
        return img

    def display(self, img, width , height):
        image = Image.fromarray(img)
        image = image.resize((width, height))
        image = ImageTk.PhotoImage(image)
        self.lbl_display["image"] = image
        self.lbl_display.image = image

    def tracking(self):
        # ready camera
        self.capture = cv2.VideoCapture(0)
        # get width, height from label
        width, height = int(self.lbl_display.winfo_width()), int(self.lbl_display.winfo_height())
        # change mode to 1 run tracking
        self.mode = True
        # chagne state for buttons
        self.bstop["state"] = NORMAL
        self.bstart["state"] = DISABLED
        self.btarget["state"] = DISABLED

        # start tracking
        while True:
            # get image from camera
            _, image = self.capture.read()
            # set last image
            self.last_image = image
            if self.tracker_object:
                success, new_bbox = self.tracker_object.update(image)
                if success:
                    x,y,w,h = [int(v) for v in new_bbox]
                    cv2.rectangle(image, (x,y), (x+w, y+h), (0,255,0), 2)
                    self.frame_state_tracker["bg"] = "#0f0"
                else:
                    self.frame_state_tracker["bg"] = "#f00"
                    print("Not Found")
            # convert bgr to rgb
            image = cv2.cvtColor(image , cv2.COLOR_BGR2RGB)
            # show image
            self.display(image, width, height)
            # check mode & stop tracking
            if not self.mode:
                break
        
        # stop camera
        self.capture.release()
    
    def start(self):
        new_thread = threading.Thread(target=self.tracking)
        new_thread.start()

    def stop(self):
        self.mode = False
        self.bstop["state"] = DISABLED
        self.bstart["state"] = NORMAL
        self.btarget["state"] = NORMAL

    def selectObject(self):
        self.new_bbox = cv2.selectROI("Object", self.last_image, False)
        self.tracker_object = cv2.legacy.TrackerCSRT_create()
        self.tracker_object.init(self.last_image, self.new_bbox)
        cv2.destroyAllWindows()
    
    def close(self):
        self.mode = False
        if self.capture:
            self.capture.release()
        time.sleep(.5)
        os._exit(0)

if __name__ == "__main__":
    root = Application()
    root.mainloop()
