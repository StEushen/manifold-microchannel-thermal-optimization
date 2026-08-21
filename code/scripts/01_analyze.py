# -*- coding: utf-8 -*-
"""Reproduce the draft's computations from Attachment 2 and dump a report."""
import json, os
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "附件2_数据.xlsx")
OUT = os.path.join(ROOT, "report.json")

df = pd.read_excel(DATA, header=1)
df.columns = ["no", "beta", "lam", "N", "R", "dP", "UT"]

fin = df[df.beta > 0].reset_index(drop=True)
nofin = df[df.beta == 0].reset_index(drop=True)

X = fin[["beta", "lam", "N"]].values.astype(float)
Y = fin[["R", "dP", "UT"]].values.astype(float)
ynames = ["R*", "dP*", "UT*"]

MU = np.array([0.1875, 3.75, 6.0])
SD = np.array([0.073951, 0.559017, 2.828427])
Z = (X - MU) / SD

def design(Zm, degree):
    cols = [np.ones(len(Zm))]
    for d in range(1, degree + 1):
        for i in range(d + 1):
            for j in range(d - i + 1):
                l = d - i - j
                cols.append((Zm[:, 0] ** i) * (Zm[:, 1] ** j) * (Zm[:, 2] ** l))
    return np.column_stack(cols)

Phi3 = design(Z, 3)
Phi2 = design(Z, 2)

def metrics(y_true, y_pred, rng):
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    ss_tot = float(np.sum((y_true - y_true.mean()) ** 2))
    r2 = 1 - ss_res / ss_tot
    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    nrmse = rmse / rng
    return {"R2": r2, "MAE": mae, "RMSE": rmse, "NRMSE": nrmse, "NRMSE_pct": nrmse * 100}

def run_cv(design_fn, model_factory, n_repeats=5):
    out = {k: [] for k in ["R2", "MAE", "RMSE", "NRMSE"]}
    for r in range(n_repeats):
        kf = KFold(n_splits=5, shuffle=True, random_state=r * 100 + 7)
        for tr, te in kf.split(Z):
            for k in range(3):
                m = model_factory()
                m.fit(design_fn(Z[tr]), Y[tr, k])
                p = m.predict(design_fn(Z[te]))
                out["RMSE"].extend((Y[te, k] - p) ** 2)
                out["MAE"].append(np.abs(Y[te, k] - p))
                # R2 needs pooled sums; collect residuals and true values instead
    return out

# Simpler correct CV: collect pooled predictions per output
def cv_scores(design_fn, model_factory, n_repeats=5, seed0=6):
    pooled_pred = {k: [] for k in range(3)}
    pooled_true = {k: [] for k in range(3)}
    for r in range(n_repeats):
        kf = KFold(n_splits=5, shuffle=True, random_state=r * 100 + seed0)
        for tr, te in kf.split(Z):
            for k in range(3):
                m = model_factory()
                m.fit(design_fn(Z[tr]), Y[tr, k])
                pooled_pred[k].extend(m.predict(design_fn(Z[te])))
                pooled_true[k].extend(Y[te, k])
    rngs = Y.max(0) - Y.min(0)
    res = {}
    for k in range(3):
        t = np.array(pooled_true[k]); p = np.array(pooled_pred[k])
        res[ynames[k]] = metrics(t, p, rngs[k])
    return res

def ridge_factory(alpha=1e-10):
    def f():
        return Ridge(alpha=alpha)
    return f

def gpr_factory():
    def f():
        return GaussianProcessRegressor(
            kernel=ConstantKernel(1.0) * RBF(length_scale=1.0, length_scale_bounds=(1e-2, 1e2))
                  + WhiteKernel(noise_level=1e-10, noise_level_bounds=(1e-12, 1e-3)),
            alpha=0.0, normalize_y=True, random_state=0)
    return f

rep = {}
rep["cubic"] = cv_scores(lambda Zm: design(Zm, 3), ridge_factory())
rep["quadratic"] = cv_scores(lambda Zm: design(Zm, 2), ridge_factory())
rep["gpr"] = cv_scores(lambda Zm: design(Zm, 3), gpr_factory())

# ---------------------------------------------------------------------------
# Final cubic fit on all 80 points, coefficients
# ---------------------------------------------------------------------------
coefs = {}
preds_all = {}
for k in range(3):
    m = Ridge(alpha=1e-10).fit(Phi3, Y[:, k])
    coefs[ynames[k]] = [float(c) for c in m.coef_]
    preds_all[ynames[k]] = m.predict(Phi3)

# ---------------------------------------------------------------------------
# Main effects (means over the other two variables)
# ---------------------------------------------------------------------------
main_effects = {}
for pname, col in [("beta", 0), ("lam", 1), ("N", 2)]:
    levels = sorted(fin[pname].unique())
    me = {pn: [] for pn in ynames}
    for lv in levels:
        sub = fin[fin[pname] == lv][["R", "dP", "UT"]].mean()
        for i, pn in enumerate(ynames):
            me[pn].append(float(sub.iloc[i]))
    main_effects[pname] = {"levels": [float(v) for v in levels], "values": me}

# percentages quoted in 5.1.7 (levels sorted: beta [.10,.15,.20,.30], lam [3,3.5,4,4.5], N [2,4,6,8,10])
def pct(a, b):
    return (b - a) / a * 100
me = main_effects
key_me = {
    "beta_01_02": {
        "R": pct(me["beta"]["values"]["R*"][0], me["beta"]["values"]["R*"][2]),
        "dP": pct(me["beta"]["values"]["dP*"][0], me["beta"]["values"]["dP*"][2]),
        "UT": pct(me["beta"]["values"]["UT*"][0], me["beta"]["values"]["UT*"][2]),
    },
    "beta_02_03": {
        "R": pct(me["beta"]["values"]["R*"][2], me["beta"]["values"]["R*"][3]),
        "dP": pct(me["beta"]["values"]["dP*"][2], me["beta"]["values"]["dP*"][3]),
        "UT": pct(me["beta"]["values"]["UT*"][2], me["beta"]["values"]["UT*"][3]),
    },
    "lam_3_45": {
        "R": pct(me["lam"]["values"]["R*"][0], me["lam"]["values"]["R*"][3]),
        "dP": pct(me["lam"]["values"]["dP*"][0], me["lam"]["values"]["dP*"][3]),
        "UT": pct(me["lam"]["values"]["UT*"][0], me["lam"]["values"]["UT*"][3]),
    },
    "N_2_10": {
        "R": pct(me["N"]["values"]["R*"][0], me["N"]["values"]["R*"][4]),
        "dP": pct(me["N"]["values"]["dP*"][0], me["N"]["values"]["dP*"][4]),
        "UT": pct(me["N"]["values"]["UT*"][0], me["N"]["values"]["UT*"][4]),
    },
}
rep["main_effects_pct"] = key_me

# ---------------------------------------------------------------------------
# Grid search + normalization + weighted loss
# ---------------------------------------------------------------------------
betas = np.round(np.arange(0.10, 0.3001, 0.001), 6)
lambs = np.round(np.arange(3.0, 4.5001, 0.01), 6)
Ns = [2, 4, 6, 8, 10]

grid = []
for b in betas:
    for l in lambs:
        for n in Ns:
            grid.append((b, l, n))
G = np.array(grid)
ZG = (G - MU) / SD
PhiG = design(ZG, 3)

PRED = np.column_stack([Ridge(alpha=1e-10).fit(Phi3, Y[:, k]).predict(PhiG) for k in range(3)])

lo = df[["R", "dP", "UT"]].values.min(0); hi = df[["R", "dP", "UT"]].values.max(0)
Sn = (PRED - lo) / (hi - lo)

def best_weighted(w):
    score = Sn @ np.array(w)
    i = int(np.argmin(score))
    return {"scheme": list(G[i]), "pred": [float(v) for v in PRED[i]],
            "s": [float(v) for v in Sn[i]], "loss": float(score[i])}

rep["eq"] = best_weighted([1/3, 1/3, 1/3])
rep["w_thermal"] = best_weighted([0.8, 0.1, 0.1])
rep["w_pressure"] = best_weighted([0.1, 0.8, 0.1])
rep["w_uniform"] = best_weighted([0.1, 0.1, 0.8])

# ideal-point distance (report the nearly-tied 0.224 point as in the draft)
ideal = Sn.min(0)
dist = np.sqrt(((Sn - ideal) ** 2).sum(1))
i = int(np.argmin(dist))
j0 = np.where((np.abs(G[:, 0] - 0.224) < 1e-9) & (G[:, 1] == 4.5) & (G[:, 2] == 6))[0][0]
rep["ideal_point"] = {"scheme": list(G[j0]), "pred": [float(v) for v in PRED[j0]],
                      "s": [float(v) for v in Sn[j0]], "dist": float(dist[j0]),
                      "argmin": list(G[i]), "dist_argmin": float(dist[i])}

# ---------------------------------------------------------------------------
# Supporting Pareto set via 0.05 weight grid
# ---------------------------------------------------------------------------
w_grid = np.arange(0, 1.0001, 0.05)
cand_idx = {}
for w1 in w_grid:
    for w2 in w_grid:
        w3 = 1 - w1 - w2
        if w3 < -1e-9:
            continue
        w = np.array([w1, w2, w3])
        score = Sn @ w
        i = int(np.argmin(score))
        cand_idx[i] = min(cand_idx.get(i, 1e9), float(score.min()))
pareto_idx = sorted(cand_idx)
rep["pareto_count"] = len(pareto_idx)

# ---------------------------------------------------------------------------
# Minimax regret over 0.01 weight grid
# ---------------------------------------------------------------------------
def regret_eval(idx_set, step=0.01):
    cands = np.array(idx_set)
    w1g = np.arange(0, 1.0001, step)
    maxreg = np.zeros(len(cands))
    reg_by_w = []
    for w1 in w1g:
        for w2 in w1g:
            w3 = 1 - w1 - w2
            if w3 < -1e-9:
                continue
            w = np.array([w1, w2, w3])
            L = Sn[cands] @ w
            Lmin = L.min()
            reg = L - Lmin
            maxreg = np.maximum(maxreg, reg)
    i = int(np.argmin(maxreg))
    return i, float(maxreg.min()), [float(v) for v in maxreg]

r_i, r_min, r_all = regret_eval(pareto_idx)
rep["minimax"] = {"scheme": list(G[pareto_idx[r_i]]),
                  "pred": [float(v) for v in PRED[pareto_idx[r_i]]],
                  "max_regret": r_min,
                  "regrets": r_all}

# ---------------------------------------------------------------------------
# Monte Carlo propagation
# ---------------------------------------------------------------------------
def mc(scheme, n=100000, seed=31):
    b, l, nfin = scheme
    rng = np.random.default_rng(seed)
    bs = rng.uniform(b - 0.01, b + 0.01, n)
    ls = rng.uniform(l - 0.05, l + 0.05, n)
    bs = np.clip(bs, 0.10, 0.30)
    ls = np.clip(ls, 3.0, 4.5)
    Gm = np.column_stack([bs, ls, np.full(n, nfin)])
    Zm = (Gm - MU) / SD
    Pm = np.column_stack([Ridge(alpha=1e-10).fit(Phi3, Y[:, k]).predict(design(Zm, 3)) for k in range(3)])
    out = {}
    for k, pn in enumerate(ynames):
        v = Pm[:, k]
        out[pn] = {"mean": float(v.mean()), "std": float(v.std()),
                   "cv_pct": float(v.std() / v.mean() * 100),
                   "p05": float(np.percentile(v, 5)), "p95": float(np.percentile(v, 95))}
    return out

rep["mc_eq"] = mc([0.220, 4.50, 4])
rep["mc_rob"] = mc([0.226, 4.50, 6])

# ---------------------------------------------------------------------------
# Elasticities at the two schemes
# ---------------------------------------------------------------------------
def elasticity(scheme):
    b, l, n = scheme
    out = {}
    for pn in ynames:
        m = Ridge(alpha=1e-10).fit(Phi3, Y[:, 0 if pn == "R*" else 1 if pn == "dP*" else 2])
        def pred(bv, lv):
            zm = (np.array([[bv, lv, n]]) - MU) / SD
            return float(m.predict(design(zm, 3))[0])
        hb = 1e-5; hl = 1e-5
        y0 = pred(b, l)
        eb = (pred(b + hb, l) - pred(b - hb, l)) / (2 * hb) * b / y0
        el = (pred(b, l + hl) - pred(b, l - hl)) / (2 * hl) * l / y0
        out[pn] = {"beta_elastic": float(eb), "lambda_elastic": float(el)}
    return out

rep["elastic_eq"] = elasticity([0.220, 4.50, 4])
rep["elastic_rob"] = elasticity([0.226, 4.50, 6])

# N perturbation table
rep["N_table"] = {}
for tag, (b, l) in [("eq", (0.220, 4.50)), ("rob", (0.226, 4.50))]:
    rows = []
    for n in ([2, 4, 6] if tag == "eq" else [4, 6, 8]):
        zm = (np.array([[b, l, n]]) - MU) / SD
        p = np.array([Ridge(alpha=1e-10).fit(Phi3, Y[:, k]).predict(design(zm, 3))[0] for k in range(3)])
        rows.append({"N": n, "R": float(p[0]), "dP": float(p[1]), "UT": float(p[2])})
    rep["N_table"][tag] = rows

# no-fin quadratic fit
ln = nofin["lam"].values; 
coef_nofin = {}
for k, pn in enumerate(ynames):
    yv = nofin.iloc[:, 4 + k].values
    A = np.column_stack([np.ones(len(ln)), ln, ln ** 2])
    c = np.linalg.lstsq(A, yv, rcond=None)[0]
    coef_nofin[pn] = [float(v) for v in c]
rep["nofin_quad"] = coef_nofin

rep["data_summary"] = {
    "n_total": int(len(df)), "n_fin": int(len(fin)), "n_nofin": int(len(nofin)),
    "ranges": {"lo": [float(v) for v in lo], "hi": [float(v) for v in hi]},
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1)

print(json.dumps(rep, ensure_ascii=False, indent=1))
