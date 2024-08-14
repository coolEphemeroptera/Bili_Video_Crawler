from threading import Thread
import threading
from queue import Queue
import time 
import random
import string
import warnings
import subprocess
import os
import shutil
warnings.filterwarnings("ignore") 

FFMPEG = "ffmpeg.exe"
YOUGET = "you-get.exe"

def mkdir(path, reset=False):
    # 检查目录是否存在
    if os.path.exists(path):
        if reset:
            # 安全地删除目录及其所有内容
            shutil.rmtree(path)
            print(f"Removed existing directory: {path}")

    # 无论是否需要重置，都确保目录被创建
    try:
        os.makedirs(path)
        print(f"Directory created: {path}")
    except OSError as e:
        # 捕捉可能的异常，如权限不足或路径为文件时无法创建目录
        print(f"Error creating directory: {e}")
        return None  # 或者根据你的错误处理策略抛出异常或返回特定值

    return path


def generate_random_string(n):
    letters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(letters) for i in range(n))
    return random_string

class Worker(Thread):
    def __init__(self,
                 wid,
                 tasks,
                 video_dir,
                 video_progress,
                 audio_dir,
                 audio_progress,):
        super().__init__()
        self.wid = wid
        self.daemon = True
        self._stop_event = threading.Event()

        self.tasks = tasks
        self.video_dir = video_dir
        self.video_progress=video_progress
        self.audio_dir = audio_dir
        self.audio_progress=audio_progress
    
    def log(self, message):
        print(f"[{self.__class__.__name__}-{self.wid}]: {message}")

    def progress(self,prgs_file,message):
        with open(prgs_file,'a+') as f:
            f.write(message+"\n")

    def run(self):
        self.log("Launch")
        while not self._stop_event.is_set():
            if not self.tasks.empty():
                task, i, N = self.tasks.get()
                utt = task.split('/')[-2]
                audio_file = os.path.join(self.audio_dir,f'{utt}.mp3')
                video_file = os.path.join(self.video_dir,f'{utt}.mp4')

                # S1: Download video
                try:
                    self.log(f"download video：{video_file}")
                    command = [YOUGET, "-o", self.video_dir, "-O", utt, task]
                    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    self.progress(self.video_progress,utt)
                except KeyboardInterrupt as e:
                    raise e
                except subprocess.CalledProcessError as e:
                    self.log("Fail to download, skip ..")
                    continue

                # S2: Video2Audio
                try:
                    self.log(f"video2audio：{audio_file}")
                    command = [FFMPEG, "-i", video_file, '-ac', '1', '-ar', '16000', audio_file]
                    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    self.progress(self.audio_progress,utt)
                    if os.path.exists(video_file):os.remove(video_file) # 删除视频文件
                except KeyboardInterrupt as e:
                    raise e
                except subprocess.CalledProcessError as e:
                    self.log("Fail to convert, skip ..")
                    continue

            else:
                break
            time.sleep(0.1)
        self.log("Done")
        


if __name__ == "__main__":

    # 任务参数
    task_list_file = "videos_url.txt"
    nj =  3
    tasks = Queue()

    prefix = "dataset/小学公开课"
    video_dir = mkdir(f"{prefix}/videos", reset=True)
    audio_dir = mkdir(f"{prefix}/audios", reset=True)
    video_progress = f"{prefix}/video.progress"
    audio_progress = f"{prefix}/audio.progress"
    with open(audio_progress,'w') as f:
        pass
    with open(video_progress,'w') as f:
        pass

    # 读取全部文本句子
    with open(task_list_file,'rt',encoding='utf-8') as f:
        text_list = f.readlines()

    # 生成任务列表
    for i, line in enumerate(text_list):
        tasks.put([line.strip(), i, len(text_list)])

    # 初始化多个worker
    workers = []
    for i in range(nj):
        workers.append(Worker(wid=i,
                              tasks=tasks,
                              video_dir=video_dir,
                              video_progress=video_progress,
                              audio_dir=audio_dir,
                              audio_progress=audio_progress))
    
    # 启动workers
    for worker in workers:
        worker.start()
 
    # 等待多线程结束
    for worker in workers:
        worker.join()
