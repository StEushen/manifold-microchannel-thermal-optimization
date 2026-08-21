# -*- coding: utf-8 -*-
"""Generate all missing figures for the revised paper."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, Rectangle, FancyArrow, FancyArrowPatch
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "附件2_数据.xlsx")
FIGDIR = os.path.join(ROOT, "figs")
os.makedirs(FIGDIR, exist_ok=True)

# ---- Chinese fonts ---------------------------------------------------------
for f in ["Microsoft YaHei", "SimHei", "SimSun", "KaiTi"]:
    if any(f.lower() == x.name.lower() for x in font_manager.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [f, "DejaVu Sans"]
        break
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 10

df = pd.read_excel(DATA, header=1)
df.columns = ["no", "beta", "lam", "N", "R", "dP", "UT"]
fin = df[df.beta > 0].reset_index(drop=True)
X = fin[["beta", "lam", "N"]].values.astype(float)
Y = fin[["R", "dP", "UT"]].values.astype(float)
ynames = ["R*", "dP*", "UT*"]
ylabels = ["无量纲热阻 R*", "无量纲压降 Δp*", "无量纲温度非均匀性 U*T"]
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

Z = (X - MU) / SD
Phi3 = design(Z)
models = [Ridge(alpha=1e-10).fit(Phi3, Y[:, k]) for k in range(3)]

def pred_xyz(b, l, n):
    zm = (np.array([[b, l, n]]) - MU) / SD
    return np.array([m.predict(design(zm))[0] for m in models])

def pred_grid(B, L, Ns):
    pts = []
    for b in B:
        for l in L:
            for n in Ns:
                pts.append((b, l, n))
    G = np.array(pts)
    P = np.column_stack([m.predict(design((G - MU) / SD)) for m in models])
    return G, P

COLORS = ["#C0392B", "#2471A3", "#1E8449"]

# ===========================================================================
# 图 2  系统结构与热流/水流路径示意图
# ===========================================================================
def draw_fig2():
    fig = plt.figure(figsize=(11.5, 5.2))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.05, 1.0], wspace=0.16)

    # ---------- (a) plan view of microchannel layer ----------
    ax = fig.add_subplot(gs[0, 0])
    ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.add_patch(Rectangle((0, 0), 10, 10, fill=False, ec="k", lw=1.6))
    nch = 9
    for i in range(nch):
        x0 = 0.5 + i * 1.0
        if i % 2 == 0:
            ax.add_patch(Rectangle((x0, 0.35), 0.55, 9.3, fc="#AED6F1", ec="none"))
        else:
            ax.add_patch(Rectangle((x0, 0.35), 0.55, 9.3, fc="#D6EAF8", ec="none"))
    # pin-fin rows (6 rows x 3-4 fins each), staggered
    for r, yc in enumerate([1.2, 2.6, 4.0, 5.4, 6.8, 8.2]):
        off = 0 if r % 2 == 0 else 0.5
        xs = np.arange(1.4 + off, 9.3, 1.6)
        for xc in xs:
            ax.add_patch(Circle((xc, yc), 0.30, fc="#E67E22", ec="#A04000", lw=0.8, zorder=3))
    # manifold-unit boundaries (dashed)
    for xb in [2.5, 5.0, 7.5]:
        ax.plot([xb, xb], [0.2, 9.8], "--", color="#7F8C8D", lw=0.9, zorder=2)
    # inlets (3) from top
    for xc in [1.8, 5.0, 8.2]:
        ax.annotate("", xy=(xc, 0.55), xytext=(xc, 1.55),
                    arrowprops=dict(arrowstyle="-|>", color="#2471A3", lw=2.2))
    # side outlets
    ax.annotate("", xy=(0.45, 5.0), xytext=(1.45, 5.0),
                arrowprops=dict(arrowstyle="-|>", color="#1E8449", lw=2.2))
    ax.annotate("", xy=(9.55, 5.0), xytext=(8.55, 5.0),
                arrowprops=dict(arrowstyle="-|>", color="#1E8449", lw=2.2))
    ax.text(5.0, 0.15, "入口（3 个，流向 ↓）", ha="center", va="top", fontsize=8.5, color="#2471A3")
    ax.text(-0.12, 5.0, "出口（2 个）", ha="right", va="center", fontsize=8.5, color="#1E8449")
    ax.text(10.12, 5.0, "出口（2 个）", ha="left", va="center", fontsize=8.5, color="#1E8449")
    ax.text(5.0, 9.62, "散热区域 10 mm × 10 mm", ha="center", va="bottom", fontsize=8.5)
    ax.text(2.55, 7.2, "针肋（沿流向分排）", ha="left", fontsize=8.5, color="#A04000")
    ax.text(8.0, 2.6, "微通道", ha="center", fontsize=8.5, color="#1A5276")
    ax.text(5.0, 4.85, "歧管单元边界", ha="center", va="top", fontsize=7.5, color="#7F8C8D", rotation=90)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title("(a) 微通道层与针肋阵列平面示意", fontsize=10)

    # ---------- (b) cross-section ----------
    ax = fig.add_subplot(gs[0, 1])
    ax.set_xlim(0, 10); ax.set_ylim(-4.5, 5.0)
    ax.set_aspect("equal")
    # chip (top center)
    ax.add_patch(Rectangle((3.4, 3.35), 3.2, 1.15, fc="#E74C3C", ec="#922B21", lw=1.2))
    ax.text(5.0, 3.92, "芯片热源", ha="center", va="center", fontsize=8.5, color="white")
    # heat arrows
    for xc in [4.1, 5.0, 5.9]:
        ax.annotate("", xy=(xc, 2.95), xytext=(xc, 3.3),
                    arrowprops=dict(arrowstyle="-|>", color="#C0392B", lw=1.8))
    ax.text(5.0, 3.02, "热流", ha="center", fontsize=7.5, color="#C0392B")
    # AlN substrate
    ax.add_patch(Rectangle((2.7, 2.35), 4.6, 0.62, fc="#F5CBA7", ec="#A04000", lw=1.0))
    ax.text(2.62, 2.66, "氮化铝衬底", ha="right", va="center", fontsize=8)
    # manifold layer with 3 inlet passages
    ax.add_patch(Rectangle((0.8, 1.35), 8.4, 0.9, fc="#AED6F1", ec="#2471A3", lw=1.1))
    for xc in [1.8, 5.0, 8.2]:
        ax.add_patch(Rectangle((xc - 0.28, 1.55), 0.56, 2.15, fc="#85C1E9", ec="#2471A3", lw=0.8))
        ax.annotate("", xy=(xc, 2.62), xytext=(xc, 4.6),
                    arrowprops=dict(arrowstyle="-|>", color="#2471A3", lw=2.0))
    ax.text(1.8, 4.72, "入口1", ha="center", fontsize=7.5, color="#2471A3")
    ax.text(5.0, 4.72, "入口2", ha="center", fontsize=7.5, color="#2471A3")
    ax.text(8.2, 4.72, "入口3", ha="center", fontsize=7.5, color="#2471A3")
    ax.text(0.95, 1.8, "歧管分配层", ha="left", va="center", fontsize=8, color="#154360")
    # microchannel layer
    ax.add_patch(Rectangle((0.8, -1.7), 8.4, 3.0, fc="#D6EAF8", ec="#1A5276", lw=1.1))
    for r, yc in enumerate(np.linspace(-1.35, 1.05, 6)):
        off = 0 if r % 2 == 0 else 0.45
        for xc in np.arange(1.5 + off, 8.6, 1.35):
            ax.add_patch(Circle((xc, yc), 0.26, fc="#E67E22", ec="#A04000", lw=0.7, zorder=3))
    ax.text(0.95, 0.15, "微通道换热层", ha="left", va="center", fontsize=8, color="#154360")
    ax.text(8.0, -1.0, "针肋", ha="center", fontsize=7.5, color="#A04000")
    # base plate
    ax.add_patch(Rectangle((0.5, -2.05), 9.0, 0.35, fc="#85929E", ec="#424949", lw=0.9))
    # side outlets
    ax.annotate("", xy=(0.45, -0.2), xytext=(0.8, -0.2),
                arrowprops=dict(arrowstyle="-|>", color="#1E8449", lw=2.0))
    ax.annotate("", xy=(9.55, -0.2), xytext=(9.2, -0.2),
                arrowprops=dict(arrowstyle="-|>", color="#1E8449", lw=2.0))
    ax.text(0.42, 0.25, "出口1", ha="right", fontsize=7.5, color="#1E8449")
    ax.text(9.58, 0.25, "出口2", ha="left", fontsize=7.5, color="#1E8449")
    # dimension lines (right side)
    ax.plot([9.9, 10.0], [2.35, 2.35], "k-", lw=0.8)
    ax.plot([9.9, 10.0], [3.5, 3.5], "k-", lw=0.8)
    ax.annotate("", xy=(9.95, 2.35), xytext=(9.95, 3.5),
                arrowprops=dict(arrowstyle="<->", color="k", lw=0.8))
    ax.text(10.05, 2.9, "歧管层\n高度 Hm", ha="left", va="center", fontsize=7.5)
    ax.plot([9.9, 10.0], [-1.7, -1.7], "k-", lw=0.8)
    ax.plot([9.9, 10.0], [1.35, 1.35], "k-", lw=0.8)
    ax.annotate("", xy=(9.95, -1.7), xytext=(9.95, 1.35),
                arrowprops=dict(arrowstyle="<->", color="k", lw=0.8))
    ax.text(10.05, -0.2, "微通道层\n高度 Hc", ha="left", va="center", fontsize=7.5)
    ax.set_xlim(0, 12.2)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title("(b) 系统剖面结构与热流、水流路径", fontsize=10)

    out = os.path.join(FIGDIR, "fig2_structure.png")
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", out)

# ===========================================================================
# 图 3  主效应
# ===========================================================================
def draw_fig3():
    params = [("β", "beta", [0.10, 0.15, 0.20, 0.30]),
              ("λ", "lam", [3, 3.5, 4, 4.5]),
              ("N", "N", [2, 4, 6, 8, 10])]
    fig, axes = plt.subplots(3, 3, figsize=(9.6, 7.2), sharex=False)
    for j, (pname, col, levels) in enumerate(params):
        means = {i: [] for i in range(3)}
        for lv in levels:
            sub = fin[fin[col] == lv][["R", "dP", "UT"]].mean()
            for i in range(3):
                means[i].append(float(sub.iloc[i]))
        for i in range(3):
            ax = axes[i, j]
            v = means[i]
            ax.plot(levels, v, "o-", color=COLORS[i], lw=1.8, ms=5)
            ax.set_title(f"{pname} 对 {ylabels[i].split()[1]}" if False else
                         (f"β 对 {ylabels[i]}" if pname == "β" else f"{pname} 对 {ylabels[i]}"), fontsize=9)
            ax.grid(alpha=0.3)
            if j == 0:
                ax.set_ylabel(ylabels[i], fontsize=8.5)
            if i == 2:
                ax.set_xlabel(pname, fontsize=9)
            pad = (max(v) - min(v)) * 0.18 + 1e-9
            ax.set_ylim(min(v) - pad, max(v) + pad)
            ax.tick_params(labelsize=8)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    out = os.path.join(FIGDIR, "fig3_maineffects.png")
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", out)

# ===========================================================================
# 图 4  一次确定性 5 折交叉验证的一致性
# ===========================================================================
def draw_fig4():
    kf = KFold(n_splits=5, shuffle=True, random_state=6)
    pooled = {k: ([], []) for k in range(3)}
    for tr, te in kf.split(Z):
        for k in range(3):
            m = Ridge(alpha=1e-10).fit(design(Z[tr]), Y[tr, k])
            p = m.predict(design(Z[te]))
            pooled[k][0].extend(p); pooled[k][1].extend(Y[te, k])
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.4))
    for k, ax in enumerate(axes):
        p = np.array(pooled[k][0]); t = np.array(pooled[k][1])
        ax.scatter(t, p, s=22, c=COLORS[k], alpha=0.8, edgecolors="white", lw=0.4, zorder=3)
        lo = min(t.min(), p.min()); hi = max(t.max(), p.max())
        ax.plot([lo, hi], [lo, hi], "k--", lw=1.2, zorder=2)
        ss_res = np.sum((t - p) ** 2); ss_tot = np.sum((t - t.mean()) ** 2)
        r2 = 1 - ss_res / ss_tot
        ax.set_title(f"{ylabels[k]}\nR² = {r2:.6f}", fontsize=9)
        ax.set_xlabel("样本观测值", fontsize=8.5)
        ax.set_ylabel("模型预测值", fontsize=8.5)
        ax.grid(alpha=0.3); ax.tick_params(labelsize=7.5)
    fig.tight_layout(rect=[0, 0, 1, 0.88])
    out = os.path.join(FIGDIR, "fig4_cv_parity.png")
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", out)

# ===========================================================================
# 图 5  候选模型交叉验证误差对比
# ===========================================================================
def draw_fig5():
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel
    def gpr():
        return GaussianProcessRegressor(
            kernel=ConstantKernel(1.0) * RBF(length_scale=1.0, length_scale_bounds=(1e-2, 1e2))
                  + WhiteKernel(noise_level=1e-10, noise_level_bounds=(1e-12, 1e-3)),
            alpha=0.0, normalize_y=True, random_state=0)
    rngs = Y.max(0) - Y.min(0)
    results = {}
    for name, dg, mf in [("二次响应面", 2, lambda: Ridge(alpha=1e-10)),
                         ("三次响应面", 3, lambda: Ridge(alpha=1e-10)),
                         ("高斯过程", 3, gpr)]:
        pooled = {k: ([], []) for k in range(3)}
        for r in range(5):
            kf = KFold(n_splits=5, shuffle=True, random_state=r * 100 + 6)
            for tr, te in kf.split(Z):
                for k in range(3):
                    m = mf(); m.fit(design(Z[tr], dg), Y[tr, k])
                    p = m.predict(design(Z[te], dg))
                    pooled[k][0].extend(p); pooled[k][1].extend(Y[te, k])
        vals = []
        for k in range(3):
            p = np.array(pooled[k][0]); t = np.array(pooled[k][1])
            vals.append(np.sqrt(np.mean((t - p) ** 2)) / rngs[k] * 100)
        results[name] = vals
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    x = np.arange(3); w = 0.25
    models = list(results)
    colors_m = ["#5DADE2", "#E67E22", "#27AE60"]
    for i, name in enumerate(models):
        ax.bar(x + (i - 1) * w, results[name], w, label=name, color=colors_m[i], edgecolor="white")
        for xi, v in zip(x + (i - 1) * w, results[name]):
            ax.text(xi, v * 1.08, f"{v:.3g}%", ha="center", va="bottom", fontsize=7.5)
    ax.set_yscale("log")
    ax.set_xticks(x); ax.set_xticklabels(["无量纲热阻 R*", "无量纲压降 Δp*", "无量纲温度非均匀性 U*T"], fontsize=9)
    ax.set_ylabel("范围归一化 RMSE（%，对数坐标）", fontsize=9)
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    ax.set_title("三种候选模型的重复 5 折交叉验证误差对比", fontsize=11)
    fig.tight_layout()
    out = os.path.join(FIGDIR, "fig5_model_cmp.png")
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", out)

# ===========================================================================
# 图 6  固定 N=4 的三项响应面
# ===========================================================================
def draw_fig6():
    B = np.linspace(0.10, 0.30, 120)
    L = np.linspace(3.0, 4.5, 120)
    BB, LL = np.meshgrid(B, L)
    pts = np.column_stack([BB.ravel(), LL.ravel(), np.full(BB.size, 4.0)])
    P = np.column_stack([m.predict(design((pts - MU) / SD)) for m in models])
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.6))
    for k, ax in enumerate(axes):
        Zz = P[:, k].reshape(BB.shape)
        cf = ax.contourf(BB, LL, Zz, levels=18, cmap="RdYlBu_r")
        ax.contour(BB, LL, Zz, levels=10, colors="k", linewidths=0.35, alpha=0.35)
        ax.set_title(ylabels[k], fontsize=10)
        ax.set_xlabel("针肋宽度比 β", fontsize=8.5)
        ax.set_ylabel("歧管深高比 λ", fontsize=8.5)
        ax.tick_params(labelsize=8)
        fig.colorbar(cf, ax=ax, shrink=0.9)
        if k == 0:
            ax.plot(0.220, 4.5, "k*", ms=11, zorder=5)
            ax.annotate("等权方案", (0.220, 4.5), textcoords="offset points", xytext=(8, -10), fontsize=7.5)
        if k == 1:
            ax.plot(0.220, 4.5, "k*", ms=11, zorder=5)
        if k == 2:
            ax.plot(0.220, 4.5, "k*", ms=11, zorder=5)
            ax.annotate("等权方案", (0.220, 4.5), textcoords="offset points", xytext=(-18, 8), fontsize=7.5)
    fig.tight_layout(rect=[0, 0, 1, 0.9])
    out = os.path.join(FIGDIR, "fig6_response.png")
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", out)

# ===========================================================================
# 图 7  Pareto 前沿
# ===========================================================================
def draw_fig7():
    betas = np.round(np.arange(0.10, 0.3001, 0.001), 6)
    lambs = np.round(np.arange(3.0, 4.5001, 0.01), 6)
    Ns = [2, 4, 6, 8, 10]
    G, P = pred_grid(betas, lambs, Ns)
    lo = df[["R", "dP", "UT"]].values.min(0); hi = df[["R", "dP", "UT"]].values.max(0)
    S = (P - lo) / (hi - lo)
    wg = np.arange(0, 1.0001, 0.05)
    cand = {}
    for w1 in wg:
        for w2 in wg:
            w3 = 1 - w1 - w2
            if w3 < -1e-9:
                continue
            sc = S @ np.array([w1, w2, w3])
            i = int(np.argmin(sc))
            cand[i] = min(cand.get(i, 1e9), float(sc.min()))
    idx = sorted(cand)
    Pn = S[idx]
    fig = plt.figure(figsize=(9.2, 5.4))
    ax = fig.add_subplot(111, projection="3d")
    sc = ax.scatter(Pn[:, 0], Pn[:, 1], Pn[:, 2], c=np.arange(len(idx)),
                    cmap="viridis", s=16, alpha=0.9, depthshade=True)
    # projections
    ax.scatter(Pn[:, 0], Pn[:, 1], np.full(len(idx), -0.12), c="0.75", s=8, alpha=0.5, depthshade=False)
    ax.scatter(Pn[:, 0], np.full(len(idx), 1.12), Pn[:, 2], c="0.75", s=8, alpha=0.5, depthshade=False)
    ax.scatter(np.full(len(idx), -0.12), Pn[:, 1], Pn[:, 2], c="0.75", s=8, alpha=0.5, depthshade=False)
    for tag, (b, l, n) in [("等权综合", (0.220, 4.5, 4)), ("偏好鲁棒", (0.226, 4.5, 6))]:
        sv = (pred_xyz(b, l, n) - lo) / (hi - lo)
        ax.scatter([sv[0]], [sv[1]], [sv[2]], marker="*", s=260, c="red", edgecolors="k", zorder=6)
        ax.text(sv[0], sv[1], sv[2] + 0.04, tag, fontsize=8.5, color="darkred")
    ax.set_xlabel("归一化热阻 s1", fontsize=9)
    ax.set_ylabel("归一化压降 s2", fontsize=9)
    ax.set_zlabel("归一化非均匀性 s3", fontsize=9)
    ax.set_zlim(-0.12, 1.12)
    ax.view_init(elev=18, azim=-58)
    fig.tight_layout()
    out = os.path.join(FIGDIR, "fig7_pareto.png")
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", out)

# ===========================================================================
# 图 8  权重变化对典型方案归一化损失的影响
# ===========================================================================
def draw_fig8():
    schemes = [("热阻优先", (0.228, 3.17, 10), "#C0392B"),
               ("压降优先", (0.223, 4.50, 2), "#2471A3"),
               ("均匀性优先", (0.224, 4.50, 4), "#1E8449"),
               ("等权综合", (0.220, 4.50, 4), "#7D3C98"),
               ("等权理想点", (0.224, 4.50, 6), "#B7950B")]
    lo = df[["R", "dP", "UT"]].values.min(0); hi = df[["R", "dP", "UT"]].values.max(0)
    w = np.linspace(0, 1, 201)
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 3.9))
    for ax, mode in zip(axes, ["w1", "w2"]):
        for name, (b, l, n), c in schemes:
            p = pred_xyz(b, l, n)
            s = (p - lo) / (hi - lo)
            if mode == "w1":
                w2 = (1 - w) / 2
                L = w * s[0] + w2 * s[1] + w2 * s[2]
            else:
                w1 = (1 - w) / 2
                L = w1 * s[0] + w * s[1] + w1 * s[2]
            ax.plot(w, L, lw=1.8, color=c, label=name)
        ax.set_xlabel("热阻权重 w1（w2 = w3 = (1−w1)/2）" if mode == "w1"
                      else "压降权重 w2（w1 = w3 = (1−w2)/2）", fontsize=8.5)
        ax.set_ylabel("归一化加权损失 L(x, w)", fontsize=8.5)
        ax.grid(alpha=0.3); ax.tick_params(labelsize=8)
    axes[0].legend(fontsize=8, loc="upper left")
    fig.tight_layout(rect=[0, 0, 1, 0.9])
    out = os.path.join(FIGDIR, "fig8_weights.png")
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", out)

# ===========================================================================
# 图 9  最小最大后悔
# ===========================================================================
def draw_fig9():
    betas = np.round(np.arange(0.10, 0.3001, 0.001), 6)
    lambs = np.round(np.arange(3.0, 4.5001, 0.01), 6)
    Ns = [2, 4, 6, 8, 10]
    G, P = pred_grid(betas, lambs, Ns)
    lo = df[["R", "dP", "UT"]].values.min(0); hi = df[["R", "dP", "UT"]].values.max(0)
    S = (P - lo) / (hi - lo)
    wg = np.arange(0, 1.0001, 0.05)
    cand = {}
    for w1 in wg:
        for w2 in wg:
            w3 = 1 - w1 - w2
            if w3 < -1e-9:
                continue
            sc = S @ np.array([w1, w2, w3])
            i = int(np.argmin(sc))
            cand[i] = min(cand.get(i, 1e9), float(sc.min()))
    idx = sorted(cand)
    SC = S[idx]
    wg01 = np.arange(0, 1.0001, 0.01)
    wpts = []
    for w1 in wg01:
        for w2 in wg01:
            w3 = 1 - w1 - w2
            if w3 < -1e-9:
                continue
            wpts.append((w1, w2, w3))
    W = np.array(wpts)
    Lmat = SC @ W.T
    Lmin = Lmat.min(0)
    Reg = Lmat - Lmin
    maxreg = Reg.max(1)
    irob = int(np.argmin(maxreg))

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.0))
    ax = axes[0]
    # regret slice along w1 (w2=w3)
    w1s = np.linspace(0, 1, 201)
    rep_schemes = [("等权综合", (0.220, 4.5, 4), "#7D3C98"),
                   ("热阻优先", (0.228, 3.17, 10), "#C0392B"),
                   ("压降优先", (0.223, 4.5, 2), "#2471A3"),
                   ("均匀性优先", (0.224, 4.5, 4), "#1E8449"),
                   ("偏好鲁棒", (0.226, 4.5, 6), "#E67E22")]
    env = None
    for name, (b, l, n), c in rep_schemes:
        sv = (pred_xyz(b, l, n) - lo) / (hi - lo)
        w2 = (1 - w1s) / 2
        L = np.column_stack([w1s, w2, w2]) @ sv
        Lb = (SC @ np.column_stack([w1s, w2, w2]).T).min(axis=0)
        reg = L - Lb
        env = reg if env is None else np.maximum(env, reg)
        lw = 2.2 if name == "偏好鲁棒" else 1.4
        ax.plot(w1s, reg, lw=lw, color=c, label=name)
    ax.plot(w1s, env, "k--", lw=1.0, label="所选方案后悔值上包络")
    ax.set_xlabel("热阻权重 w1（w2 = w3 = (1−w1)/2）", fontsize=8.5)
    ax.set_ylabel("后悔值 Regret(x, w)", fontsize=8.5)
    ax.legend(fontsize=7.5, loc="upper left")
    ax.grid(alpha=0.3); ax.tick_params(labelsize=8)

    ax = axes[1]
    order = np.argsort(maxreg)
    ax.scatter(np.arange(len(idx)), maxreg[order], s=12, c="#5DADE2", alpha=0.75)
    ax.scatter(irob, maxreg[irob], s=90, marker="*", c="#E67E22", edgecolors="k", zorder=5)
    ax.annotate(f"偏好鲁棒方案\n最大后悔 = {maxreg[irob]:.6f}",
                (irob, maxreg[irob]), textcoords="offset points", xytext=(25, -5),
                fontsize=8.5, color="#B9770E")
    ax.set_xlabel("支持型 Pareto 候选方案（按最大后悔排序）", fontsize=8.5)
    ax.set_ylabel("最大后悔值 max_w Regret(x, w)", fontsize=8.5)
    ax.grid(alpha=0.3); ax.tick_params(labelsize=8)
    fig.tight_layout(rect=[0, 0, 1, 0.9])
    out = os.path.join(FIGDIR, "fig9_regret.png")
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", out)

if __name__ == "__main__":
    draw_fig2()
    draw_fig3()
    draw_fig4()
    draw_fig5()
    draw_fig6()
    draw_fig7()
    draw_fig8()
    draw_fig9()
    print("ALL FIGURES DONE")
