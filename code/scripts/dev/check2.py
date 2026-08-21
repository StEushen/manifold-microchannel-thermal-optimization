# -*- coding: utf-8 -*-
import numpy as np, pandas as pd, os
from sklearn.linear_model import Ridge

ROOT = r"C:\Users\粟俊棋\Desktop\修改"
df = pd.read_excel(os.path.join(ROOT, "附件 2：不同结构参数下无量纲的热阻、压降和温度非均匀性结果数据.xlsx"), header=1)
df.columns = ["no","beta","lam","N","R","dP","UT"]
fin = df[df.beta>0].reset_index(drop=True)

print("== mean per beta level ==")
for lv in [0.10,0.15,0.20,0.30]:
    sub = fin[fin.beta==lv][["R","dP","UT"]].mean()
    print(lv, sub.round(6).tolist())
print("== mean per lam level ==")
for lv in [3,3.5,4,4.5]:
    sub = fin[fin.lam==lv][["R","dP","UT"]].mean()
    print(lv, sub.round(6).tolist())
print("== mean per N level ==")
for lv in [2,4,6,8,10]:
    sub = fin[fin.N==lv][["R","dP","UT"]].mean()
    print(lv, sub.round(6).tolist())
print("== nofin means ==")
print(df[df.beta==0][["R","dP","UT"]].mean().round(6).tolist())

def pct(a,b): return (b-a)/a*100
print("beta .10->.20", pct(fin[fin.beta==0.10].R.mean(), fin[fin.beta==0.20].R.mean()),
      pct(fin[fin.beta==0.10].dP.mean(), fin[fin.beta==0.20].dP.mean()),
      pct(fin[fin.beta==0.10].UT.mean(), fin[fin.beta==0.20].UT.mean()))
print("beta .20->.30", pct(fin[fin.beta==0.20].R.mean(), fin[fin.beta==0.30].R.mean()),
      pct(fin[fin.beta==0.20].dP.mean(), fin[fin.beta==0.30].dP.mean()),
      pct(fin[fin.beta==0.20].UT.mean(), fin[fin.beta==0.30].UT.mean()))
print("beta .10->.30 cumulative", pct(fin[fin.beta==0.10].R.mean(), fin[fin.beta==0.30].R.mean()),
      pct(fin[fin.beta==0.10].dP.mean(), fin[fin.beta==0.30].dP.mean()),
      pct(fin[fin.beta==0.10].UT.mean(), fin[fin.beta==0.30].UT.mean()))

# grid search with 84-point normalization
Y84 = df[["R","dP","UT"]].values
lo84, hi84 = Y84.min(0), Y84.max(0)
Y = fin[["R","dP","UT"]].values
X = fin[["beta","lam","N"]].values
MU=np.array([0.1875,3.75,6.0]); SD=np.array([0.073951,0.559017,2.828427])
def design(Zm, deg):
    cols=[np.ones(len(Zm))]
    for d in range(1,deg+1):
        for i in range(d+1):
            for j in range(d-i+1):
                l=d-i-j
                cols.append(Zm[:,0]**i*Zm[:,1]**j*Zm[:,2]**l)
    return np.column_stack(cols)
Phi3 = design((X-MU)/SD, 3)
models=[Ridge(alpha=1e-10).fit(Phi3,Y[:,k]) for k in range(3)]
G=[]
for b in np.round(np.arange(0.10,0.3001,0.001),6):
    for l in np.round(np.arange(3,4.5001,0.01),6):
        for n in [2,4,6,8,10]:
            G.append((b,l,n))
G=np.array(G)
P=np.column_stack([m.predict(design((G-MU)/SD,3)) for m in models])
for tag, lo, hi in [("fin80", Y.min(0), Y.max(0)), ("all84", lo84, hi84)]:
    S=(P-lo)/(hi-lo)
    eq=np.argmin(S.mean(1)); print("norm",tag,"eq", G[eq], P[eq].round(6), "loss", S.mean(1)[eq].round(6))
    w=[0.8,0.1,0.1]; i=np.argmin(S@w); print("  thermal", G[i], P[i].round(6))
    w=[0.1,0.8,0.1]; i=np.argmin(S@w); print("  pressure", G[i], P[i].round(6))
    w=[0.1,0.1,0.8]; i=np.argmin(S@w); print("  uniform", G[i], P[i].round(6))
    ideal=S.min(0); i=np.argmin(((S-ideal)**2).sum(1)); print("  ideal", G[i], P[i].round(6))
    wg=np.arange(0,1.0001,0.05); cand={}
    for w1 in wg:
        for w2 in wg:
            w3=1-w1-w2
            if w3<-1e-9: continue
            sc=S@np.array([w1,w2,w3]); i=int(np.argmin(sc)); cand[i]=min(cand.get(i,1e9),float(sc.min()))
    idx=sorted(cand); print("  pareto", len(idx))
    wg01=np.arange(0,1.0001,0.01); maxreg=np.zeros(len(idx))
    for w1 in wg01:
        for w2 in wg01:
            w3=1-w1-w2
            if w3<-1e-9: continue
            L=S[idx]@np.array([w1,w2,w3]); maxreg=np.maximum(maxreg, L-L.min())
    i=int(np.argmin(maxreg)); print("  minimax", G[idx[i]], P[idx[i]].round(6), "regret", round(float(maxreg.min()),6))
