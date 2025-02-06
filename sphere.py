import re
import math
import numpy as np
from miniball import get_bounding_ball
from tkinter import Tk, Label, Button, filedialog, Text, messagebox
from PIL import Image, ImageTk


def parse_coordinates(file_path):
    """
    从文件中提取点的编号和三维坐标
    """
    with open(file_path, "r", encoding="utf-8") as file:
        data = file.readlines()

    # 正则表达式匹配模式
    pattern = re.compile(r"^(\w+\d*)\s+\w+\s+([\d.]+(?:\(\d+\))?)\s+([\d.]+(?:\(\d+\))?)\s+([\d.]+(?:\(\d+\))?)")

    # 存储解析后的结果
    parsed_data = []

    for line in data:
        match = pattern.match(line)  # 仅匹配行首
        if match:
            identifier = match.group(1)  # 提取编号 (如 ASN1, H2)

            # 在cif文件的UNIT处截止，避免多次读取数据
            if identifier == 'UNIT':
                break

            # 去除括号内的不确定性值
            x = re.sub(r"\(\d+\)", "", match.group(2))
            y = re.sub(r"\(\d+\)", "", match.group(3))
            z = re.sub(r"\(\d+\)", "", match.group(4))

            try:
                parsed_data.append((identifier, float(x), float(y), float(z)))
            except ValueError:
                print(f"无法转换：{match.groups()}")

    # 打印提取结果
    """
        for entry in parsed_data:
        print(entry)
    """

    return parsed_data


def calculate_distance(point1, point2):
    """
    计算两点之间的欧几里得距离
    """
    return math.sqrt(sum((p1 - p2) ** 2 for p1, p2 in zip(point1, point2)))


def minimum_enclosing_sphere(points):
    """
    使用 miniball 库计算最小包围球
    """
    points_array = np.array(points)
    center, radius_squared = get_bounding_ball(points_array)
    radius = math.sqrt(radius_squared)
    return center.tolist(), radius


def find_max_distance(parsed_data):
    """
    计算点集中最长的两点距离
    """
    points = [coords[1:] for coords in parsed_data]
    max_distance = 0
    max_pair = None
    for i, p1 in enumerate(points):
        for j, p2 in enumerate(points[i + 1:]):
            distance = calculate_distance(p1, p2)
            """
            检查循环中的计数
            print(f"distance between{i, i+j+1, parsed_data[i],parsed_data[j+i+1]} is {distance}")
            """
            if distance > max_distance:
                max_distance = distance
                max_pair = (parsed_data[i], parsed_data[j+i+1])

    return max_distance, max_pair


def open_file():
    """
    打开文件并处理数据
    """
    file_path = filedialog.askopenfilename(title="选择坐标文件", filetypes=(("文本文件", "*.txt"), ("所有文件", "*.*")))
    if not file_path:
        return

    try:
        parsed_data = parse_coordinates(file_path)
        points = [coords[1:] for coords in parsed_data]

        # 计算最小包围球
        center, radius = minimum_enclosing_sphere(points)

        # 计算两点之间的最大距离
        max_distance, max_pair = find_max_distance(parsed_data)

        # 显示结果
        result_text.delete(1.0, "end")
        result_text.insert("end", f"文件: {file_path}\n")
        result_text.insert("end", f"最小包围球的中心: {center}\n")
        result_text.insert("end", f"最小包围球的半径: {radius:.6f}\n")
        result_text.insert("end", f"两个原子最长距离为: {max_distance:.6f}\n")
        result_text.insert("end", f"距离最远的两个原子为: {max_pair}\n")

        print(f"文件: {file_path}\n")
        print(f"最小包围球的中心: {center}\n")
        print(f"最小包围球的半径: {radius:.6f}\n")
        print(f"两个原子最长距离为: {max_distance:.6f}\n")
        print(f"距离最远的两个原子为: {max_pair}\n")

    except Exception as e:
        messagebox.showerror("错误", f"处理文件时出错: {str(e)}")


# 创建 Tkinter 主窗口
root = Tk()
root.title("分子半径计算器")

# 设置窗口图标
img = ImageTk.PhotoImage(file="Zyzx.jpg")  # 加载图片
root.iconphoto(True, img)

# 添加按钮和文本框
Label(root, text="分子半径计算器", font=("Times New Roman", 16)).pack(pady=10)
Label(root, text="Developed by Zyzx", font=("Times New Roman", 12)).pack(pady=5)
Label(root, text="这是一个分子半径计算器，可以通过单晶数据计算分子半径\n将cif文件中晶体坐标另存至一个txt文件中\n可以计算得到分子中两个最远原子的距离，以及最小包围球的半径（基于Welzl迭代算法）", font=("Times New Roman", 12)).pack(pady=5)
Button(root, text="打开文件并计算", command=open_file, width=20, height=2).pack(pady=10)

result_text = Text(root, height=15, width=60)
result_text.pack(pady=10)

Button(root, text="退出", command=root.quit, width=20, height=2).pack(pady=10)

# 运行主循环
root.mainloop()
