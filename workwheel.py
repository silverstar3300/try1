
# SpinWheel类实现
import math
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class Work:
    def __init__(self, subjects=None, colors=None, duration=3.5, fps=30, fig_size=(6, 6)):
        self.subjects = subjects if subjects is not None else ['sweep the floor', 'wash the dishes',
                                                                'take a shower','wash your clothes']
        self.colors = colors if colors is not None else ['#ff9999', '#99ff99', '#9999ff','#ffe066']
        self.n = len(self.subjects)
        self.sector_angle = 360.0 / self.n
        self.duration = duration
        self.fps = fps
        self.frames = int(self.duration * self.fps)
        self.fig_size = fig_size
        self.target_index = None
        self.stop_angle = None
        self.result = None

    def _ease_out_cubic(self, t):
        return 1 - (1 - t) ** 3

    def _draw_pointer(self, ax):
        # 指针坐标（以圆心为原点，指向顶部，长度适中）
        triangle = np.array([[0.0, 0.0], [-0.06, 0.7], [0.06, 0.7]])
        ax.add_patch(plt.Polygon(triangle, color='k', zorder=5))

    def _get_current_selected_index(self, current_angle):
        normalized_angle = current_angle % 360
        selected_index = int(normalized_angle / self.sector_angle) % self.n
        return selected_index

    def _animate(self, frame):
        ax = self.ax
        ax.clear()
        ax.set_aspect('equal')
        ax.axis('off')

        t = frame / float(self.frames - 1) if self.frames > 1 else 1.0
        eased_t = self._ease_out_cubic(t)
        current_rotation = eased_t * self.stop_angle
        pie_startangle = 90 - current_rotation

        wedges, texts = ax.pie(
            [1]*self.n,
            colors=self.colors,
            startangle=pie_startangle,
            counterclock=False,
            wedgeprops=dict(edgecolor='k', linewidth=1)
        )

        # 标签绘制，指针始终指向顶部
        for i, p in enumerate(wedges):
            sector_center = (i + 0.5) * self.sector_angle
            label_angle = 90 - current_rotation + sector_center
            x = 0.6 * math.cos(math.radians(label_angle))
            y = 0.6 * math.sin(math.radians(label_angle))
            if frame == self.frames - 1 and i == self._get_current_selected_index(current_rotation):
                ax.text(
                    x, y, self.subjects[i],
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontsize=18, fontweight='bold', color='red',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='red')
                )
            else:
                ax.text(
                    x, y, self.subjects[i],
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontsize=14, fontweight='bold'
                )

        self._draw_pointer(ax)

        if frame == self.frames - 1:
            selected_idx = self._get_current_selected_index(current_rotation)
            self.result = self.subjects[selected_idx]
            result_text = f"选择：{self.result}"
            ax.text(
                0, -0.05, result_text,
                fontsize=20, ha='center', va='center',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
            )

    def spin(self, show=True, random_seed=None):
        if random_seed is not None:
            random.seed(random_seed)
            np.random.seed(random_seed)
        self.target_index = random.randrange(self.n)
        target_sector_start = self.target_index * self.sector_angle
        target_sector_end = (self.target_index + 1) * self.sector_angle
        target_sector_center = (target_sector_start + target_sector_end) / 2
        full_spins = random.randint(3, 6)
        max_offset = self.sector_angle / 4.0
        rand_offset = random.uniform(-max_offset, max_offset)
        self.stop_angle = full_spins * 360 + (target_sector_center + rand_offset)
        print(f"目标项: {self.subjects[self.target_index]}, 目标索引: {self.target_index}")
        print(f"总旋转角度 (deg): {self.stop_angle:.2f}")

        self.fig, self.ax = plt.subplots(figsize=self.fig_size)
        plt.subplots_adjust(top=0.95, bottom=0.05)
        self.result = None
        ani = animation.FuncAnimation(
            self.fig, self._animate,
            frames=self.frames,
            interval=1000/self.fps,
            repeat=False
        )
        if show:
            plt.show()
        return self.result

# 示例用法（可删除）
if __name__ == "__main__":
    wheel = Work()
    result = wheel.spin()
    print("最终选择:", result)