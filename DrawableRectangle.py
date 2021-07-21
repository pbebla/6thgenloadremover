from tkinter import *
from tkinter import ttk
import cv2
import PIL.Image
from PIL import ImageTk
from skimage.metrics import structural_similarity as ssim


def clip(bottom, value, top):
    if value >= top:
        return top
    elif value <= bottom:
        return bottom
    else:
        return value


class DrawableRectangle(Canvas):

    def __init__(self, master, ref_imgs, img, **kw):
        super().__init__(master, **kw)
        self.drawnrect = None
        self.bind("<Button-1>", self._mouse_down)
        self.bind('<B1-Motion>', self._mouse_move)
        self.x1 = IntVar(0)
        self.y1 = IntVar(0)
        self.x2 = IntVar(0)
        self.y2 = IntVar(0)
        self.width = self.winfo_width()
        self.height = self.winfo_height()
        self.x1.trace("w", self.redraw_rect)
        self.y1.trace("w", self.redraw_rect)
        self.x2.trace("w", self.redraw_rect)
        self.y2.trace("w", self.redraw_rect)
        self.HP3_x1 = 0.42708333333
        self.HP3_x2 = 0.5625
        self.HP3_y1 = 0.84489187173
        self.HP3_y2 = 0.89560029828
        self.references = ref_imgs
        self.img = img
        self.psnrVal = DoubleVar(0.0)
        self.which = 0


    def set_img(self, img):
        self.img = img

    def _mouse_down(self, event):
        x = int(event.x)
        y = int(event.y)
        self.set_point_1(x, y)
        self.set_point_2(x, y)
        self.getPSNR()

    def _mouse_move(self, event):
        x = int(clip(0, event.x, self.winfo_width()))
        y = int(clip(0, event.y, self.winfo_height()))
        self.set_point_2(x, y)
        self.getPSNR()
        # self.redraw_rect()

    def redraw_rect(self, *args):
        _x1 = self.x1.get()
        _y1 = self.y1.get()
        _x2 = self.x2.get()
        _y2 = self.y2.get()
        if self.drawnrect is None:
            self.drawnrect = self.create_rectangle(
                _x1, _y1, _x2, _y2, outline="red")
        else:
            self.coords(self.drawnrect, _x1, _y1, _x2, _y2)

    def set_point_1(self, x, y):
        ih, iw = self.winfo_height(), self.winfo_width()
        self.x1.set(clip(0, x, iw))
        self.y1.set(clip(0, y, ih))

    def set_point_2(self, x, y):
        ih, iw = self.winfo_height(), self.winfo_width()
        self.x2.set(clip(0, x, iw))
        self.y2.set(clip(0, y, ih))

    def _set_image_internal(self):
        if self.drawnrect is not None:
            self.tag_raise(self.drawnrect)

    def getPSNR(self):
        _x1 = min(int(self.x1.get()), int(self.x2.get()))
        _y1 = min(int(self.y1.get()), int(self.y2.get()))
        _x2 = max(int(self.x1.get()), int(self.x2.get()))
        _y2 = max(int(self.y1.get()), int(self.y2.get()))
        if(abs(_x2-_x1) != 0 and abs(_y2-_y1) != 0):
            tempImg = self.img[_y1:_y2, _x1:_x2]
            resized = cv2.resize(
                # TODO: Verify that each reference image is the same size --Ted
                tempImg, (self.references[0].shape[1], self.references[0].shape[0]))

            max_value = -1
            grayResized = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            for i in range(len(self.references)):
                grayRef = cv2.cvtColor(self.references[i], cv2.COLOR_BGR2GRAY)
                value, diff = ssim(grayRef, grayResized, full=TRUE)
                #value = cv2.PSNR(self.references[i], resized)
                if value > max_value:
                    max_value = value
                    self.which = i

            self.psnrVal.set(max_value)
            return self.psnrVal.get()
