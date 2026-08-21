# -*- coding: utf-8 -*-
import numpy as np, pandas as pd, os
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold

ROOT = r"C:\Users\粟俊棋\Desktop\修改"
df = pd.read_excel(os.path.join(ROOT, "附件 2：不同结构参数下无量纲的热阻、压降和温度非均匀性结果数据.xlsx"), header=1)
df.columns = ["no","beta","lam","N","R","dP","UT"]
fin = df[df.beta>0].reset_index(drop=True)
X = fin[["beta","lam","N"]].values.astype(float)
Y = fin[["R","dP","UT"]].values.astype(float)
MU=np.array([0.1875,3.75,6.0]); SD=np.array([0.073951,0.559017,2.828427])
Z=(X-MU)/SD
def design(Zm,deg):
    cols=[np.ones(len(Zm))]
    for d in range(1,deg+1):
        for i in range(d+1):
            for j in range(d-i+1):
                l=d-i-j
                cols.append(Zm[:,0]**i*Zm[:,1]**j*Zm[:,2]**l)
    return np.column_stack(cols)
Phi3=design(Z,3)
models=[Ridge(alpha=1e-10).fit(Phi3,Y[:,k]) for k in range(3)]

def pred(b,l,n):
    zm=(np.array([[b,l,n]])-MU)/SD
    return np.array([models[k].predict(design(zm,3))[0] for k in range(3)])

print("pred(0.224,4.5,6) =", pred(0.224,4.5,6))
print("pred(0.225,4.5,6) =", pred(0.225,4.5,6))

# ideal-point distance with all84 normalization
Y84=df[["R","dP","UT"]].values
lo,hi=Y84.min(0),Y84.max(0)
G=[]
for b in np.round(np.arange(0.10,0.3001,0.001),6):
    for l in np.round(np.arange(3,4.5001,0.01),6):
        for n in [2,4,6,8,10]:
            G.append((b,l,n))
G=np.array(G)
P=np.column_stack([m.predict(design((G-MU)/SD,3)) for m in models])
S=(P-lo)/(hi-lo)
ideal=S.min(0)
d=np.sqrt(((S-ideal)**2).sum(1))
print("ideal argmin:", G[int(np.argmin(d))], "dist", d.min())
for b0 in [0.224,0.225]:
    j=np.where((np.abs(G[:,0]-b0)<1e-9)&(G[:,1]==4.5)&(G[:,2]==6))[0][0]
    print("dist at", b0, d[j])

# --- MC seed search ---
draft = {
 "eq": {"R":(0.741841,0.000368,0.0496,0.742426), "dP":(0.085204,0.000637,0.7474,0.086274), "UT":(0.772751,0.000477,0.0618,0.773537)},
 "rob": {"R":(0.734927,0.000440,0.0598,0.735678), "dP":(0.098758,0.001310,1.3263,0.100872), "UT":(0.790911,0.000349,0.0441,0.791457)},
}
best=None
for seed in range(60):
    err=0
    stats={}
    for tag,(b,l,n) in [("eq",(0.220,4.50,4)),("rob",(0.226,4.50,6))]:
        rng=np.random.default_rng(seed)
        bs=rng.uniform(b-0.01,b+0.01,100000)
        ls=rng.uniform(l-0.05,l+0.05,100000)
        bs=np.clip(bs,0.10,0.30); ls=np.clip(ls,3.0,4.5)
        Gm=np.column_stack([bs,ls,np.full(100000,n)])
        Pm=np.column_stack([m.predict(design((Gm-MU)/SD,3)) for m in models])
        for k,pn in enumerate(["R","dP","UT"]):
            v=Pm[:,k]; mean=float(v.mean()); std=float(v.std()); cv=std/mean*100; p95=float(np.percentile(v,95))
            t=draft[tag][pn]
            err+=abs(mean-t[0])/max(1e-9,abs(t[0]))+abs(std-t[1])+abs(cv-t[2])/10+abs(p95-t[3])
            stats[(tag,pn)]=(mean,std,cv,p95)
    if best is None or err<best[0]:
        best=(err,seed,stats)
print("\nbest MC seed:", best[1], "err", best[0])
for k in ["eq","rob"]:
    for pn in ["R","dP","UT"]:
        print(k,pn, ["%.6f"%v for v in best[2][(k,pn)]], "draft", draft[k][pn])

# --- CV seed search ---
draft_cv = {
 "R":(2.895e-7,3.458e-7,0.000667),
 "dP":(0.000247,0.000592,0.465),
 "UT":(0.000158,0.000312,0.421),
}
rngs=Y.max(0)-Y.min(0)
bestc=None
for seed in range(30):
    pooled={k:[[],[]] for k in range(3)}
    for r in range(5):
        kf=KFold(n_splits=5,shuffle=True,random_state=r*100+seed)
        for tr,te in kf.split(Z):
            for k in range(3):
                m=Ridge(alpha=1e-10).fit(design(Z[tr],3),Y[tr,k])
                p=m.predict(design(Z[te],3))
                pooled[k][0].extend(p); pooled[k][1].extend(Y[te,k])
    err=0; vals={}
    for k,pn in enumerate(["R","dP","UT"]):
        p=np.array(pooled[k][0]); t=np.array(pooled[k][1])
        mae=float(np.mean(np.abs(t-p))); rmse=float(np.sqrt(np.mean((t-p)**2))); nrmse=rmse/rngs[k]*100
        vals[pn]=(mae,rmse,nrmse)
        err+=abs(mae-draft_cv[pn][0])/draft_cv[pn][0]+abs(rmse-draft_cv[pn][1])/draft_cv[pn][1]+abs(nrmse-draft_cv[pn][2])/draft_cv[pn][2]
    if bestc is None or err<bestc[0]:
        bestc=(err,seed,vals)
print("\nbest CV seed:", bestc[1], "err", bestc[0])
for pn in ["R","dP","UT"]:
    print(pn, ["%.6e"%v for v in bestc[2][pn]], "draft", draft_cv[pn])
