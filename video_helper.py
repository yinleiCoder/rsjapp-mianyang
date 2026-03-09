import os
import subprocess

def obtain_video_duration_by_ffprobe(url):
    ffprobe_path = os.path.join('ffmpeg', "bin", "ffprobe.exe")    
    cmd = [
        ffprobe_path,
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        url
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    duration = float(result.stdout.strip())

    print("视频时长:", duration, "秒")
    return duration

obtain_video_duration_by_ffprobe("https://rsjapp.mianyang.cn/jxjy/psp/resource/ZJSITE/CYYQPC/video/videoFile/2021CY001.mp4")

# import requests
# import struct

# def get_mp4_duration(url, chunk_size=1024*1024*5):
#     """
#     获取在线 MP4 视频时长（秒）
#     只下载前几 MB 数据解析 moov box
#     """
#     headers = {"Range": f"bytes=0-{chunk_size}"}
#     r = requests.get(url, headers=headers, timeout=10)
#     data = r.content

#     i = 0
#     while i < len(data):
#         size = struct.unpack(">I", data[i:i+4])[0]
#         box_type = data[i+4:i+8]

#         if box_type == b"moov":
#             moov_data = data[i:i+size]
#             return parse_mvhd(moov_data)

#         i += size
#     raise Exception("未找到 moov box，可能 moov 在文件末尾")


# def parse_mvhd(moov_data):
#     """
#     从 moov 中解析 mvhd
#     """
#     i = 0
#     while i < len(moov_data):
#         size = struct.unpack(">I", moov_data[i:i+4])[0]
#         box_type = moov_data[i+4:i+8]
#         if box_type == b"mvhd":
#             version = moov_data[i+8]
#             if version == 1:
#                 timescale = struct.unpack(">I", moov_data[i+28:i+32])[0]
#                 duration = struct.unpack(">Q", moov_data[i+32:i+40])[0]
#             else:
#                 timescale = struct.unpack(">I", moov_data[i+20:i+24])[0]
#                 duration = struct.unpack(">I", moov_data[i+24:i+28])[0]
#             return duration / timescale
#         i += size

#     raise Exception("未找到 mvhd box")


# # 测试
# duration = get_mp4_duration(url)

# print("视频时长:", duration, "秒")

