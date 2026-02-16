---
name: arxiv-scout
description: 搜索arXiv和HuggingFace论文，多专家会诊分析，生成精读报告、TTS播客和PPT幻灯片。触发词：论文、paper、arxiv、最新研究、论文推荐、paper scout
---

# arxiv-scout v2.0

AI论文侦察、多专家会诊、TTS播客与PPT生成系统。

## 核心功能

1. **论文搜索与筛选** - arXiv API + HuggingFace热门
2. **深度精读报告** - 2000+字中文分析，五专家会诊
3. **TTS播客脚本** - 4000字深度技术讲解，语音播客
4. **PPT幻灯片生成** - 20-30页专业演示文稿
5. **多Agent并行处理** - 大规模论文批量处理
6. **每日自动推送** - 8AM定时输出到iCloud + Telegram

## 数据源
1. arXiv API (免费，无key)
2. HuggingFace Daily Papers API (社区热门)
3. web_search补充搜索

## 使用方式

### 搜索论文
```bash
bash SKILL_DIR/search-arxiv.sh "robot reasoning" 10 cs.RO
bash SKILL_DIR/search-arxiv.sh "medical robotics" 5 cs.AI
```

### 获取HF热门
```bash
bash SKILL_DIR/hf-trending.sh 30
```

### 获取论文全文摘要
```bash
bash SKILL_DIR/fetch-paper.sh 2602.07885
```

### 生成完整产物（精读+TTS+PPT）
```bash
# 对单篇论文生成所有产物
python3 SKILL_DIR/generate-podcast.py paper_report.md output_podcast.txt
python3 SKILL_DIR/generate-pptx.py paper_report.md output_slides.pptx
bash SKILL_DIR/generate-audio.sh output_podcast.txt output_podcast.mp3
```

## 重点领域（按优先级）
1. 🤖 机器人推理/规划/操作 (cs.RO, robotics reasoning/manipulation/planning)
2. 🧠 LLM/VLM推理能力 (reasoning, chain-of-thought, inference)
3. 🏥 医疗AI/手术机器人 (medical AI, surgical robotics)
4. 🔧 训练方法/基础设施 (efficient training, RLHF, scaling)
5. 💡 AI Agent/创新应用 (agents, novel applications)

---

# 详细功能规格

## 1. 论文精读报告（保持现有标准）

### 五专家会诊模式
对每篇值得深入的论文，5位专家从不同角度评审：

#### 👨‍🔬 算法专家
- 方法创新性评估
- 与SOTA对比
- 技术可行性

#### 👨‍💻 工程专家
- 代码复现难度
- 计算资源需求
- 工程落地可能性

#### 🏥 医疗机器人专家
- 对医疗/手术机器人的适用性
- 迁移到太森领域的潜力
- 安全性考量

#### 💰 商业专家
- 商业化潜力
- 竞争格局
- 对创业的启发

#### 🎓 学术专家
- 论文质量（写作、实验设计）
- 引用潜力
- 对后续研究的影响

### 精读报告要求
- **字数**: 每篇2000+字中文精读笔记
- **必须包含**:
  - 问题背景与动机
  - 方法详解（架构/算法/公式/训练细节）
  - 具体实验数字与结果分析
  - 学习要点与医疗机器人迁移路径
  - 团队/实验室信息
  - 原文链接与PDF下载链接
- **五专家会诊**: 必须引用论文具体内容，不能泛泛而谈
- **输出格式**: Markdown + HTML双格式

### 精读报告输出格式模板
```markdown
# 📄 {论文中文标题}
**英文标题**: {Original Title}
**arXiv链接**: https://arxiv.org/abs/{arxiv_id}
**PDF原文**: https://arxiv.org/pdf/{arxiv_id}.pdf
**发表日期**: {date}
**分类**: {category}
**作者团队**: {authors}
**实验室/机构**: {institutions}

## 🎯 核心贡献（一句话）
{一句话总结核心贡献}

## 📋 问题背景与动机
{详细描述领域现状、存在问题、为什么需要这个方法}
{具体引用论文中的motivation部分}

## 🔬 方法详解
### 整体架构
{描述整体框架，如果有架构图最好}

### 关键技术组件
#### 组件1: {技术名称}
{详细解释，包含公式推导}
{引用论文具体章节}

#### 组件2: {技术名称}
{详细解释}

### 算法流程
{逐步说明算法执行过程}
{伪代码或关键步骤}

### 训练细节
{损失函数、优化器、超参数、数据处理等}

## 📊 实验结果分析
### 数据集
{使用的数据集，规模，特点}

### 基线对比
{与哪些方法对比，具体数字}
| 方法 | 指标1 | 指标2 | 指标3 |
|------|-------|-------|-------|
| {方法名} | {数值} | {数值} | {数值} |

### 消融实验
{各个组件的贡献度分析}

### 关键发现
{实验中的重要观察和insight}

## 五专家会诊

### 👨‍🔬 算法专家评分: {X}/10
**创新性分析**: {基于论文具体技术内容的分析}
**技术优势**: {引用具体方法和实验结果}
**局限性**: {指出具体问题}
**与SOTA对比**: {基于实验数据的对比}

### 👨‍💻 工程专家评分: {X}/10
**复现难度**: {基于代码和实现细节的评估}
**计算复杂度**: {具体的时间/空间复杂度分析}
**工程可行性**: {实际部署的考虑}
**硬件需求**: {GPU内存、计算资源等}

### 🏥 医疗机器人专家评分: {X}/10
**医疗适用性**: {如何应用到医疗场景}
**手术机器人迁移**: {具体的迁移方案}
**安全性考量**: {医疗应用的安全要求}
**临床价值**: {对医疗实践的潜在影响}

### 💰 商业专家评分: {X}/10
**市场潜力**: {商业化前景}
**竞争优势**: {与现有方案的差异}
**成本效益**: {实施成本分析}
**创业机会**: {基于这个技术的创业方向}

### 🎓 学术专家评分: {X}/10
**研究质量**: {实验设计、写作质量}
**贡献显著性**: {对学术界的贡献}
**引用潜力**: {预测引用情况}
**后续研究**: {可能的延续方向}

## 📈 综合评分: {X}/10

## 💡 核心学习要点
1. {要点1}
2. {要点2}
3. {要点3}

## 🤖 医疗机器人迁移路径
### 直接应用场景
{具体的医疗机器人应用场景}

### 技术迁移方案
{如何改造和适配}

### 实施步骤
1. {步骤1}
2. {步骤2}
3. {步骤3}

## 🎯 推荐行动
- **优先级**: {高/中/低}
- **建议**: {精读/泛读/跳过/立即复现}
- **时间投入**: {建议的学习时间}
- **下一步**: {具体的行动建议}

---
**报告生成时间**: {datetime}
**分析agent**: Claude-4
```

---

## 2. TTS播客脚本生成（新功能）

### 播客脚本要求
- **字数**: 约4000字中文播客式讲解文稿
- **风格**: 像资深研究者在给同行做深度技术分享，不是念摘要
- **语调**: 自然对话式，有节奏感，适合语音播放
- **深度**: 技术细节充分，但用口语化方式表达

### 播客脚本内容结构
1. **开场引入** (300字)
   - 热情的开场白
   - 今天要分享的论文简介
   - 为什么这篇论文值得关注

2. **背景动机** (500字)
   - 领域现状和痛点
   - 现有方法的局限性
   - 这个研究想解决什么问题

3. **核心方法详解** (2000字)
   - 整体思路和创新点
   - 关键技术组件逐个讲解
   - 数学公式用口语化描述
   - 算法流程step by step

4. **实验结果分析** (600字)
   - 关键实验数据
   - 与baseline对比的具体数字
   - 消融实验的发现
   - 性能提升的原因分析

5. **医疗机器人启发** (400字)
   - 如何应用到手术机器人
   - 具体的迁移思路
   - 潜在的技术难点

6. **总结和takeaways** (200字)
   - 核心收获
   - 对未来研究的影响
   - 值得关注的后续方向

### 数学公式口语化规则
- `θ_merged = Σ α_i × θ_i` → "theta merged等于求和alpha i乘以theta i"
- `L = L_task + λL_reg` → "损失函数L等于任务损失加上lambda倍的正则化损失"
- `Attention(Q,K,V) = softmax(QK^T/√d_k)V` → "注意力机制是Q乘以K转置，除以根号d_k，然后softmax，最后乘以V"

### 播客脚本输出格式
```
# {论文简短标题} - 深度技术播客脚本

大家好，欢迎来到今天的AI论文深度解读。我是你们的主播，今天要和大家分享一篇非常有意思的论文...

[4000字播客脚本内容]

...好的，今天的分享就到这里。这篇论文给我们展示了...希望对大家有启发。下次再见！

---
脚本字数: ~4000字
适合语音时长: 约25-30分钟
生成时间: {datetime}
```

### 语音生成指令
```bash
# 使用edge-tts生成MP3（默认），sag作为备选
edge-tts -t "$(cat {script_file}.txt)" -v YunyangNeural -f mp3 --write-media {output_file}.mp3
# 或使用sag CLI（需ElevenLabs API key）
# sag speak -f {script_file}.txt -o {output_file}.mp3 --no-play --lang zh --model-id eleven_multilingual_v2
```

### 文件命名规则
- 播客脚本: `{paper_short_name}_podcast.txt`
- 语音文件: `{paper_short_name}_podcast.mp3`

---

## 3. PPT幻灯片生成（新功能）

### PPT生成要求
- **使用库**: python-pptx
- **背景色**: **浅色背景**（白色#FFFFFF或浅灰#F8F9FA，绝对不要黑色！）
- **页数**: 每篇论文20-30页
- **图片**: 必须包含从论文PDF提取的figure，或架构图URL

### 配色方案（固定）
- **背景色**: 白色 #FFFFFF 或浅灰 #F8F9FA
- **标题色**: 深蓝 #1B3A5C
- **正文色**: 深灰 #333333
- **强调色**: 橙色 #E67E22
- **辅助色**: 浅蓝 #3498DB

### 字体规格
- **标题**: 28pt 粗体
- **正文**: 18pt 常规
- **注释**: 14pt
- **中文字体**: 苹方/微软雅黑
- **英文字体**: Helvetica/Calibri

### PPT结构模板（20-30页）

#### 1. 封面页（1页）
- 论文标题（中英文）
- 作者团队和机构
- arXiv链接和发表日期
- 一句话核心贡献
- "AI论文深度解读"副标题

#### 2. 问题背景（2-3页）
- 页面2: 领域现状与挑战
- 页面3: 现有方法的局限性
- 页面4: 本研究的动机

#### 3. 核心方法（8-12页）
- 页面5: 整体架构概览（含架构图）
- 页面6-7: 关键技术组件1（原理+公式）
- 页面8-9: 关键技术组件2
- 页面10-11: 算法流程与伪代码
- 页面12: 训练策略与细节
- 页面13-14: 创新点总结

#### 4. 实验结果（3-5页）
- 页面15: 实验设置与数据集
- 页面16: 基线对比结果表格
- 页面17: 消融实验分析
- 页面18: 关键性能指标可视化
- 页面19: 实验发现与insights

#### 5. 医疗机器人迁移（2-3页）
- 页面20: 医疗应用场景分析
- 页面21: 手术机器人迁移方案
- 页面22: 技术适配与挑战

#### 6. 关键Takeaways（1页）
- 页面23: 核心学习要点（3-5条）

#### 7. 行动清单（1页）
- 页面24: 后续研究方向
- 页面25: 实施建议
- 页面26: 参考资源链接

#### 8. 结尾页（1页）
- 页面27: 感谢观看，讨论与交流

### PPT内容要求
- **每页必须有标题和详细内容**，不是只有几个bullet points
- **解释性文字**: 每个概念都要有充分解释，不假设观众背景
- **图表丰富**: 尽可能多的视觉元素（流程图、表格、对比图）
- **公式展示**: 重要公式单独成页，配有文字解释
- **实际案例**: 具体的数字、实验结果、对比数据

### 图片处理
- **论文figure提取**: 从PDF中提取关键图表
- **架构图**: 如果有URL直接引用，否则用文字描述
- **自制图表**: 用python-pptx绘制简单流程图
- **图片位置**: 标题下方，配文字解释

### 文件命名
- PPT文件: `{paper_short_name}_slides.pptx`

### PPT生成示例代码结构
```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

# 创建演示文稿，使用浅色主题
prs = Presentation()

# 设置配色
title_color = RGBColor(27, 58, 92)  # 深蓝 #1B3A5C
text_color = RGBColor(51, 51, 51)   # 深灰 #333333
accent_color = RGBColor(230, 126, 34)  # 橙色 #E67E22

# 封面页
slide1 = prs.slides.add_slide(prs.slide_layouts[0])
slide1.shapes.title.text = "论文标题"
# ... 更多页面
```

---

## 4. 多Agent工作流

### 触发场景
当需要处理多篇论文（N > 1）时，自动启用多Agent并行处理模式。

### 工作流程
```
主Agent (Coordinator)
    ├── 搜索和筛选论文 (3-5篇)
    ├── 为每篇论文启动Sub-Agent
    ├── 监控Sub-Agent进度
    ├── 汇总所有结果
    └── 生成总结报告

Sub-Agent-1 (Paper 1)          Sub-Agent-2 (Paper 2)          Sub-Agent-N (Paper N)
    ├── 获取论文详情                ├── 获取论文详情                ├── 获取论文详情
    ├── 生成精读报告                ├── 生成精读报告                ├── 生成精读报告
    ├── 生成播客脚本                ├── 生成播客脚本                ├── 生成播客脚本
    ├── 生成PPT幻灯片              ├── 生成PPT幻灯片              ├── 生成PPT幻灯片
    ├── 生成语音文件                ├── 生成语音文件                ├── 生成语音文件
    └── 返回完成状态                └── 返回完成状态                └── 返回完成状态
```

### Sub-Agent任务规格
每个Sub-Agent负责一篇论文的完整处理流程：

1. **论文信息获取**
   - 使用 `fetch-paper.sh` 获取详细摘要
   - 下载PDF原文（如果可能）
   - 解析元数据（作者、日期、分类）

2. **精读报告生成**
   - 按照精读报告模板生成2000+字分析
   - 五专家会诊模式
   - 输出Markdown和HTML格式

3. **播客脚本生成**
   - 调用 `generate-podcast.py`
   - 生成4000字播客脚本
   - 保存为txt文件

4. **PPT生成**
   - 调用 `generate-pptx.py`
   - 生成20-30页幻灯片
   - 保存为pptx文件

5. **语音生成**
   - 调用 `generate-audio.sh`
   - 使用edge-tts生成MP3（默认），sag作为备选
   - 保存语音文件

6. **文件整理**
   - 按照标准目录结构组织文件
   - 生成单篇论文的完整报告

### Sub-Agent启动命令
```bash
# 主Agent使用sessions_spawn启动Sub-Agent
# 传递参数：arxiv_id, paper_title, output_directory
sessions_spawn "paper-processor-{arxiv_id}" "
处理单篇论文: {paper_title}
arxiv_id: {arxiv_id}
输出目录: {output_dir}
执行完整流程: 精读报告 + TTS脚本 + PPT + 语音
"
```

### 进度监控
主Agent定期检查Sub-Agent状态：
```bash
# 检查所有子任务进度
sessions_list | grep "paper-processor"
# 获取具体子任务结果
sessions_result {session_id}
```

### 结果汇总
所有Sub-Agent完成后，主Agent生成：
1. **总结报告** (`00_summary.html`)
2. **今日精选** (`00_今日总结.md`)
3. **推送清单** (Telegram消息 + 文件)

---

## 5. 每日Cron自动化

### Cron触发时间
- **时间**: 每天上午8:00 AM EST
- **频率**: 每日一次
- **标识**: paper-daily-scout-v2

### 完整工作流程
```
08:00 AM EST 触发
    ↓
1. 搜索当日热门论文
   - HuggingFace Daily Papers (top 50)
   - arXiv最新提交 (cs.AI, cs.RO, cs.LG)
   - 结合搜索热门关键词
    ↓
2. 智能筛选论文 (3-5篇)
   - 按重点领域优先级排序
   - 排除已处理的论文
   - 确保质量和多样性
    ↓
3. 多Agent并行处理
   - 为每篇论文启动Sub-Agent
   - 并行生成精读+TTS+PPT
   - 监控处理进度
    ↓
4. 文件整理与保存
   - 创建日期目录
   - 保存到iCloud同步文件夹
   - 生成汇总报告
    ↓
5. Telegram推送
   - 发送HTML总结报告
   - 推送PDF原文
   - 发送MP3语音文件
   - 发送PPT幻灯片
    ↓
完成，等待下一日
```

### iCloud保存路径
```
~/Library/Mobile Documents/com~apple~CloudDocs/Documents/OpenClaw/论文/daily/YYYY-MM-DD/
├── 00_summary.html          # 今日总结报告
├── 00_今日总结.md
├── 01_{name}.md              # 第一篇论文精读报告
├── 01_{name}.html            # HTML版本
├── 01_{name}_podcast.txt     # TTS播客脚本(~4000字)
├── 01_{name}_podcast.mp3     # 语音文件
├── 01_{name}_slides.pptx     # PPT幻灯片
├── {arxiv_id}.pdf            # 原文PDF
├── 02_{name}.md              # 第二篇论文...
├── 02_{name}.html
├── 02_{name}_podcast.txt
├── 02_{name}_podcast.mp3
├── 02_{name}_slides.pptx
├── {arxiv_id2}.pdf
└── ...                      # 更多论文
```

### Telegram推送内容
1. **总结消息**: HTML格式的当日论文总结
2. **PDF文件**: 所有论文的PDF原文
3. **语音文件**: 所有播客MP3文件
4. **PPT文件**: 所有幻灯片文件
5. **链接汇总**: arXiv链接、iCloud文件夹链接

### 推送命令示例
```bash
# 发送HTML总结
message action=send target=telegram filePath="00_summary.html"

# 发送PDF原文
for pdf in *.pdf; do
    message action=send target=telegram filePath="$pdf"
done

# 发送语音文件
for mp3 in *_podcast.mp3; do
    message action=send target=telegram filePath="$mp3" caption="🎧 播客音频"
done

# 发送PPT文件
for pptx in *_slides.pptx; do
    message action=send target=telegram filePath="$pptx" caption="📊 演示文稿"
done
```

### Cron Payload详细内容
```
任务：每日AI论文深度分析 v2.0

时间：每天8:00 AM EST
目标：搜索3-5篇最新热门论文，生成精读报告+TTS播客+PPT幻灯片

执行流程：
1. 搜索论文源
   - HuggingFace Daily Papers API (top 50，按upvotes排序)
   - arXiv最新提交 (cs.AI, cs.RO, cs.LG, cs.CL 过去24小时)
   - 重点关键词: robot reasoning, medical AI, surgical robotics, LLM reasoning, multimodal, agent

2. 智能筛选标准 (筛选出3-5篇)
   - 优先级1: 医疗机器人/手术机器人相关
   - 优先级2: 机器人推理、规划、操作
   - 优先级3: LLM/VLM推理能力提升
   - 优先级4: 创新训练方法或AI Agent
   - 排除: 纯理论数学、无关领域、质量过低
   - 去重: 检查是否已处理过（基于标题相似度）

3. 多Agent并行处理
   为每篇选中论文启动一个Sub-Agent，执行：
   - fetch论文详情和PDF
   - 生成2000+字精读报告（五专家会诊）
   - 生成4000字播客脚本（深度技术讲解）
   - 生成20-30页PPT幻灯片（浅色背景）
   - 生成MP3语音文件（edge-tts默认）
   - 保存所有格式文件

4. 文件保存
   输出目录：~/Library/Mobile Documents/com~apple~CloudDocs/Documents/OpenClaw/论文/daily/$(date +%Y-%m-%d)/
   
   文件结构：
   ├── 00_summary.html          # 今日总结
   ├── 00_今日总结.md
   ├── 01_{short_name}.md        # 精读报告
   ├── 01_{short_name}.html      # HTML版本  
   ├── 01_{short_name}_podcast.txt  # 播客脚本
   ├── 01_{short_name}_podcast.mp3  # 语音文件
   ├── 01_{short_name}_slides.pptx  # PPT幻灯片
   ├── {arxiv_id}.pdf               # 原文PDF
   └── ... (其他论文文件)

5. Telegram推送
   - 发送今日总结HTML报告
   - 逐个推送PDF原文 (caption: 📄 论文原文)  
   - 逐个推送MP3音频 (caption: 🎧 播客讲解)
   - 逐个推送PPT文件 (caption: 📊 演示文稿)
   - 最后发送iCloud文件夹链接

6. 完成标志
   在Telegram发送：✅ 今日论文分析完成 - 共处理X篇论文，生成完整分析+播客+PPT

错误处理：
- 如果某个Sub-Agent失败，跳过该论文继续处理其他
- 如果所有Sub-Agent都失败，发送错误报告到Telegram  
- 如果搜索到的论文少于3篇，降低筛选标准重新搜索

必须使用技能：arxiv-scout v2.0
所需工具：search-arxiv.sh, hf-trending.sh, fetch-paper.sh, generate-podcast.py, generate-pptx.py, generate-audio.sh
```

---

## 6. 核心脚本规格

### 6.1 generate-podcast.py
**功能**: 播客脚本生成辅助工具（4000字播客文稿主要由agent用LLM生成）

**输入**: Markdown格式的精读报告
**输出**: 4000字中文播客脚本（.txt格式）

**说明**: 
- 这个脚本是辅助工具，真正的4000字播客文稿由agent用LLM生成
- 脚本可用于格式检查和后处理
- LLM生成的播客文稿更自然、更有深度
- 脚本主要用于标准化输出格式和质量控制

**脚本特点**:
- 解析精读报告的结构化内容
- 转换为口语化的播客风格  
- 数学公式口语化处理
- 添加播客特有的过渡语言
- 保持技术深度但增加可听性

### 6.2 generate-pptx.py  
**功能**: 将精读报告转换为专业PPT幻灯片

**输入**: Markdown格式的精读报告
**输出**: 20-30页PPT幻灯片（.pptx格式）

**脚本特点**:
- 使用python-pptx库
- 浅色背景主题（白色/浅灰）
- 固定配色方案（蓝白+橙强调）
- 自动布局和美化
- 包含图表和公式展示
- 结构化内容分页

### 6.3 generate-audio.sh
**功能**: 调用edge-tts生成高质量中文语音（默认），sag作为备选

**输入**: 播客脚本文本文件
**输出**: MP3音频文件

**核心命令**:
```bash
# edge-tts（默认，免费）
edge-tts -t "$(cat input.txt)" -v YunyangNeural -f mp3 --write-media output.mp3

# sag CLI（备选，需API key）  
# sag speak -f input.txt -o output.mp3 --no-play --lang zh --model-id eleven_multilingual_v2
```

**脚本特点**:
- 错误处理和重试机制
- 音频质量检查
- 文件大小和时长验证
- 支持批量处理

---

## 7. 质量标准

### 精读报告质量要求
- **深度**: 不能是简单的摘要翻译，必须有深入的技术分析
- **具体**: 引用具体的实验数据、公式推导、架构细节
- **实用**: 五专家会诊必须结合实际应用场景
- **原创**: 不能照搬论文原文，要有自己的理解和见解

### TTS播客质量要求
- **自然流畅**: 语言符合中文播客习惯，有节奏感
- **技术准确**: 专业术语使用正确，公式转换准确
- **易懂性**: 复杂概念有充分解释和类比
- **完整性**: 覆盖论文的核心内容，不遗漏重点

### PPT幻灯片质量要求
- **视觉统一**: 严格按照配色方案，字体一致
- **内容丰富**: 每页都有substantial内容，不是空洞的bullet points
- **逻辑清晰**: 页面之间有明确的逻辑关系和过渡
- **专业美观**: 适合学术演讲和技术分享使用

### 音频质量要求
- **语音自然**: 使用高质量TTS模型，发音准确
- **语速适中**: 便于理解技术内容
- **无错误**: 没有明显的发音错误或停顿异常
- **时长合理**: 4000字脚本对应25-30分钟音频

---

## 8. 错误处理与容错

### 常见错误场景
1. **论文获取失败**: arXiv链接失效或PDF无法下载
2. **API限制**: HuggingFace API请求频率限制
3. **TTS生成失败**: edge-tts/sag CLI调用失败或音频质量异常
4. **PPT生成错误**: python-pptx库异常或图片处理失败
5. **文件系统问题**: iCloud同步异常或磁盘空间不足

### 容错机制
1. **重试机制**: 关键操作失败后自动重试3次
2. **降级方案**: TTS失败时只生成文本脚本，PPT失败时生成简化版本
3. **部分成功**: 即使部分环节失败，也保证已完成部分的输出
4. **错误日志**: 详细记录错误信息，便于后续排查
5. **通知机制**: 严重错误时发送Telegram通知

### 质量检查
1. **文件完整性**: 检查生成文件的大小和格式
2. **内容质量**: 验证字数、页数等关键指标
3. **格式正确性**: 确保Markdown、HTML、PPT格式正确
4. **链接有效性**: 验证arXiv链接和PDF下载链接

---

## 9. 使用示例

### 单篇论文处理
```bash
# 1. 搜索论文
bash search-arxiv.sh "surgical robotics" 5 cs.RO

# 2. 选择感兴趣的论文ID，获取详情
bash fetch-paper.sh 2402.12345

# 3. 人工生成精读报告（按模板）
# ... 完成 2402.12345.md 精读报告

# 4. 生成播客脚本
python3 generate-podcast.py 2402.12345.md 2402.12345_podcast.txt

# 5. 生成PPT幻灯片  
python3 generate-pptx.py 2402.12345.md 2402.12345_slides.pptx

# 6. 生成语音文件
bash generate-audio.sh 2402.12345_podcast.txt 2402.12345_podcast.mp3

# 7. 转换HTML格式
python3 -c "
import markdown
with open('2402.12345.md', 'r') as f:
    md_content = f.read()
html_content = markdown.markdown(md_content, extensions=['tables'])
with open('2402.12345.html', 'w') as f:
    f.write(html_content)
"
```

### 多论文批量处理
```bash
# 使用多Agent模式处理当日热门论文
# （这通常由主Agent协调，用户不直接调用）

# 主Agent启动流程
sessions_spawn "daily-paper-scout" "
执行每日论文分析任务：
1. 搜索HuggingFace和arXiv热门论文
2. 筛选3-5篇高质量论文  
3. 为每篇论文启动Sub-Agent处理
4. 汇总结果并推送到Telegram
使用skill: arxiv-scout v2.0
"
```

### Cron自动化配置
```bash
# 设置每日8AM的Cron任务
# （通过OpenClaw的cron系统，而不是系统cron）
# 具体配置见上面的Cron Payload部分
```

---

## 总结

arxiv-scout v2.0 是一个功能全面的AI论文分析系统，提供从搜索到最终产物的完整工作流：

✅ **论文发现**: arXiv + HuggingFace双源搜索  
✅ **深度分析**: 2000+字五专家会诊精读报告  
✅ **语音讲解**: 4000字播客脚本 + 高质量TTS音频  
✅ **视觉展示**: 20-30页专业PPT幻灯片  
✅ **并行处理**: 多Agent协同工作，提升效率  
✅ **自动化**: 每日定时运行，智能推送  
✅ **多格式输出**: Markdown、HTML、TXT、MP3、PPTX  
✅ **云端同步**: iCloud自动保存，随时随地访问  

适用场景：
- 🏥 医疗机器人技术跟踪
- 🤖 机器人和AI领域研究
- 📚 学术研究和技术学习  
- 📺 技术分享和演讲准备
- 🚀 创业项目的技术调研

通过多模态输出（文本+语音+视觉），满足不同学习偏好和使用场景的需求。