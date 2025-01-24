import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal.windows import tukey

import os

# 指定目标文件夹路径
folder_path = "D:/Desktop/data/"
type_of_file = "Metal2Empty/"
#os.mkdir(type_of_file)
# 遍历文件夹，获取所有 .mp4 文件名
mp4_files = [f for f in os.listdir(folder_path + type_of_file) if f.endswith(".mp4")]

for file_path in mp4_files:
    # 文件选择（硬编码文件路径）
    cap = cv2.VideoCapture(folder_path + type_of_file + file_path)

    if not cap.isOpened():
        raise Exception("无法打开视频文件！")

    # 视频属性
    Nframes = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    Nwidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    Nheight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 参数设置
    mu_min, mu_max = 30, 284
    sig_min, sig_max = 10, 470

    # Tukey 窗函数权重
    p = 0.0  # 调整边缘权重的比例
    w = tukey(Nframes, p)

    # 读取视频帧并计算加权平均
    vid_frames = []
    for i_frame in range(Nframes):
        ret, frame = cap.read()
        if not ret:
            break
        frame = frame.astype(np.float64)  # 转换为浮点类型
        frame_weighted = frame * w[i_frame]
        vid_frames.append(frame_weighted)

    vid_frames = np.stack(vid_frames, axis=-1)  # 转换为 4D 矩阵
    vid_mean = np.mean(vid_frames, axis=-1)
    vid_min = np.min(vid_frames, axis=-1)
    vid_std = np.std(vid_frames, axis=-1)

    # 分离 RGB 通道
    R_mean = vid_mean[mu_min:mu_max, sig_min:sig_max, 0]
    G_mean = vid_mean[mu_min:mu_max, sig_min:sig_max, 1]
    B_mean = vid_mean[mu_min:mu_max, sig_min:sig_max, 2]

    R_min = vid_min[mu_min:mu_max, sig_min:sig_max, 0]
    G_min = vid_min[mu_min:mu_max, sig_min:sig_max, 1]
    B_min = vid_min[mu_min:mu_max, sig_min:sig_max, 2]

    R_std = vid_std[mu_min:mu_max, sig_min:sig_max, 0]
    G_std = vid_std[mu_min:mu_max, sig_min:sig_max, 1]
    B_std = vid_std[mu_min:mu_max, sig_min:sig_max, 2]

    cap.release()

    R_G_Mean = np.abs(R_mean - G_mean)
    G_B_Mean = np.abs(G_mean - B_mean)

    R_G_Mean[(R_G_Mean < 15)] = 15
    R_G_Mean[(R_G_Mean > 30)] = 30
    G_B_Mean[(G_B_Mean < 15)] = 15
    G_B_Mean[(G_B_Mean > 30)] = 30

    # 检测框（替换为实际值）
    metal_box = [250, 20, 450-250, 284-230]
    ferrous_box = [20, 230, 450-20, 100-20]

    R_G_Mean = R_G_Mean - 15
    G_B_Mean = G_B_Mean - 15

    #R_G_Mean = R_G_Mean[20:450, 0:80]
    #G_B_Mean = G_B_Mean[metal_box[1]:metal_box[1] + metal_box[3], metal_box[0]:metal_box[0] + metal_box[2]]
    # 绘图
    # 第一组：颜色均值差异分析
    fig, axs = plt.subplots(2, 1, figsize=(10, 8))
    im1 = axs[0].imshow(R_G_Mean, extent=[sig_min, sig_max, mu_min, mu_max], aspect='auto', cmap='viridis')
    axs[0].set_title("Battery Detector: Mean(Red) - Mean(Green)")
    axs[0].set_xlabel("Signal Range")
    axs[0].set_ylabel("Mu Range")
    fig.colorbar(im1, ax=axs[0])
    axs[0].add_patch(plt.Rectangle((ferrous_box[0], ferrous_box[1]), ferrous_box[2], ferrous_box[3], edgecolor='white', fill=False))

    im2 = axs[1].imshow(G_B_Mean, extent=[sig_min, sig_max, mu_min, mu_max], aspect='auto', cmap='viridis')
    axs[1].set_title("Coin Detector: Mean(Green) - Mean(Blue)")
    axs[1].set_xlabel("Signal Range")
    axs[1].set_ylabel("Mu Range")
    fig.colorbar(im2, ax=axs[1])
    axs[1].add_patch(plt.Rectangle((metal_box[0], metal_box[1]), metal_box[2], metal_box[3], edgecolor='white', fill=False))
    plt.tight_layout()
    plt.savefig(type_of_file + file_path[:-4] + "2.png")  # 保存图像到文件
    plt.close()
