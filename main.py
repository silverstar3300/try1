#这是一个能在你不知道干什么的时候帮你做决定的转盘程序

import tkinter as tk
from tkinter import ttk, messagebox
import math
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Wedge, Polygon
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# 配置主题选项
todo = ['work', 'study', 'rest', 'other']  # 可修改选项
colors = ['#ff9999', '#99ff99', '#9999ff', '#ffe066']
n = len(todo)
sector_angle = 360.0 / n

# 全局变量：存储最终选中的结果
final_selected_idx = -1
anim_window = None  # 动画窗口引用

# Tk 主窗口
root = tk.Tk()
root.title('接下来应该干什么')
root.geometry('900x700') 
root.resizable(False, False)


# 自定义ttk样式（按钮/标签美化）
style = ttk.Style(root)
# 设置主题（优先使用系统美观主题）
try:
    style.theme_use('clam')  # clam主题更易自定义
except:
    style.theme_use('default')

# 自定义按钮样式
style.configure('Custom.TButton', 
                font=('微软雅黑', 10, 'bold'),
                padding=8,
                relief='flat',
                background='#f0f8ff')
style.map('Custom.TButton',
          background=[('active', '#e6f7ff')], 
          foreground=[('active', '#0066cc')]) 

# 自定义标题标签样式
style.configure('Title.TLabel',
                font=('微软雅黑', 20, 'bold'),
                foreground='#2f4f4f')

# 自定义结果标签样式
style.configure('Result.TLabel',
                font=('微软雅黑', 16, 'bold'),
                foreground='#d9534f')

# 自定义提示标签样式
style.configure('Tip.TLabel',
                font=('微软雅黑', 12),
                foreground='#4682b4')

bg_canvas = tk.Canvas(root, width=900, height=700, highlightthickness=0)
bg_canvas.place(x=0, y=0)
# 绘制浅蓝色渐变背景
bg_canvas.create_rectangle(0, 0, 900, 700, 
                          fill='#f0f8ff', outline='')
bg_canvas.create_rectangle(0, 0, 900, 100, 
                          fill='#e6f7ff', outline='')

top_frame = ttk.Frame(root, style='Transparent.TFrame')
top_frame.pack(pady=5)
label_title = ttk.Label(top_frame, text="当你不知道该干什么时你可以干什么", 
                       style='Title.TLabel')
label_title.pack()

result_label = ttk.Label(root, text="", style='Result.TLabel')
result_label.pack(pady=10)

# Matplotlib 静态转盘（主窗口）- 优化尺寸和间距
fig_static = plt.Figure(figsize=(3, 3), dpi=100)  # 调整转盘尺寸更协调
ax_static = fig_static.add_subplot(111, aspect='equal')
canvas_static = FigureCanvasTkAgg(fig_static, master=root)
canvas_widget_static = canvas_static.get_tk_widget()
# 给转盘添加圆角边框
canvas_widget_static.config(bg='#ffffff', relief='raised', bd=2)
canvas_widget_static.pack(expand=True, fill='both', padx=50, pady=10)

# 底部控制区 - 优化间距和背景
control_frame = ttk.Frame(root, style='Transparent.TFrame')
control_frame.pack(pady=20)

# 转动主转盘按钮（使用自定义样式）
spin_btn = ttk.Button(control_frame, text="点击转动主转盘", 
                     style='Custom.TButton', width=15)
spin_btn.grid(row=0, column=0, padx=10, pady=10)

# 动画参数
duration = 3.5  # 秒
fps = 30
frames = int(duration * fps)
animating = False  # 防止重复点击

def draw_static_wheel(highlight_idx=None):
    """绘制主窗口的静态转盘（旋转结束后更新高亮）"""
    ax_static.clear()
    ax_static.set_xlim(-1.25, 1.25)
    ax_static.set_ylim(-1.25, 1.25)
    ax_static.axis('off')

    radius = 1.0
    # 绘制扇区
    for i in range(n):
        theta1 = 90.0 - (i + 1) * sector_angle
        theta2 = 90.0 - i * sector_angle
        
        # 高亮选中的扇区
        highlight_scale = 1.08 if (highlight_idx is not None and i == highlight_idx) else 1.0
        r = radius * highlight_scale
        wedge = Wedge(center=(0, 0), r=r, theta1=theta1, theta2=theta2,
                      facecolor=colors[i], edgecolor='white', linewidth=2.0, zorder=2)  # 白色边框更美观
        ax_static.add_patch(wedge)

        # 光晕效果（仅高亮扇区）
        if highlight_idx is not None and i == highlight_idx:
            for j, factor in enumerate([1.08, 1.12, 1.17]):
                ga = 0.08 * (0.6 ** j)
                glow = Wedge(center=(0, 0), r=r * factor, theta1=theta1, theta2=theta2,
                             facecolor='yellow', edgecolor=None, linewidth=0, alpha=ga, zorder=1)
                ax_static.add_patch(glow)

        # 标签（优化字体）
        mid_ang = (theta1 + theta2) / 2.0
        x = 0.62 * math.cos(math.radians(mid_ang))
        y = 0.62 * math.sin(math.radians(mid_ang))
        if highlight_idx is not None and i == highlight_idx:
            ax_static.text(x, y, todo[i], ha='center', va='center', 
                          fontsize=20, fontweight='bold', fontfamily='微软雅黑',
                          color='red', bbox=dict(boxstyle='round,pad=0.3', 
                                               facecolor='white', alpha=0.95, edgecolor='red'), zorder=4)
        else:
            ax_static.text(x, y, todo[i], ha='center', va='center', 
                          fontsize=16, fontweight='bold', fontfamily='微软雅黑', zorder=4)

    # 指针（优化样式）
    tri = Polygon([[0.0, 1.05], [-0.045, 0.92], [0.045, 0.92]], 
                 closed=True, color='#d9534f', linewidth=1, zorder=5)
    ax_static.add_patch(tri)

    canvas_static.draw_idle()

def compute_selected_index(current_rotation):
    """计算指针指向的扇区索引"""
    norm_rot = current_rotation % 360.0
    angle_from_top = norm_rot % 360.0
    idx = int(angle_from_top // sector_angle) % n
    return idx

def ease_out_cubic(t):
    """缓动函数：先快后慢"""
    return 1 - (1 - t) ** 3

def create_animation_window():
    """创建独立的Matplotlib动画窗口"""
    global anim_window, final_selected_idx
    final_selected_idx = -1

    # 创建新的Matplotlib窗口（美化）
    anim_fig = plt.figure(figsize=(6, 6), dpi=100, facecolor='#f0f8ff')
    anim_ax = anim_fig.add_subplot(111, aspect='equal')
    anim_ax.set_xlim(-1.25, 1.25)
    anim_ax.set_ylim(-1.25, 1.25)
    anim_ax.axis('off')

    # 随机目标扇区
    target_index = random.randrange(n)
    full_spins = random.randint(3, 6)
    max_offset = sector_angle / 4.0
    rand_offset = random.uniform(-max_offset, max_offset)
    target_sector_center = target_index * sector_angle + sector_angle / 2
    target_rotation = full_spins * 360.0 + (target_sector_center + rand_offset)

    def animate(frame):
        """动画帧更新函数"""
        anim_ax.clear()
        anim_ax.set_xlim(-1.25, 1.25)
        anim_ax.set_ylim(-1.25, 1.25)
        anim_ax.axis('off')

        # 计算当前进度和旋转角度
        t = frame / (frames - 1) if frames > 1 else 1.0
        eased_t = ease_out_cubic(t)
        current_rot = eased_t * target_rotation

        # 绘制转盘
        radius = 1.0
        for i in range(n):
            theta1 = 90.0 - (i + 1) * sector_angle
            theta2 = 90.0 - i * sector_angle
            t1 = theta1 - current_rot
            t2 = theta2 - current_rot

            wedge = Wedge(center=(0, 0), r=radius, theta1=t1, theta2=t2,
                          facecolor=colors[i], edgecolor='white', linewidth=2.0, zorder=2)
            anim_ax.add_patch(wedge)

            # 标签（优化字体）
            mid_ang = (t1 + t2) / 2.0
            x = 0.62 * math.cos(math.radians(mid_ang))
            y = 0.62 * math.sin(math.radians(mid_ang))
            anim_ax.text(x, y, todo[i], ha='center', va='center', 
                        fontsize=16, fontweight='bold', fontfamily='微软雅黑', zorder=4)

        # 绘制指针（优化样式）
        tri = Polygon([[0.0, 1.05], [-0.045, 0.92], [0.045, 0.92]], 
                     closed=True, color='#d9534f', zorder=5)
        anim_ax.add_patch(tri)

        # 最后一帧记录选中的索引
        if frame == frames - 1:
            nonlocal target_index
            final_selected_idx = compute_selected_index(current_rot)

        return [anim_ax]

    # 创建动画
    ani = animation.FuncAnimation(
        anim_fig, animate, frames=frames, interval=int(1000/fps),
        repeat=False, blit=True
    )

    # 显示动画窗口（优化布局）
    plt.tight_layout(pad=2)
    plt.show(block=True)  # 阻塞直到窗口关闭

    # 动画结束后更新主窗口
    if final_selected_idx >= 0:
        draw_static_wheel(highlight_idx=final_selected_idx)
        result_label.config(text=f"最终结果：{todo[final_selected_idx]}")
    else:
        result_label.config(text="")

def spin_wheel():
    """点击按钮触发旋转"""
    global animating
    if animating:
        messagebox.showinfo("提示", "转盘正在旋转中，请稍候！", 
                           icon='info', font=('微软雅黑', 12))
        return
    
    animating = True
    try:
        # 清空之前的结果
        result_label.config(text="")
        # 启动独立动画窗口
        create_animation_window()
    finally:
        animating = False

#4个按钮
#work 按钮的函数
from workwheel import Work
def work_action():
    wheel2 = Work()   
    wheel2.spin()

work_btn = ttk.Button(control_frame, text="工作", width=10, 
                     style='Custom.TButton', command=work_action)
work_btn.grid(row=0, column=1, padx=8, pady=10)

#study 按钮的函数
from studysubjectwheel import Xuexi
def study_action():
    wheel1 = Xuexi()
    wheel1.spin()

study_btn = ttk.Button(control_frame, text="学习", width=10, 
                      style='Custom.TButton', command=study_action)
study_btn.grid(row=0, column=2, padx=8, pady=10)

#rest 按钮的函数
from restwheel import Rest
def rest_action():
    wheel3 = Rest()
    wheel3.spin()

rest_btn = ttk.Button(control_frame, text="休息", width=10,
                     style='Custom.TButton', command=rest_action)
rest_btn.grid(row=0, column=3, padx=8, pady=10)

#other 按钮的函数
from againwheel import Again
def again_action():
    wheel4 = Again()
    wheel4.spin()

def other_action():
    # 美化弹窗样式
    w1indow = tk.Toplevel(root)
    w1indow.title("其他选项")
    w1indow.geometry('350x250')
    w1indow.resizable(False, False)
    w1indow.configure(bg='#f0f8ff')
    
    # 弹窗标题
    title_label = ttk.Label(w1indow, text="其他选项", style='Title.TLabel')
    title_label.pack(pady=15)
    
    # 提示文字
    label = ttk.Label(w1indow, text="转盘都没转出来，要不再试一次", 
                     style='Tip.TLabel')
    label.pack(pady=5)
    
    # 按钮框架
    btn_frame = ttk.Frame(w1indow)
    btn_frame.pack(pady=20)
    
    ok_button = ttk.Button(btn_frame, text="确定", width=10,
                          style='Custom.TButton', command=w1indow.destroy)
    ok_button.grid(row=0, column=0, padx=10)
    
    def cancel_action():
        w2indow=tk.Toplevel(w1indow)
        w2indow.title("没招了")
        w2indow.geometry('300x180')
        w2indow.resizable(False, False)
        w2indow.configure(bg='#f0f8ff')
        
        label = ttk.Label(w2indow, text="再转一次", style='Tip.TLabel')
        label.pack(pady=20)
        
        ok_button1 = ttk.Button(w2indow, text="确定", width=10,
                               style='Custom.TButton', command=again_action)
        ok_button1.pack(pady=10)
    
    cancel_button = ttk.Button(btn_frame, text="取消", width=10,
                              style='Custom.TButton', command=cancel_action)
    cancel_button.grid(row=0, column=1, padx=10)

other_btn = ttk.Button(control_frame, text="其他", width=10,
                      style='Custom.TButton', command=other_action)
other_btn.grid(row=0, column=4, padx=8, pady=10)

# 提示标签（美化后）
tip_label = ttk.Label(root, text="当你完成主转盘的转动时，请点击相应的按钮", 
                     style='Tip.TLabel')
tip_label.pack(pady=10)

# 初始绘制静态转盘
draw_static_wheel()

# 绑定按钮事件
spin_btn.config(command=spin_wheel)

# 主循环
root.mainloop()