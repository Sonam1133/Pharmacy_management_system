"""A minimal bar-chart widget drawn directly on a Tkinter Canvas."""
import tkinter as tk


class BarChart(tk.Canvas):
    def __init__(self, parent, data, title="", width=720, height=380, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg="white", highlightthickness=1,
                         highlightbackground="#cccccc", **kwargs)
        self.data = data          # list of (label, value)
        self.title = title
        self._draw()

    def _draw(self):
        self.delete("all")
        pad_l, pad_r, pad_t, pad_b = 70, 30, 50, 90
        chart_w = int(self.winfo_reqwidth())  - pad_l - pad_r
        chart_h = int(self.winfo_reqheight()) - pad_t - pad_b

        self.create_text(int(self.winfo_reqwidth()) / 2, 25,
                         text=self.title, font=("Helvetica", 14, "bold"))

        if not self.data:
            self.create_text(int(self.winfo_reqwidth()) / 2,
                             int(self.winfo_reqheight()) / 2,
                             text="No data available", fill="gray",
                             font=("Helvetica", 12))
            return

        max_val = max(v for _, v in self.data) or 1
        n = len(self.data)
        slot = chart_w / n
        bar_w = slot * 0.55

        # axes
        self.create_line(pad_l, pad_t, pad_l, pad_t + chart_h, fill="black", width=2)
        self.create_line(pad_l, pad_t + chart_h,
                         pad_l + chart_w, pad_t + chart_h, fill="black", width=2)

        # y ticks
        for i in range(6):
            y = pad_t + chart_h - (chart_h * i / 5)
            self.create_line(pad_l - 5, y, pad_l, y, fill="black")
            self.create_text(pad_l - 10, y, anchor="e",
                             text=f"{int(max_val * i / 5)}",
                             font=("Helvetica", 9))

        # bars
        for i, (label, value) in enumerate(self.data):
            x0 = pad_l + i * slot + (slot - bar_w) / 2
            x1 = x0 + bar_w
            bar_h = (value / max_val) * chart_h
            y0 = pad_t + chart_h - bar_h
            y1 = pad_t + chart_h

            self.create_rectangle(x0, y0, x1, y1, fill="#3b82f6", outline="")
            self.create_text((x0 + x1) / 2, y0 - 10,
                             text=f"{value:g}", font=("Helvetica", 9))

            # rotated-ish label handling: truncate long names
            short = label if len(label) <= 14 else label[:12] + "…"
            self.create_text((x0 + x1) / 2, y1 + 15,
                             text=short, anchor="n",
                             font=("Helvetica", 9))
