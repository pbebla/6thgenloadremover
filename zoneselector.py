from tkinter import *
from tkinter import ttk
import cv2
from DrawableRectangle import DrawableRectangle
from PIL import ImageTk, Image

# input: string of filename path, string of refrence image path
# launchs interface for user to input parameters
# output: bounds of watch zone, start and end frame, PSNR threshold, video FPS


def load_interface(filename, ref_imgs):
    root = Tk()
    root.title("Cyna's HP 6th Gen Load Remover")
    root.focus_force()
    root.resizable(TRUE, TRUE)
    cap = cv2.VideoCapture(filename)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    frameCount = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    _, img = cap.read()
    canvas = DrawableRectangle(root, width=width, height=height, ref_imgs=ref_imgs, img=img, bg="red")

    def getPSNRVal():
        nonlocal ref_imgs, img
        canvas.set_img(img)
        updatePreview()

    _x1 = IntVar(0)
    _x2 = IntVar(0)
    _y1 = IntVar(0)
    _y2 = IntVar(0)
    _start = IntVar(0)
    _end = IntVar(0)
    controls_frame = Frame(root)
    controls_frame.pack()
    _x2.set(width)
    _y2.set(height)
    x1_label = ttk.Label(controls_frame, text="x1:")
    x1_label.pack(side=LEFT)
    x1_value = ttk.Spinbox(controls_frame, from_=0, to=width, width=8,
                           textvariable=canvas.x1, takefocus=True, command=getPSNRVal)
    x1_value.pack(side=LEFT)
    x2_label = ttk.Label(controls_frame, text="x2:")
    x2_label.pack(side=LEFT)
    x2_value = ttk.Spinbox(controls_frame, from_=0, to=width, width=8,
                           textvariable=canvas.x2, takefocus=True, command=getPSNRVal)
    x2_value.pack(side=LEFT)
    y1_label = ttk.Label(controls_frame, text="y1:")
    y1_label.pack(side=LEFT)
    y1_value = ttk.Spinbox(controls_frame, from_=0, to=height, width=8,
                           textvariable=canvas.y1, takefocus=True, command=getPSNRVal)
    y1_value.pack(side=LEFT)
    y2_label = ttk.Label(controls_frame, text="y2:")
    y2_label.pack(side=LEFT)
    y2_value = ttk.Spinbox(controls_frame, from_=0, to=height, width=8,
                           textvariable=canvas.y2, takefocus=True, command=getPSNRVal)
    y2_value.pack(side=LEFT)

    start_label = ttk.Label(controls_frame, text="Start:")
    start_label.pack(side=LEFT)
    start_value = ttk.Spinbox(
        controls_frame, from_=0, to=frameCount, width=8, textvariable=_start, takefocus=True)
    start_value.pack(side=LEFT)
    end_label = ttk.Label(controls_frame, text="End:")
    end_label.pack(side=LEFT)
    end_value = ttk.Spinbox(controls_frame, from_=0, to=frameCount,
                            width=8, textvariable=_end, takefocus=True)
    end_value.pack(side=LEFT)

    #canvas = Canvas(root, bd=0, highlightthickness=0, width=width, height=height)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    canvas_img = ImageTk.PhotoImage(Image.fromarray(img))
    drawing = canvas.create_image(0, 0, image=canvas_img, anchor=NW)
    canvas.configure(scrollregion=canvas.bbox(ALL))
    canvas.pack(fill=BOTH, expand=YES)

    def on_resize(e):
        img1 = Image.fromarray(img)
        wratio = img1.width/img1.height
        hratio = img1.height/img1.width
        resized_img = img1.resize((int(e.height*wratio), int(e.width*hratio)), Image.ANTIALIAS)
        new_img = ImageTk.PhotoImage(resized_img)
        canvas.create_image(0,0,image=new_img, anchor="nw")
        canvas.pack()

    def slide(var):
        nonlocal drawing, canvas, canvas_img, img
        cap.set(cv2.CAP_PROP_POS_FRAMES, slider.get())
        _, img = cap.read()
        if drawing is not None:
            canvas.delete(drawing)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        canvas.set_img(img)
        canvas_img = ImageTk.PhotoImage(Image.fromarray(img))
        drawing = canvas.create_image(0, 0, image=canvas_img, anchor=NW)
        canvas._set_image_internal()
        getPSNRVal()
        canvas.pack()

    slider_frame = Frame(root)
    slider_frame.pack()
    slider = Scale(slider_frame, from_=0, to=frameCount,
                   orient=HORIZONTAL, command=slide, length=width)
    slider.pack(side=BOTTOM)

    def quickStart():
        nonlocal _start
        _start.set(slider.get())
    quick_start = ttk.Button(
        controls_frame, text="Select Start From Video", command=quickStart)
    quick_start.pack(side=LEFT)

    def quickEnd():
        nonlocal _end
        _end.set(slider.get())
    quick_end = ttk.Button(
        controls_frame, text="Select End From Video", command=quickEnd)
    quick_end.pack(side=LEFT)

    psnrLabel = ttk.Label(controls_frame, textvariable=canvas.psnrVal)
    canvas.getPSNR()
    psnrLabel.pack(side=LEFT)
    #psnrButton = ttk.Button(controls_frame, text="Update PSNR", command=getPSNRVal)
    # psnrButton.pack(side=LEFT)

    def updatePreview(e=""):
        if (abs(canvas.y2.get() - canvas.y1.get()) != 0 and abs(canvas.x2.get() - canvas.x1.get()) != 0):
            _x1 = min(int(canvas.x1.get()), int(canvas.x2.get()))
            _y1 = min(int(canvas.y1.get()), int(canvas.y2.get()))
            _x2 = max(int(canvas.x1.get()), int(canvas.x2.get()))
            _y2 = max(int(canvas.y1.get()), int(canvas.y2.get()))
            preview_img = img[_y1:_y2, _x1:_x2]
            preview_img = cv2.resize(
                preview_img, (ref_imgs[0].shape[1], ref_imgs[0].shape[0]))
            canvas.getPSNR()
            preview_img = cv2.subtract(preview_img, ref_imgs[canvas.which])
            preview_img = ImageTk.PhotoImage(Image.fromarray(preview_img))
            preview_img_value.configure(image=preview_img, text="")
            preview_img_value.image = preview_img

    #previewButton = ttk.Button(controls_frame, text="Update Preview")
    # previewButton.pack(side=LEFT)
    psnrFrame = Frame(controls_frame)
    psnrLabel = Label(psnrFrame, text="Enter PSNR Threshold")
    psnrLabel.pack(side=TOP)
    psnrVal = StringVar("")
    psnrEntry = ttk.Entry(psnrFrame, textvariable=psnrVal)
    psnrEntry.pack(side=BOTTOM)
    psnrFrame.pack(side=LEFT)
    result = []

    fpsFrame = Frame(controls_frame)
    fpsFrame.pack(side=LEFT)
    fpsLabel = Label(fpsFrame, text="Enter FPS (Optional)")
    fpsLabel.pack(side=TOP)
    fpsVal = DoubleVar(0.0)
    fpsEntry = ttk.Entry(fpsFrame, textvariable=fpsVal)
    fpsEntry.pack(side=BOTTOM)

    def OK():
        nonlocal root, result, cap
        result = (canvas.x1.get(),
                  canvas.y1.get(),
                  canvas.x2.get(),
                  canvas.y2.get(),
                  _start.get(),
                  _end.get(),
                  float(psnrVal.get()),
                  max(fpsVal.get(), float(cap.get(cv2.CAP_PROP_FPS))))
        cap.release()
        root.destroy()

    okB = ttk.Button(controls_frame, text="OK", command=OK)
    okB.pack(side=RIGHT)

    # ref_img_img = ImageTk.PhotoImage(Image.fromarray(
    #     cv2.cvtColor(ref_img, cv2.COLOR_BGR2RGB)))
    # ref_img_label = Label(root, image=ref_img_img)
    # ref_img_label.pack(side=LEFT)
    ref_imgs_imgs = []
    ref_imgs_labels = []
    for ref_img in ref_imgs:
        ref_img_img = ImageTk.PhotoImage(Image.fromarray(
            cv2.cvtColor(ref_img, cv2.COLOR_BGR2RGB)))
        ref_imgs_imgs.append(ref_img_img)
        ref_img_label = Label(root, image=ref_img_img)
        ref_img_label.pack(side=LEFT)
        ref_imgs_labels.append(ref_img_label)

    preview_img_value = Label(
        root, text="Selected Region comparison will go here once created")
    preview_img_value.pack(side=LEFT)

    #previewButton.bind("<Button-1>", updatePreview)
    canvas.bind("<Motion>", updatePreview)
    canvas.bind("<Configure>", on_resize)
    root.mainloop()
    return result
