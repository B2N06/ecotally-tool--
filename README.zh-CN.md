# EcoTally

[English](README.md) · [方法与公式](METHODOLOGY.md) ·
[参与贡献](CONTRIBUTING.md)

EcoTally 是一个轻量、透明、可复现的开源群落生态学工具。它读取物种丰度
数据，生成 α、β、γ 多样性、采样完整度、稀释曲线、功能多样性和数据质量
报告。核心功能只依赖 Python 标准库，便于审计计算过程和长期保存工作流。

## 快速开始

长表数据包含 `site,species,abundance` 三列：

```csv
site,species,abundance
forest,oak,12
forest,fern,7
marsh,reed,20
```

运行分析：

```shell
python -m pip install -e .
python -m ecotally examples/observations.csv
python -m ecotally examples/observations.csv --format markdown -o report.md
```

EcoTally 会自动识别长表和“每行一个样方、每列一个物种”的宽表。

## 常用分析

```shell
# Bootstrap 置信区间
python -m ecotally examples/observations.csv --bootstrap 999 --format json

# 稀释曲线
python -m ecotally examples/observations.csv --rarefaction 20 --format json

# Hill 多样性谱
python -m ecotally examples/observations.csv --hill-orders 0,0.5,1,2,3 \
  --format markdown

# 功能性状分析；不同单位的性状先标准化
python -m ecotally examples/observations.csv --traits examples/traits.csv \
  --standardize-traits --format markdown

# 输出可用于 R、GIS 或聚类的距离矩阵
python -m ecotally examples/observations.csv --format matrix \
  --metric bray_curtis

# 生成无额外绘图库依赖的矢量图
python -m ecotally examples/observations.csv --format svg -o diversity.svg

# 导出完整 JSON、清单和各报告分区 CSV
python -m ecotally examples/observations.csv --format bundle -o analysis
```

## 结果解释

- 丰富度只计算丰度大于零的物种。
- Shannon 指数使用自然对数。
- Simpson 多样性为 `1 - Σp²`，逆 Simpson 为 `1 / Σp²`。
- Jaccard 和 Sørensen 使用出现/未出现数据；Bray–Curtis 使用丰度。
- Chao1、稀释和 Bootstrap 要求非负整数个体数。
- 功能距离使用欧氏距离；性状单位不同时建议启用标准化。
- 报告会标注空样方、全零物种和严重采样不平衡。
- 报告包含 Berger–Parker 优势度以及可直接绘图的等级–丰度数据。

完整定义、公式和边界条件见 [METHODOLOGY.md](METHODOLOGY.md)。

## 可复现性

JSON 和 Markdown 报告包含 EcoTally 版本、运行参数、输入文件名和 SHA-256
哈希。相同数据与参数会产生相同的 Bootstrap 结果。

## 开源与引用

项目采用 MIT 许可证。研究中使用时请引用仓库中的 `CITATION.cff`。
贡献流程见 [CONTRIBUTING.md](CONTRIBUTING.md)。
