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
import PIL.Image
import PIL.ImageTk
import os
from tqdm.tk import trange, tqdm
from skimage.metrics import structural_similarity as ssim

# Returns filepath string of the video selected by user


def get_file() -> str:
    root = Tk()
    filename = filedialog.askopenfilename(title="Import video")
    root.destroy()
    return filename

# Create a options list, users selects the game, get_game() retrieves its reference image filepath


def get_game():
    def OK():
        root.destroy()
    root = Tk()
    root.focus_force()
    answer = StringVar()
    root.title("Choose Game")
    #hp1 = Radiobutton(root, text="HP1 Xbox/PS2/Gamecube", variable=answer, value="Images/hp1.png", state=DISABLED)
    hp2 = ttk.Radiobutton(root, text="HP2 Xbox/Gamecube",
                          variable=answer, value="Images/hp2.png")
    hp2pc = ttk.Radiobutton(root, text="HP2 PC", variable=answer,
                            value="Images/hp2pc_cs1.png;Images/hp2pc_cs2.png;Images/hp2pc_cs3.png")
    hp2ps2 = ttk.Radiobutton(root, text="HP2 PS2",
                             variable=answer, value="Images/hp2ps2.png")
    hp3 = ttk.Radiobutton(root, text="HP3 Xbox/PS2/Gamecube",
                          variable=answer, value="Images/loading.png")
    ok = Button(root, text="OK", command=OK)
    # hp1.pack()
    hp2.pack()
    hp2pc.pack()
    hp2ps2.pack()
    hp3.pack()
    ok.pack()
    root.mainloop()
    return answer.get()

# runs for each allocated process
# input: group_number_list = parameters list, includes PSNR threshold and portion of video to process
# output: number of load frames for the selected video portion
# to-do: add sleep() calls to reduce CPU usage


def process_video_multiprocessing(group_number_list):
    ref_imgs = group_number_list[0]
    x1 = group_number_list[1]
    x2 = group_number_list[2]
    y1 = group_number_list[3]
    y2 = group_number_list[4]
    threshold = group_number_list[5]
    group_number = group_number_list[6]
    filename = group_number_list[7]
    frame_jump_unit = group_number_list[8]
    startPos = group_number_list[9]
    if group_number == 0:
        pbarVal = tqdm(total=frame_jump_unit)
    cap = cv2.VideoCapture(filename)
    cap.set(cv2.CAP_PROP_POS_FRAMES, startPos +
            (frame_jump_unit * group_number))
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
            resized = cv2.resize(
                temp, (ref_imgs[0].shape[1], ref_imgs[0].shape[0]))
            # c1 = cv2.PSNR(ref_img, resized)
            if any([ssim(ref_img, resized, full=TRUE, multichannel=TRUE)[0] >= threshold for ref_img in ref_imgs]):
                load_frames += 1
            proc_frames += 1
            if group_number == 0:
                pbarVal.update(1)
    except Exception as e:
        print(e)
        cap.release()
    if group_number == 0:
        pbarVal.close()
    cap.release()
    return load_frames

# spawns processes for all video chunks, collects and tallies load frame count, converts to times and displays them


def multi_process():
    root = Tk()
    root.title("Video Results")
    root.focus_force()
    print("Video processing using {} processes...".format(num_processes))
    start_time = time.time()
    data_pairs = []
    for i in range(num_processes):
        data_pairs.append([ref_imgs, x1, x2, y1, y2, threshold,
                          i, filename, frame_jump_unit, startPos])
    p = mp.Pool(num_processes)
    counts = p.map(process_video_multiprocessing, data_pairs)
    end_time = time.time()
    total_load_frames = 0
    for count in counts:
        total_load_frames += count
    total_processing_time = end_time - start_time

    elapsed_time_label = Label(
        root, text="Time taken: {}".format(total_processing_time))
    elapsed_time_label.pack()
    print("FPS : {}".format(videoCount / total_processing_time))
    rta = datetime.timedelta(seconds=videoCount / fps)
    rta_label = Label(root, text="RTA: {}".format(rta))
    rta_label.pack()
    load_frame_count_label = Label(root, text="Total Load Frames: {}".format(total_load_frames))
    load_frame_count_label.pack()
    igt = rta - datetime.timedelta(seconds=total_load_frames/fps)
    igt_label = Label(root, text="Loadless: {}".format(igt))
    igt_label.pack()
    root.mainloop()

def single_process():
    root = Tk()
    root.title("Video Results")
    root.focus_force()
    print("Video processing using {} processes...".format(num_processes))
    start_time = time.time()
    proc_frames = 0
    load_frames = 0
    pbarVal = tqdm(total=videoCount)
    cap = cv2.VideoCapture(filename)
    cap.set(cv2.CAP_PROP_POS_FRAMES, startPos)
    try:
        while proc_frames < videoCount:
            ret, frame = cap.read()
            if not ret:
                break
            temp = frame[y1:y2, x1:x2]
            resized = cv2.resize(
                temp, (ref_imgs[0].shape[1], ref_imgs[0].shape[0]))
            # c1 = cv2.PSNR(ref_img, resized)
            if any([ssim(ref_img, resized, full=TRUE, multichannel=TRUE)[0] >= threshold for ref_img in ref_imgs]):
                load_frames += 1
            proc_frames += 1
            pbarVal.update(1)
    except Exception as e:
        print(e)
        cap.release()
    pbarVal.close()
    cap.release()
    end_time = time.time()
    total_processing_time = end_time - start_time
    elapsed_time_label = Label(
        root, text="Time taken: {}".format(total_processing_time))
    elapsed_time_label.pack()
    print("FPS : {}".format(videoCount / total_processing_time))
    rta = datetime.timedelta(seconds=videoCount / fps)
    rta_label = Label(root, text="RTA: {}".format(rta))
    rta_label.pack()
    load_frame_count_label = Label(root, text="Total Load Frames: {}".format(load_frames))
    load_frame_count_label.pack()
    igt = rta - datetime.timedelta(seconds=load_frames / fps)
    igt_label = Label(root, text="Loadless: {}".format(igt))
    igt_label.pack()
    root.mainloop()

if __name__ == '__main__':
    filename = get_file()
    ref_imgs = [cv2.imread(x) for x in get_game().split(';')]
    #ref_img = cv2.imread("Images/loading.png")
    parameters = []
    if filename is not None and os.path.isfile(filename):
        parameters = zoneselector.load_interface(filename, ref_imgs)
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
        # progress_bar.pack()
        num_processes = mp.cpu_count()//2
        frame_jump_unit = videoCount//num_processes
        multi_process()
        #single_process()
