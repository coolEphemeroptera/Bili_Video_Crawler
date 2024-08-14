import subprocess








def download_video(video_url):
    """使用 you-get 下载单个视频"""
    command = ["you-get", "-o", "下载目录", video_url]
    subprocess.run(command, check=True)

def main():
    # 示例视频URL列表
    video_urls = [
        "https://www.bilibili.com/video/BV1v4411B7G5",
        "https://www.bilibili.com/video/BV12J411m7n9"
    ]
    
    for url in video_urls:
        try:
            download_video(url)
            print(f"下载成功: {url}")
        except subprocess.CalledProcessError:
            print(f"下载失败: {url}")

if __name__ == "__main__":
    main()
