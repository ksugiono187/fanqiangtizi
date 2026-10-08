# 翻墙梯子 · fanqiangtizi.wiki

包含150篇博客文章、29个品牌档案、29个测评记录页、3类严选专题与11个知识合集，全部输出为独立静态HTML。无需数据库或付费依赖。

## 文件与维护

- `data/brands.json`：站主提供的29个品牌顺序、推广链接与11个优惠码。
- `data/source-site-data.json`：站主授权旧博客的公开原始资料快照。
- `data/brand-catalog.json`：保留价格、流量、来源日期、争议和分析的品牌资料。
- `data/topics.tsv`：121篇知识指南的主题与专属段落。
- `data/articles.json`：150篇文章目录。
- `data/reviews.json`：实测数据位置。当前全部为待测，不含虚构性能数值。
- `assets/`：样式、动态背景、交互和图标。
- `tools/`：页面生成与检查工具。
- `dist/`：可直接部署的完整网站。
- `validation-report.json`：自动检查结果。

使用 Python 3.12 或更高版本：

```sh
python tools/build.py
python tools/check.py
python -m http.server 4173 --directory dist
```

然后访问 http://localhost:4173。不能直接双击HTML预览，因为网站内部链接以域名根路径组织。

## 数据口径

读取旧博客日期：2026-10-08；原套餐日期保留在每一行。历史价格没有升级为当前订单已验证售价。原资料归属争议、容量差异与运营状态疑点都保留。优惠码以当前结算页为准。

机场推荐榜按站主给出的前十顺序。便宜榜仅比较明确月额度的无归属争议月付档位，不折算年付、不扣未验证优惠。稳定专题包含十个待测候选，目前没有实际稳定性排名。

## 域名与发布

仓库为 https://github.com/ksugiono187/fanqiangtizi 。已提供GitHub Pages自动发布工作流。仓库 Settings → Pages 的 Source 应选择 GitHub Actions，Custom domain 为 fanqiangtizi.wiki。

在域名DNS管理中按GitHub官方说明配置域名，并等待HTTPS证书签发。详见 `发布与维护说明.md`。域名配置完成前，本地文件不能证明该域名已上线。

每页有独立title、description、keywords、canonical、Open Graph和结构化数据。提供XML/HTML sitemap、RSS及robots.txt。关键词围绕“梯子推荐”“机场推荐”，收录和排名由搜索引擎决定，不能保证位置。
