# 歧管式微通道芯片热管理系统优化

针对高热流密度芯片歧管式微通道热管理系统的数学建模论文与配套代码（CUMCM 风格 B 题）。

## 内容

```
├── paper/          论文 LaTeX 源码（XeLaTeX，真实数学公式，公式编号 (1)–(53)）
│   ├── paper.tex
│   ├── appendix-coef.tex   附录 A 系数表（由代码生成）
│   └── figs/               论文插图（图 2–图 9）
├── code/           Python 计算与绘图代码（可完整复现论文全部数值与图表）
│   ├── scripts/    01_analyze.py / 02_figures.py / 03_equations.py / 04_build_docx.py
│   ├── data/       附件 2 原始数据
│   ├── figs/       论文插图
│   ├── eqs/        公式 PNG（Word 版用）
│   └── report.json 全部关键数值
└── 歧管式微通道芯片热管理系统_修订稿_LaTeX.pdf   成品 PDF（19 页）
```

## 编译论文（XeLaTeX）

依赖：完整的 TeX 发行版（含 ctex/xeCJK，TeX Live 或 MiKTeX 默认自带）+ SimSun、SimHei、KaiTi、Times New Roman 字体。

```bash
cd paper
xelatex paper.tex
xelatex paper.tex    # 跑两遍刷新交叉引用
```

> 若本机 MiKTeX 缺少中文宏包，可临时使用本工作区未提交的 `latex_src/texmf`（xeCJK 3.8.9 等，第三方宏包，不入库）。

## 复现计算与图表

```bash
cd code
pip install numpy pandas scikit-learn matplotlib openpyxl python-docx
python scripts/01_analyze.py     # 全部计算 -> report.json
python scripts/02_figures.py     # 论文插图
python scripts/03_equations.py   # 公式 PNG
python scripts/04_build_docx.py  # Word 版论文
```

关键设定（与论文附录 B 一致）：三次响应面 + Ridge（α=10⁻¹⁰）；5 次重复 5 折交叉验证（种子 6）；84 组样本极值归一化；Pareto 候选权重步长 0.05（115 个方案）；后悔值权重步长 0.01；蒙特卡洛每方案 100000 次抽样（种子 31）。

## 主要结论

- 等权综合推荐：β = 0.220，λ = 4.50，N = 4
- 偏好鲁棒方案（最小最大后悔）：β = 0.226，λ = 4.50，N = 6，最大后悔值 0.270865
- 三次响应面范围归一化 RMSE：0.000666% / 0.459% / 0.420%
