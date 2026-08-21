# -*- coding: utf-8 -*-
"""图 10：有界制造误差下两方案三项性能指标的蒙特卡洛分布（100000 次抽样）。"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from sklearn.linear_model import Ridge

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "附件2_数据.xlsx")
FIGDIR = os.path.join(ROOT, "figs")
os.makedirs(FIGDIR, exist_ok=True)

for f in ["Microsoft YaHei", "SimHei", "SimSun"]:
    if any(f.lower() == x.name.lower() for x in font_manager.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [f, "DejaVu Sans"]
        break
plt.rcParams["axes.unicode_minus"] = False

df = pd.read_excel(DATA, header=1)
df.columns = ["no", "beta", "lam", "N", "R", "dP", "UT"]
fin = df[df.beta > 0].reset_index(drop=True)
X = fin[["beta", "lam", "N"]].values.astype(float)
Y = fin[["R", "dP", "UT"]].values.astype(float)
MU = np.array([0.1875, 3.75, 6.0])
SD = np.array([0.073951, 0.559017, 2.828427])

def design(Zm, deg=3):
    cols = [np.ones(len(Zm))]
    for d in range(1, deg + 1):
        for i in range(d + 1):
            for j in range(d - i + 1):
                l = d - i - j
                cols.append((Zm[:, 0] ** i) * (Zm[:, 1] ** j) * (Zm[:, 2] ** l))
    return np.column_stack(cols)

Ph = design((X - MU) / SD)
models = [Ridge(alpha=1e-10).fit(Ph, Y[:, k]) for k in range(3)]

def predict(b, l, n, batch=None):
    if batch is None:
        pts = np.array([[b, l, n]])
    else:
        pts = np.column_stack([b, l, np.full(len(b), n)])
    return np.column_stack([m.predict(design((pts - MU) / SD)) for m in models])

schemes = [
    ("等权综合 (0.220, 4.50, 4)", 0.220, 4.50, 4),
    ("偏好鲁棒 (0.226, 4.50, 6)", 0.226, 4.50, 6),
]
mnames = ["无量纲热阻 $R^{*}$", "无量纲压降 $\\Delta p^{*}$", "无量纲温度非均匀性 $U_T^{*}$"]
colors = ["#C0392B", "#2471A3", "#1E8449"]

rng = np.random.default_rng(31)
N_MC = 100000

fig, axes = plt.subplots(2, 3, figsize=(12.0, 6.6))
for r, (tag, b0, l0, n0) in enumerate(schemes):
    bs = np.clip(rng.uniform(b0 - 0.01, b0 + 0.01, N_MC), 0.10, 0.30)
    ls = np.clip(rng.uniform(l0 - 0.05, l0 + 0.05, N_MC), 3.0, 4.5)
    P = predict(bs, ls, n0, batch=bs)
    nom = predict(b0, l0, n0)[0]
    for k in range(3):
        ax = axes[r, k]
        v = P[:, k]
        mean, std = v.mean(), v.std()
        p05, p95 = np.percentile(v, [5, 95])
        lo, hi = np.min(v), np.max(v)
        pad = (hi - lo) * 0.08
        bins = np.linspace(lo - pad, hi + pad, 61)
        ax.hist(v, bins=bins, color=colors[k], alpha=0.55, edgecolor="white", lw=0.3)
        ax.axvline(nom[k], color="k", ls="-.", lw=1.4, label="标称值")
        ax.axvline(mean, color="#B03A2E", ls="--", lw=1.4, label="均值")
        ax.axvline(p05, color="0.45", ls=":", lw=1.2)
        ax.axvline(p95, color="0.45", ls=":", lw=1.2)
        ax.text(0.975, 0.965,
                f"均值 {mean:.6f}\n标准差 {std:.6f}\n变异系数 {std/mean*100:.4f}%\nP05–P95 [{p05:.6f}, {p95:.6f}]",
                transform=ax.transAxes, ha="right", va="top", fontsize=8,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="0.7", alpha=0.9))
        ax.set_title(mnames[k], fontsize=10)
        ax.tick_params(labelsize=8)
        ax.grid(alpha=0.25)
        if r == 1:
            ax.set_xlabel("指标值", fontsize=8.5)
        if k == 0:
            ax.set_ylabel("频数", fontsize=8.5)
    axes[r, 0].annotate(tag, xy=(0.015, 0.97), xycoords="axes fraction",
                        fontsize=9.5, ha="left", va="top",
                        bbox=dict(boxstyle="round,pad=0.35", fc="#FDF2E9", ec="#B9770E", alpha=0.95))

handles, labels = axes[0, 0].get_legend_handles_labels()
fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=9, frameon=True, bbox_to_anchor=(0.5, -0.02))
fig.suptitle("有界制造误差下的性能指标蒙特卡洛分布（$\\beta \\pm 0.01$、$\\lambda \\pm 0.05$，100000 次抽样）",
             fontsize=12)
fig.tight_layout(rect=[0, 0.04, 1, 0.97])
out = os.path.join(FIGDIR, "fig10_mc_hist.png")
fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
plt.close(fig)
print("saved:", out)
