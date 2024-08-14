from threading import Thread
from queue import Queue
import time 
import random
import string
import warnings
import subprocess
warnings.filterwarnings("ignore") 


def generate_random_string(n):
    letters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(letters) for i in range(n))
    return random_string

class Worker(Thread):
    def __init__(self,
                 wid,
                 tasks,
                 tmpdir,
                 outdir):
        super().__init__()
        self.wid = wid
        self.daemon = True
        self.tasks = tasks
        self.tmpdir = tmpdir
        self.outdir = outdir
        

    def run(self):
        print(f"worker-{self.wid}: Launch")
        while True:
            if not self.tasks.empty():
                task, i, N = self.tasks.get()
                utt = task.split('/')[-2]

                command = ["you-get", "-o", self.tmpdir, "-O", utt, task]
                subprocess.run(command, check=True)
                
                
            else:
                break
            time.sleep(0.1)
        print(f"worker-{self.wid}: Done")
        


if __name__ == "__main__":

    text_list_file = "/opt/wangwei/TTS/data2.txt"
    model_id = 'damo/speech_sambert-hifigan_tts_zh-cn_16k'
    nj =  20
    tasks = Queue()
    outdir = "/dev/dataset_tts/"

    # 读取全部文本句子
    with open(text_list_file,'rt',encoding='utf-8') as f:
        text_list = f.readlines()

    # 生成任务列表
    for i, line in enumerate(text_list):
        tasks.put([line.strip(), i, len(text_list)])

    # 初始化多个worker
    workers = []
    for i in range(nj):
        workers.append(Worker(wid=i,
                              model_id=model_id,
                              tasks=tasks,
                              outdir=outdir))
    
    # 启动workers
    for worker in workers:
        worker.start()
 
    # 等待多线程结束
    for worker in workers:
        worker.join()
