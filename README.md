# 🔬 ArXiv Scout v2.0

AI论文智能侦察、深度精读与多模态输出系统。

开源替代方案，将arXiv/HuggingFace论文自动转化为：
- 📝 2000+字中文精读报告（五专家会诊）
- 🎙️ 4000字播客讲解 + TTS音频
- 📊 25-30页专业PPT（含论文截图和公式）

## 功能特色

### 🔍 智能论文发现
- **arXiv API集成**: 免费API，支持复杂查询和分类筛选
- **HuggingFace热门**: 自动获取社区热门论文和每日精选
- **多维度搜索**: 按作者、机构、研究领域、发布时间筛选

### 🧠 五专家会诊系统
每篇论文由5位AI专家从不同角度深度评审：
- 👨‍🔬 **算法专家**: 创新性、技术可行性、SOTA对比
- 👨‍💻 **工程专家**: 代码复现、计算资源、工程落地
- 🏥 **医疗机器人专家**: 医疗适用性、迁移潜力、安全性
- 💰 **商业专家**: 商业化潜力、竞争格局、创业启发
- 🎓 **学术专家**: 论文质量、引用潜力、学术影响

### 🎙️ TTS播客生成
- **4000字深度脚本**: 自然对话式技术讲解
- **edge-tts引擎**: 微软免费TTS，YunyangNeural中文声音
- **ElevenLabs备选**: 高质量多语言TTS（需API key）
- **25-30分钟音频**: 适合通勤和碎片时间学习

### 📊 专业PPT生成  
- **25-30页幻灯片**: 完整论文演示文稿
- **论文图片提取**: 自动从PDF提取关键图表
- **LaTeX公式渲染**: 数学公式清晰展示
- **模板化设计**: 统一风格，专业美观

### 🤖 多Agent并行处理
- **批量论文处理**: 同时处理多篇论文
- **智能资源调度**: 优化GPU和API调用
- **失败重试机制**: 确保高成功率

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/zhuangzard/arxiv-scout.git
cd arxiv-scout
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
# 安装edge-tts（免费TTS）
pip install edge-tts
```

### 3. 第一次运行
```bash
# 搜索机器人推理相关论文（返回10篇）
bash search-arxiv.sh "robot reasoning" 10 cs.RO

# 获取HuggingFace热门论文（最近30篇）
bash hf-trending.sh 30

# 获取特定论文摘要
bash fetch-paper.sh 2602.07885

# 生成完整报告+TTS+PPT
python3 generate-podcast.py paper_report.md output_podcast.txt
python3 generate-pptx.py paper_report.md output_slides.pptx
bash generate-audio.sh output_podcast.txt output_podcast.mp3
```

## 配置

### API Keys说明
- **arXiv API**: 完全免费，无需注册
- **HuggingFace API**: 免费公开数据，无需key
- **edge-tts**: 微软免费TTS服务，无需API key
- **ElevenLabs (可选)**: 高质量TTS，需付费API key
- **Claude/GPT (可选)**: 用于精读报告生成

### 环境变量（可选）
```bash
# 如使用ElevenLabs TTS
export ELEVENLABS_API_KEY="your_key_here"

# 如使用OpenAI/Claude增强精读
export OPENAI_API_KEY="your_key_here"
export ANTHROPIC_API_KEY="your_key_here"
```

## 使用方式

### 搜索和获取论文
```bash
# arXiv搜索（关键词 数量 分类）
bash search-arxiv.sh "medical robotics" 5 cs.AI
bash search-arxiv.sh "large language model" 10 cs.CL

# HuggingFace热门
bash hf-trending.sh 20

# 获取论文详情
bash fetch-paper.sh 2312.11805
```

### 生成多模态输出
```bash
# 生成播客脚本（4000字）
python3 generate-podcast.py paper.md podcast.txt

# 生成PPT幻灯片（25-30页）
python3 generate-pptx.py paper.md slides.pptx

# 生成音频文件（edge-tts默认）
bash generate-audio.sh podcast.txt audio.mp3
```

### 批量处理
```bash
# 批量生成（精读+TTS+PPT）
for paper in *.md; do
  base=$(basename "$paper" .md)
  python3 generate-podcast.py "$paper" "${base}_podcast.txt"
  python3 generate-pptx.py "$paper" "${base}_slides.pptx"
  bash generate-audio.sh "${base}_podcast.txt" "${base}_audio.mp3"
done
```

## 作为OpenClaw Skill使用

在OpenClaw环境中，可以通过以下触发词激活：
- `论文`、`paper`、`arxiv`
- `最新研究`、`论文推荐`
- `paper scout`

### OpenClaw命令示例
```bash
# 自动论文推荐和分析
"帮我找5篇最新的机器人推理论文"
"分析一下arXiv上关于LLM reasoning的最新进展"
"生成今天HuggingFace热门论文的播客"
```

### 定时任务
```bash
# 每日8AM自动推送（需要OpenClaw配置）
openclaw cron add "0 8 * * *" "arxiv-scout-daily"
```

## 输出示例

### 生成的文件结构
```
outputs/
├── 2024-02-16_batch/
│   ├── 00_summary.html              # 批次摘要
│   ├── 01_robotics_reasoning.md     # 精读报告
│   ├── 01_robotics_reasoning_podcast.txt  # TTS脚本
│   ├── 01_robotics_reasoning_podcast.mp3  # 音频文件
│   ├── 01_robotics_reasoning.pptx   # PPT幻灯片
│   ├── 02_llm_inference.md
│   ├── 02_llm_inference_podcast.txt
│   └── ...
```

### 精读报告样本
- **字数**: 2000+字中文深度分析
- **结构**: 背景→方法→实验→五专家评审→迁移路径
- **质量**: 必须引用论文具体内容，避免泛泛而谈

### TTS播客样本
- **时长**: 25-30分钟（4000字脚本）
- **风格**: 自然对话式，技术准确性与可听性平衡
- **语音**: edge-tts YunyangNeural中文声音

### PPT样本
- **页数**: 25-30页专业演示
- **内容**: 包含论文原图、公式、架构图
- **设计**: 统一模板，清晰易读

## 重点关注领域

1. 🤖 机器人推理/规划/操作 (cs.RO)
2. 🧠 LLM/VLM推理能力 (cs.CL, cs.AI)
3. 🏥 医疗AI/手术机器人 (Medical AI)
4. 🔧 训练方法/基础设施 (MLSys)
5. 💡 AI Agent/创新应用 (Applications)

## 贡献

欢迎提交Issue和Pull Request！

### 开发环境设置
```bash
git clone https://github.com/zhuangzard/arxiv-scout.git
cd arxiv-scout
pip install -r requirements.txt
pip install -e .
```

### 测试
```bash
# 运行基础测试
python -m pytest tests/

# 测试TTS生成
bash test/test-tts.sh
```

## License

Apache-2.0 License - 详见 [LICENSE](LICENSE) 文件

## 更新日志

详见 [CHANGELOG.md](CHANGELOG.md)

---

**ArXiv Scout v2.0** - 让AI论文阅读更高效，让知识传播更生动 🚀