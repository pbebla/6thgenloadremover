from collections import deque
import multiprocessing as mp
import datetime
import time
from multiprocessing.pool import ThreadPool
import threading
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import threading
import zoneselector
import cv2
import PIL.Image, PIL.ImageTk
import os
from tqdm.tk import trange, tqdm
def get_file():
    root = Tk()
    filename = filedialog.askopenfilename(title="Import video")
    root.destroy()
    return filename

def get_game():
    def OK():
        root.destroy()
    root = Tk()
    root.focus_force()
    answer = StringVar()
    root.title("Choose Game")
    #hp1 = Radiobutton(root, text="HP1 Xbox/PS2/Gamecube", variable=answer, value="Images/hp1.png", state=DISABLED)
    hp2 = ttk.Radiobutton(root, text="HP2 Xbox/Gamecube", variable=answer, value="Images/hp2.png")
    hp2ps2 = ttk.Radiobutton(root, text="HP2 PS2", variable=answer, value="Images/hp2ps2.png")
    hp3 = ttk.Radiobutton(root, text="HP3 Xbox/PS2/Gamecube", variable=answer, value="Images/loading.png")
    ok = Button(root, text="OK", command=OK)
    #hp1.pack()
    hp2.pack()
    hp2ps2.pack()
    hp3.pack()
    ok.pack()
    root.mainloop()
    return answer.get()


def process_video_multiprocessing(group_number_list):
    ref_img = group_number_list[0]
    x1 = group_number_list[1]
    x2 = group_number_list[2]
    y1 = group_number_list[3]
    y2 = group_number_list[4]
    threshold = group_number_list[5]
    group_number = group_number_list[6]
    filename = group_number_list[7]
    frame_jump_unit = group_number_list[8]
    startPos = group_number_list[9]
    if group_number==0:
        pbarVal = tqdm(total=frame_jump_unit)
    cap = cv2.VideoCapture(filename)
    cap.set(cv2.CAP_PROP_POS_FRAMES, startPos + (frame_jump_unit * group_number))
    #no_of_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    #fps = int(cap.get(cv2.CAP_PROP_FPS))
    proc_frames = 0
    load_frames = 0
    try:
        while proc_frames < frame_jump_unit:
            ret, frame = cap.read()
            if not ret:
                break
            temp = frame[y1:y2, x1:x2]
            resized = cv2.resize(temp, (ref_img.shape[1], ref_img.shape[0]))
            c1 = cv2.PSNR(ref_img, resized)
            if c1>=threshold:
                load_frames+=1
            proc_frames+=1
            if group_number==0:
                pbarVal.update(1)
    except Exception as e:
        print(e)
        cap.release()
    if group_number==0:
        pbarVal.close()
    cap.release()
    return load_frames

def multi_process():
    root = Tk()
    root.title("Video Results")
    root.focus_force()
    print("Video processing using {} processes...".format(num_processes))
    start_time = time.time()
    data_pairs = []
    for i in range(num_processes):
        data_pairs.append([ref_img, x1, x2, y1, y2, threshold, i, filename, frame_jump_unit, startPos])
    p = mp.Pool(num_processes)
    counts = p.map(process_video_multiprocessing, data_pairs)
    end_time = time.time()
    total_load_frames = 0
    for count in counts:
        total_load_frames+=count
    total_processing_time = end_time - start_time

    elapsed_time_label = Label(root, text="Time taken: {}".format(total_processing_time))
    elapsed_time_label.pack()
    print("FPS : {}".format(videoCount / total_processing_time))
    rta = datetime.timedelta(seconds=videoCount / fps)
    rta_label = Label(root, text="RTA: {}".format(rta))
    rta_label.pack()

    igt = rta - datetime.timedelta(seconds=total_load_frames/fps)
    igt_label = Label(root, text="Loadless: {}".format(igt))
    igt_label.pack()
    root.mainloop()

if __name__ == '__main__':
    filename = get_file()
    ref_img = cv2.imread(get_game())
    #ref_img = cv2.imread("Images/loading.png")
    parameters = []
    if filename is not None and os.path.isfile(filename):
        parameters = zoneselector.load_interface(filename, ref_img)
        x1 = min(parameters[0], parameters[2])
        x2 = max(parameters[0], parameters[2])
        y1 = min(parameters[1], parameters[3])
        y2 = max(parameters[1], parameters[3])
        fps = parameters[7]
        startPos = parameters[4]
        endPos = parameters[5]
        videoCount = endPos - startPos
        threshold = parameters[6]

        #progress_bar = ttk.Progressbar(root, orient=HORIZONTAL, length=100, mode='determinate')
        #progress_bar.pack()
        num_processes = mp.cpu_count()//2
        frame_jump_unit = videoCount//num_processes
        multi_process()





