# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import re
import numpy as np
import pandas as pd
import seaborn as sns
import sys

def parse_log(file_path):
    #coremark.exe    2628 11503.640780:     250000 task-clock:uH:      59c2c3e2c6ef matrix_mul_matrix+0x5f (/home/nrush/coremark/coremark.exe)
    pattern = r"(\S+)\s+(\d+)\s+(\d+\.\d+)\:\s+(\d+)\s+\S+clock\:\S+\s+([0-9a-fA-f]+)\s+(\S+)\+0x([0-9a-fA-f]+)\s+\((\S+)\)"
    info = {"comm":[], "pid":[], "time":[], "cnt":[], "address":[], "func":[], "offset":[], "file_name":[]}
    with open(file_path, 'r') as file:
        for line in file:
            match = re.search(pattern, line)
            if match:
                info["comm"].append(match.group(1))
                info["pid"].append(int(match.group(2)))
                info["time"].append(float(match.group(3)))
                info["cnt"].append(int(match.group(4)))
                info["address"].append(int(match.group(5), 16))
                info["func"].append(match.group(6))
                info["offset"].append(int(match.group(7), 16))
                info["file_name"].append(match.group(8))
    df = pd.DataFrame(info)
    return df

def plot_heatmap(df, so_path, n, cols = 64):
    new_df = df[df['file_name'] == so_path]
    bins = range(min(new_df['address']), max(new_df['address']) + n, n)
    new_df['bins'] = pd.cut(new_df['address'], bins=bins)
    distribution = new_df['bins'].value_counts().sort_index()

    counts_2d = distribution.to_numpy()
    current_size = len(counts_2d)
    new_size = ((current_size + cols - 1) // cols) * cols
    pad_size = new_size - current_size
    counts_2d = np.pad(counts_2d, (0, pad_size), mode='constant', constant_values=0)
    counts_2d = counts_2d.reshape((new_size // cols, cols))

    # 绘制热力图
    plt.figure(figsize=(10, 10))
    # sns.heatmap(counts_2d, annot=False, fmt="", cmap="YlGnBu", cbar=True, aspect='equal')
    img = plt.imshow(counts_2d, cmap='YlGnBu', aspect='equal')
    plt.colorbar(img)
    plt.title('{}-heatmap {}B/cell'.format(so_path, n))
    plt.savefig('{}-heatmap.png'.format(so_path.replace('/', '-')), dpi=300)  # 保存图片

    plt.figure(figsize=(10, 10))
    plt.title('{}-bar {}B/cell'.format(so_path, n))
    plt.bar(range(len(distribution.values)), distribution.values)
    plt.xlabel('')
    plt.xticks([])
    plt.savefig('{}-bar.png'.format(so_path.replace('/', '-')), dpi=300)  # 保存图片
    
if __name__ == "__main__":
    log_file_path = sys.argv[1] # 替换为你的日志文件路径
    n_bytes_per_cell = int(sys.argv[2])
    n_cols = int(sys.argv[3])
    so_path = sys.argv[4]
    df = parse_log(log_file_path)
    plot_heatmap(df, so_path, n_bytes_per_cell, n_cols)