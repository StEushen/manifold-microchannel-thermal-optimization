# -*- coding: utf-8 -*-
"""Render all numbered equations as PNG images for the revised paper."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["mathtext.fontset"] = "cm"
plt.rcParams["font.family"] = "serif"

EQDIR = os.path.join(ROOT, "eqs")
os.makedirs(EQDIR, exist_ok=True)

def render_eq(num, tex, fontsize=15):
    fig = plt.figure(figsize=(0.1, 0.1))
    fig.text(0.0, 0.0, tex, fontsize=fontsize)
    path = os.path.join(EQDIR, f"eq{num}.png")
    fig.savefig(path, dpi=300, bbox_inches="tight", pad_inches=0.025, transparent=True)
    plt.close(fig)
    return path

def render_piecewise(num, left, rows, fontsize=15, brace_scale=2.5):
    """left: mathtext string before brace; rows: list of (mathtext, y)."""
    fig = plt.figure(figsize=(0.1, 0.1))
    fig.text(0.01, 0.5, left, fontsize=fontsize, ha="left", va="center")
    for tex, y in rows:
        fig.text(0.06, y, tex, fontsize=fontsize, ha="left", va="center")
    fig.text(0.055, 0.5, "{", fontsize=fontsize * brace_scale,
             ha="center", va="center", family="DejaVu Serif")
    path = os.path.join(EQDIR, f"eq{num}.png")
    fig.savefig(path, dpi=300, bbox_inches="tight", pad_inches=0.025, transparent=True)
    plt.close(fig)
    return path

EQS = {
    1: r"$V_h = 1.2\times 10^{-8}\,\mathrm{m^3},\qquad Q = q^{\prime\prime\prime} V_h = 60\,\mathrm{W}$",
    2: r"$Q = \dot{m}_\Sigma\, c_p\,(\bar{T}_{\mathrm{out,m}} - T_{\mathrm{in}}) + Q_{\mathrm{air}}$",
    3: r"$\bar{T}_{\mathrm{out,m}} - T_{\mathrm{in}} \simeq \frac{60}{0.001\times 4182} = 14.35\,\mathrm{K}$",
    4: r"$\nabla\cdot\mathbf{u} = 0$",
    5: r"$\rho\,(\mathbf{u}\cdot\nabla)\,\mathbf{u} = -\nabla p + \mu\nabla^2 \mathbf{u} + \rho\,\mathbf{g}$",
    6: r"$\rho\, c_p\, \mathbf{u}\cdot\nabla T_f = \nabla\cdot(k_f\nabla T_f)$",
    7: r"$\nabla\cdot(k_s\nabla T_s) + q_s^{\prime\prime\prime} = 0,\qquad q_s^{\prime\prime\prime} =$",
    8: r"$T_s = T_f,\qquad -k_s\frac{\partial T_s}{\partial n_s} = -k_f\frac{\partial T_f}{\partial n_s}$",
    9: r"$-k_s\frac{\partial T_s}{\partial n} = h_{\mathrm{air}}(T_s - T_\infty),\qquad T_\infty = 293\,\mathrm{K}$",
    10: r"$M_{j+1}^{s} = M_j^{s} - \dot{m}_j,\qquad M_{j+1}^{c} = M_j^{c} + \dot{m}_j,\qquad \sum_{j=1}^{J}\dot{m}_j = \dot{m}_\Sigma$",
    11: r"$B\,\mathbf{m}_e = \mathbf{s},\qquad \mathbf{1}^{\mathrm{T}}\mathbf{s} = 0$",
    12: r"$p_j^{s} - p_j^{c} = \left[f_c\frac{L_c}{D_{h,c}} + K_v + N\,K_p(\beta, Re_g, \cdots)\right]\frac{\rho u_g^{2}}{2}$",
    13: r"$D_h = \frac{4A_f}{P_w},\qquad Re = \frac{\rho u D_h}{\mu}$",
    14: r"$\phi(\beta, N) = \frac{N\, n_\perp\, \pi\, \beta^{2} w_c^{2}}{4 A_{pl}}$",
    15: r"$\varepsilon = 1 - \phi$",
    16: r"$u_g \sim \frac{\dot{m}_j}{\rho\,\varepsilon\, A_{c0}}$",
    17: r"$A_m = W_m\lambda H_c,\qquad u_m = \frac{\dot{m}_m}{\rho W_m\lambda H_c},\qquad D_{h,m} = \frac{2W_m\lambda H_c}{W_m + \lambda H_c}$",
    18: r"$\Delta p_{m,f} \sim \frac{\mu L_m \dot{V}_m}{W_m H_m^{3}} \propto \lambda^{-3},\qquad \Delta p_{m,\mathrm{loc}} \sim K_m\frac{\rho u_m^{2}}{2} \propto \lambda^{-2}$",
    19: r"$\frac{\partial \Delta p}{\partial \beta} > 0,\qquad \Delta_N \Delta p > 0,\qquad \frac{\partial \Delta p}{\partial \lambda} < 0$",
    20: r"$\dot{m}_j c_p \frac{dT_{b,j}}{dx} = h_j P_{w,j}\,(T_{w,j} - T_{b,j})$",
    21: r"$T_{\mathrm{out},j} = T_{w,j} - (T_{w,j} - T_{\mathrm{in},j})\,e^{-NTU_j},\qquad NTU_j = \frac{h_j A_{\mathrm{wet},j}}{\dot{m}_j c_p}$",
    22: r"$A_{\mathrm{wet}} = A_{w0} + N\,n_\perp\left(\pi\beta w_c H_c - \nu_b\frac{\pi\beta^{2} w_c^{2}}{4}\right)$",
    23: r"$h = \frac{k_f Nu}{D_{h,c}},\qquad Nu = F_{Nu}\left(Re_g,\ Pr,\ \beta,\ N,\ \frac{s_x}{d_p},\ \frac{s_y}{d_p},\ \frac{H_c}{w_c}\right)$",
    24: r"$R_{th} = \frac{T_{\max} - T_{\mathrm{in}}}{Q} = R_{\mathrm{chip,gen}} + R_{\mathrm{spread}} + R_{\mathrm{conv}} + R_{\mathrm{fluid,mal}}$",
    25: r"$R_{\mathrm{conv}} = \frac{1}{h A_{\mathrm{wet}}} = \frac{D_{h,c}}{k_f\, Nu\, A_{\mathrm{wet}}}$",
    26: r"$\frac{\partial \ln R_{\mathrm{conv}}}{\partial x} = \frac{\partial \ln D_{h,c}}{\partial x} - \frac{\partial \ln Nu}{\partial x} - \frac{\partial \ln A_{\mathrm{wet}}}{\partial x}$",
    27: r"$U_T = \frac{\sigma_T}{\Theta_{\mathrm{ref}}},\qquad \sigma_T = \sqrt{\frac{1}{M}\sum_{i=1}^{M}(T_i - \bar{T})^{2}}$",
    28: r"$C_m = \frac{\sqrt{\frac{1}{J}\sum_{j=1}^{J}(\dot{m}_j - \bar{m})^{2}}}{\bar{m}},\qquad \bar{m} = \frac{\dot{m}_\Sigma}{J}$",
    29: r"$T_i - T_{\mathrm{in}} \simeq Q_i R_{s,i} + \frac{Q_i}{h_i A_i} + \frac{Q_{\mathrm{up},i}}{\dot{m}_i c_p}$",
    30: r"$T_i - \bar{T} \simeq -\left(a_i\frac{Q_i}{\bar{h}_i A_i} + \frac{Q_{\mathrm{up},i}}{\bar{m} c_p}\right)\delta_i + \delta_{T_g,i}$",
    31: r"$T_{\max} = T_{\mathrm{in}} + Q\, R_{th}$",
    32: r"$P_{\mathrm{pump}} = \frac{\Delta p\, \dot{V}}{\eta_p}$",
    33: r"$\sigma_{th} \sim \frac{E\,\alpha_T}{1 - \nu}\,\Delta T$",
    34: r"$\hat{y}_k(\mathbf{x}) =$",
    35: r"$g_{k,p} = a_{k,0} + \sum_{1\leq i+j+l\leq 3} a_{k,ijl}\, z_\beta^{i}\, z_\lambda^{j}\, z_N^{l}$",
    36: r"$z_\beta = \frac{\beta - 0.1875}{0.073951},\qquad z_\lambda = \frac{\lambda - 3.75}{0.559017},\qquad z_N = \frac{N - 6}{2.828427}$",
    37: r"$R^{2} = 1 - \frac{\sum_i (y_i - \hat{y}_i)^{2}}{\sum_i (y_i - \bar{y})^{2}},\qquad RMSE = \sqrt{\frac{1}{n}\sum_i (y_i - \hat{y}_i)^{2}},\qquad NRMSE = \frac{RMSE}{y_{\max} - y_{\min}}$",
    38: r"$\min_{\beta,\lambda,N}\ \left[\hat{R}^{*}(\beta,\lambda,N),\ \widehat{\Delta p}^{\,*}(\beta,\lambda,N),\ \hat{U}_T^{*}(\beta,\lambda,N)\right]$",
    39: r"$0.10 \leq \beta \leq 0.30,\qquad 3 \leq \lambda \leq 4.5,\qquad N \in \{2,\,4,\,6,\,8,\,10\}$",
    40: r"$s_k(\mathbf{x}) = \frac{\hat{y}_k(\mathbf{x}) - y_k^{\min}}{y_k^{\max} - y_k^{\min}},\qquad k = 1,\,2,\,3$",
    41: r"$L_{\mathrm{eq}}(\mathbf{x}) = \frac{s_1(\mathbf{x}) + s_2(\mathbf{x}) + s_3(\mathbf{x})}{3}$",
    42: r"$(\beta,\ \lambda,\ N) = (0.220,\ 4.50,\ 4)$",
    43: r"$\mathcal{W} = \{w : w_k \geq 0,\ \sum_{k=1}^{3} w_k = 1\},\qquad L(\mathbf{x}, w) = w^{\mathrm{T}} s(\mathbf{x})$",
    44: r"$\mathrm{Regret}(\mathbf{x}, w) = L(\mathbf{x}, w) - \min_{\mathbf{x}'\in P} L(\mathbf{x}', w)$",
    45: r"$\mathbf{x}_{\mathrm{rob}} = \arg\min_{\mathbf{x}\in P}\ \max_{w\in\mathcal{W}}\ \mathrm{Regret}(\mathbf{x}, w)$",
    46: r"$(\beta,\ \lambda,\ N) = (0.226,\ 4.50,\ 6)$",
    47: r"$(R^{*},\ \Delta p^{*},\ U_T^{*}) = (0.734274,\ 0.098231,\ 0.790195)$",
    48: r"$E_{kj} = \frac{\partial \hat{y}_k}{\partial x_j}\cdot\frac{x_j}{\hat{y}_k}$",
    49: r"$\tilde{\beta} \sim U[\beta_0 - 0.01,\ \beta_0 + 0.01],\qquad \tilde{\lambda} \sim U[\lambda_0 - 0.05,\ \lambda_0 + 0.05]$",
    50: r"$\frac{\Delta p}{\Delta p_0} \in [\,1.05,\ 1.05^{2}\,] = [\,1.05,\ 1.1025\,]$",
    51: r"$\hat{y} = \Phi(\beta,\ \lambda,\ N,\ \dot{m},\ T_{\mathrm{in}},\ q^{\prime\prime\prime})$",
    52: r"$(\beta,\ \lambda,\ N) = (0.220,\ 4.50,\ 4)$",
    53: r"$(\beta,\ \lambda,\ N) = (0.226,\ 4.50,\ 6)$",
}

render_piecewise(7, EQS[7], [(r"$5\times 10^{9},\quad r \in \Omega_{\mathrm{chip}}$", 0.66),
                             (r"$0,\quad r \in \Omega_{\mathrm{AlN}}$", 0.34)])
render_piecewise(34, EQS[34], [(r"$g_{k,0}(\lambda),\qquad \beta = 0,\ N = 0$", 0.66),
                               (r"$g_{k,p}(\beta,\lambda,N),\qquad \beta > 0,\ N \geq 2$", 0.34)])
for n, tex in EQS.items():
    if n in (7, 34):
        continue
    render_eq(n, tex)

print("equations done:", len(EQS))
