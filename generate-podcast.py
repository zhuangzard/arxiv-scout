#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate-podcast.py - 将论文精读报告转换为播客脚本

功能：
- 解析Markdown格式的精读报告
- 转换为4000字左右的中文播客脚本  
- 数学公式口语化处理
- 添加播客特有的过渡语言和节奏
- 保持技术深度但增加可听性

使用方法：
python3 generate-podcast.py input_report.md output_script.txt

作者：太森的AI助手二丫
版本：v2.0
"""

import sys
import re
import os
from datetime import datetime

class PodcastGenerator:
    def __init__(self):
        # 数学公式口语化映射规则
        self.formula_patterns = {
            r'θ_(\w+)': r'theta_\1',
            r'α_(\w+)': r'alpha_\1',  
            r'β_(\w+)': r'beta_\1',
            r'λ': r'lambda',
            r'Σ': r'求和',
            r'∫': r'积分',
            r'∂': r'偏导数',
            r'∇': r'梯度',
            r'≈': r'约等于',
            r'≤': r'小于等于',
            r'≥': r'大于等于',
            r'∈': r'属于',
            r'×': r'乘以',
            r'÷': r'除以',
            r'\^T': r'的转置',
            r'\^(-?\d+)': r'的\1次方',
            r'sqrt\(([^)]+)\)': r'根号\1',
            r'log\(([^)]+)\)': r'\1的对数',
            r'exp\(([^)]+)\)': r'e的\1次方',
            r'softmax': r'softmax函数',
        }
        
        # 播客过渡语句
        self.transitions = {
            'intro': [
                "大家好，欢迎来到今天的AI论文深度解读。我是你们的主播，",
                "今天要和大家分享一篇非常有意思的论文。",
                "这篇论文来自",
                "让我们一起来看看这个工作到底有什么创新之处。"
            ],
            'background': [
                "首先，我们来了解一下这个研究的背景。",
                "在讲具体方法之前，我需要先给大家介绍一下现在这个领域的情况。",
                "为什么要做这个研究呢？"
            ],
            'method': [
                "接下来我们进入今天的重点——这篇论文的核心方法。",
                "现在让我来详细解释一下他们是怎么做的。",
                "这里的创新点非常有意思，",
                "让我们逐个来看这些关键技术。"
            ],
            'experiment': [
                "说完方法，我们来看看实验结果。",
                "数据是最有说服力的，让我们来看看具体的数字。",
                "这些实验结果告诉我们什么呢？"
            ],
            'medical': [
                "作为专注于医疗机器人的研究者，我特别关注这个工作对我们领域的启发。",
                "这个技术如何应用到手术机器人上呢？",
                "从医疗应用的角度来看，"
            ],
            'conclusion': [
                "好的，让我们来总结一下今天的内容。",
                "这篇论文给我们带来了哪些启发呢？",
                "总的来说，"
            ]
        }

    def parse_markdown_report(self, content):
        """解析Markdown格式的精读报告"""
        sections = {}
        current_section = None
        current_content = []
        
        lines = content.split('\n')
        for line in lines:
            # 检测一级标题
            if line.startswith('# '):
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = 'title'
                current_content = [line[2:].strip()]
            # 检测二级标题
            elif line.startswith('## '):
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                section_name = line[3:].strip()
                current_section = self._normalize_section_name(section_name)
                current_content = []
            else:
                current_content.append(line)
        
        # 保存最后一个section
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections

    def _normalize_section_name(self, section):
        """标准化section名称"""
        section_map = {
            '核心贡献': 'contribution',
            '问题背景与动机': 'background', 
            '方法详解': 'method',
            '实验结果分析': 'experiment',
            '医疗机器人迁移路径': 'medical',
            '核心学习要点': 'takeaways',
            '推荐行动': 'action'
        }
        
        for key, value in section_map.items():
            if key in section:
                return value
        return 'other'

    def formula_to_speech(self, text):
        """将数学公式转换为口语化描述"""
        for pattern, replacement in self.formula_patterns.items():
            text = re.sub(pattern, replacement, text)
        
        # 处理复杂公式结构
        # 例如：θ_merged = Σ α_i × θ_i
        text = re.sub(r'([a-zA-Z_]+)\s*=\s*(.+)', r'\1等于\2', text)
        text = re.sub(r'([a-zA-Z_]+)\(([^)]+)\)', r'\1函数，输入是\2', text)
        
        return text

    def clean_markdown_format(self, text):
        """清理Markdown格式标记"""
        # 移除markdown格式
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # 粗体
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # 斜体  
        text = re.sub(r'`([^`]+)`', r'\1', text)        # 代码
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # 链接
        text = re.sub(r'^\s*[-*+]\s*', '', text, flags=re.MULTILINE)  # 列表项
        text = re.sub(r'^\s*\d+\.\s*', '', text, flags=re.MULTILINE)  # 数字列表
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)  # 标题标记
        text = re.sub(r'\n\s*\n', '\n\n', text)  # 多余空行
        
        return text.strip()

    def generate_intro(self, sections):
        """生成播客开场白"""
        title = sections.get('title', '今天要分享的论文')
        title = self.clean_markdown_format(title)
        
        intro_parts = [
            "大家好，欢迎来到今天的AI论文深度解读。我是你们的主播，",
            f"今天要和大家分享一篇非常有意思的论文，标题是《{title}》。",
            "这篇论文刚刚在arXiv上发表，我觉得它有一些很创新的地方，值得我们深入讨论一下。",
            "在人工智能快速发展的今天，每天都有大量的论文发表，但能真正引起我注意的并不多。",
            "这篇论文就是其中之一，让我们一起来看看它到底有什么特别之处。"
        ]
        
        return '\n\n'.join(intro_parts)

    def generate_background(self, sections):
        """生成背景介绍部分"""
        background_content = sections.get('background', '')
        if not background_content:
            return ""
        
        background_content = self.clean_markdown_format(background_content)
        background_content = self.formula_to_speech(background_content)
        
        intro = "首先，我们来了解一下这个研究的背景。为什么研究者要做这个工作呢？"
        
        # 将背景内容转换为口语化
        sentences = background_content.split('。')
        spoken_sentences = []
        
        for sentence in sentences:
            if sentence.strip():
                sentence = sentence.strip() + '。'
                # 添加一些口语化的连接词
                if len(spoken_sentences) > 0:
                    connectors = ['另外，', '同时，', '而且，', '更重要的是，', '这就意味着']
                    if len(spoken_sentences) % 3 == 0:
                        sentence = connectors[len(spoken_sentences) % len(connectors)] + sentence
                spoken_sentences.append(sentence)
        
        content = intro + '\n\n' + '\n\n'.join(spoken_sentences)
        
        transition = "\n\n了解了背景之后，现在让我们看看研究者们是如何解决这些问题的。"
        
        return content + transition

    def generate_method(self, sections):
        """生成方法讲解部分"""
        method_content = sections.get('method', '')
        if not method_content:
            return ""
        
        method_content = self.clean_markdown_format(method_content)
        method_content = self.formula_to_speech(method_content)
        
        intro = "接下来我们进入今天的重点——这篇论文的核心方法。这里的创新点非常有意思，让我逐个来给大家解释。"
        
        # 分解方法内容，添加详细解释
        paragraphs = method_content.split('\n\n')
        spoken_paragraphs = []
        
        for i, para in enumerate(paragraphs):
            if para.strip():
                para = para.strip()
                
                # 为每个段落添加引导语
                if '架构' in para or '框架' in para:
                    para = "先说说整体架构。" + para
                elif '算法' in para or '流程' in para:
                    para = "然后我们看看具体的算法流程。" + para
                elif '训练' in para or '优化' in para:
                    para = "在训练方面，" + para
                elif '损失函数' in para or '目标函数' in para:
                    para = "关于损失函数的设计，" + para
                
                # 添加技术解释的过渡语
                if i > 0 and i % 2 == 0:
                    transitions = [
                        "这里需要特别注意的是，",
                        "换句话说，",
                        "让我再详细解释一下，", 
                        "这个技术的关键在于，"
                    ]
                    para = transitions[i % len(transitions)] + para
                
                spoken_paragraphs.append(para)
        
        content = intro + '\n\n' + '\n\n'.join(spoken_paragraphs)
        
        transition = "\n\n说完了核心方法，大家可能会问，这个方法效果到底怎么样？让我们来看看实验数据。"
        
        return content + transition

    def generate_experiment(self, sections):
        """生成实验结果讲解"""
        experiment_content = sections.get('experiment', '')
        if not experiment_content:
            return ""
        
        experiment_content = self.clean_markdown_format(experiment_content)
        experiment_content = self.formula_to_speech(experiment_content)
        
        intro = "说完方法，我们来看看实验结果。数据是最有说服力的，让我们来看看具体的数字。"
        
        # 处理实验数据，让数字更口语化
        content = experiment_content
        
        # 将百分号转换
        content = re.sub(r'(\d+\.?\d*)%', r'百分之\1', content)
        
        # 处理倍数
        content = re.sub(r'(\d+\.?\d*)倍', r'\1倍', content)
        
        # 处理精度数值
        content = re.sub(r'(\d+\.?\d*)', r'\1', content)
        
        paragraphs = content.split('\n\n')
        spoken_paragraphs = []
        
        for para in paragraphs:
            if para.strip():
                para = para.strip()
                
                # 为数据分析添加解释语句
                if '对比' in para or '比较' in para:
                    para = "我们来看对比实验的结果。" + para
                elif '消融' in para:
                    para = "消融实验的结果很有意思。" + para  
                elif '数据集' in para:
                    para = "在数据集的选择上，" + para
                
                spoken_paragraphs.append(para)
        
        content = intro + '\n\n' + '\n\n'.join(spoken_paragraphs)
        
        # 添加结果解读
        conclusion = "\n\n从这些实验结果可以看出，这个方法确实带来了显著的性能提升。更重要的是，它证明了我们之前讲的那些技术创新是有效的。"
        
        return content + conclusion

    def generate_medical_application(self, sections):
        """生成医疗机器人应用讲解"""
        medical_content = sections.get('medical', '')
        if not medical_content:
            # 如果没有专门的医疗部分，生成通用的医疗应用分析
            return self._generate_generic_medical_analysis()
        
        medical_content = self.clean_markdown_format(medical_content)
        
        intro = "作为专注于医疗机器人的研究者，我特别关注这个工作对我们领域的启发。让我来分析一下这个技术如何应用到手术机器人上。"
        
        content = intro + '\n\n' + medical_content
        
        transition = "\n\n可以看出，这个技术在医疗机器人领域有很大的应用潜力。当然，从研究到实际临床应用还有很长的路要走，但这个方向是值得投入的。"
        
        return content + transition

    def _generate_generic_medical_analysis(self):
        """生成通用的医疗应用分析"""
        return """作为专注于医疗机器人的研究者，我特别关注这个工作对我们领域的启发。

虽然这篇论文没有直接针对医疗应用，但我认为其核心技术可以很好地迁移到手术机器人上。特别是在机器人的感知和决策能力方面，这个工作提供了新的思路。

在手术机器人的应用场景中，我们需要机器人能够准确理解手术环境，做出精确的操作决策。这篇论文提出的方法，在提升AI系统的推理和判断能力方面，与我们的需求高度契合。

当然，从研究到实际临床应用还有很长的路要走，包括安全性验证、监管审批等等。但这个方向确实值得我们深入研究。"""

    def generate_conclusion(self, sections):
        """生成总结部分"""
        takeaways = sections.get('takeaways', '')
        action = sections.get('action', '')
        
        intro = "好的，让我们来总结一下今天的内容。这篇论文给我们带来了哪些启发呢？"
        
        summary_points = []
        
        # 从takeaways中提取要点
        if takeaways:
            takeaways_clean = self.clean_markdown_format(takeaways)
            points = takeaways_clean.split('\n')
            for point in points:
                if point.strip() and not point.startswith('#'):
                    summary_points.append(point.strip())
        
        # 如果没有现成的takeaways，生成通用总结
        if not summary_points:
            summary_points = [
                "这篇论文在方法创新上确实有其独特之处",
                "实验结果证明了方法的有效性", 
                "对我们的研究工作有一定的参考价值",
                "在医疗机器人应用方面也有很好的潜力"
            ]
        
        # 构建总结内容
        summary_content = "总的来说，" + "。同时，".join(summary_points) + "。"
        
        # 添加行动建议
        if action:
            action_clean = self.clean_markdown_format(action)
            action_part = f"\n\n对于我们后续的研究工作，{action_clean}"
        else:
            action_part = "\n\n我建议大家可以深入阅读一下这篇论文的原文，特别是技术细节部分。如果你们在相关领域做研究，这个工作可能会给你们一些新的灵感。"
        
        ending = "\n\n好的，今天的分享就到这里。希望这篇论文的解读对大家有所帮助。我们下期再见！"
        
        return intro + '\n\n' + summary_content + action_part + ending

    def generate_podcast_script(self, sections):
        """生成完整的播客脚本"""
        script_parts = []
        
        # 1. 开场白
        intro = self.generate_intro(sections)
        script_parts.append(intro)
        
        # 2. 背景介绍
        background = self.generate_background(sections)
        if background:
            script_parts.append(background)
        
        # 3. 方法讲解
        method = self.generate_method(sections)
        if method:
            script_parts.append(method)
        
        # 4. 实验结果
        experiment = self.generate_experiment(sections)
        if experiment:
            script_parts.append(experiment)
        
        # 5. 医疗应用
        medical = self.generate_medical_application(sections)
        if medical:
            script_parts.append(medical)
        
        # 6. 总结
        conclusion = self.generate_conclusion(sections)
        script_parts.append(conclusion)
        
        # 组合完整脚本
        full_script = '\n\n---\n\n'.join(script_parts)
        
        # 添加元信息
        word_count = len(full_script)
        estimated_duration = word_count // 160  # 中文语音大约160字/分钟
        
        header = f"""# {sections.get('title', '论文播客脚本')} - 深度技术播客脚本

脚本字数: ~{word_count}字
预计时长: 约{estimated_duration}-{estimated_duration+5}分钟
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
风格: 深度技术讲解，播客对话式

---

"""
        
        return header + full_script

def main():
    if len(sys.argv) != 3:
        print("使用方法: python3 generate-podcast.py input_report.md output_script.txt")
        print("示例: python3 generate-podcast.py paper_analysis.md podcast_script.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"错误：输入文件 {input_file} 不存在")
        sys.exit(1)
    
    try:
        # 读取输入文件
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 生成播客脚本
        generator = PodcastGenerator()
        sections = generator.parse_markdown_report(content)
        podcast_script = generator.generate_podcast_script(sections)
        
        # 写入输出文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(podcast_script)
        
        word_count = len(podcast_script)
        print(f"✅ 播客脚本生成完成！")
        print(f"📝 输出文件: {output_file}")
        print(f"📊 脚本字数: {word_count}字")
        print(f"🎙️ 预计时长: {word_count//160}-{word_count//160+5}分钟")
        
        if word_count < 3000:
            print("⚠️  警告：脚本字数偏少，建议检查输入报告的完整性")
        elif word_count > 5000:
            print("⚠️  警告：脚本字数偏多，可能需要压缩内容")
    
    except Exception as e:
        print(f"❌ 生成播客脚本时出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()