#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate-pptx.py - 将论文精读报告转换为专业PPT幻灯片

功能：
- 解析Markdown格式的精读报告
- 生成20-30页专业PPT幻灯片
- 浅色背景主题（白色/浅灰）
- 固定配色方案（蓝白+橙强调）
- 结构化内容分页，包含图表和公式

使用方法：
python3 generate-pptx.py input_report.md output_slides.pptx

依赖：pip3 install python-pptx

作者：太森的AI助手二丫
版本：v2.0
"""

import sys
import re
import os
from datetime import datetime
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

class PPTGenerator:
    def __init__(self):
        # 配色方案
        self.colors = {
            'background': RGBColor(255, 255, 255),      # 白色 #FFFFFF
            'title': RGBColor(27, 58, 92),              # 深蓝 #1B3A5C
            'text': RGBColor(51, 51, 51),               # 深灰 #333333
            'accent': RGBColor(230, 126, 34),           # 橙色 #E67E22
            'secondary': RGBColor(52, 152, 219),        # 浅蓝 #3498DB
            'light_gray': RGBColor(248, 249, 250)       # 浅灰 #F8F9FA
        }
        
        # 字体大小
        self.font_sizes = {
            'title': Pt(28),
            'subtitle': Pt(24),
            'heading': Pt(20),
            'text': Pt(18),
            'caption': Pt(14),
            'small': Pt(12)
        }
        
        # 创建演示文稿
        self.prs = Presentation()
        self._setup_slide_master()

    def _setup_slide_master(self):
        """设置幻灯片母版样式"""
        # 设置幻灯片尺寸为16:9
        self.prs.slide_width = Inches(13.33)
        self.prs.slide_height = Inches(7.5)

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
            '五专家会诊': 'experts',
            '综合评分': 'score',
            '核心学习要点': 'takeaways',
            '医疗机器人迁移路径': 'medical',
            '推荐行动': 'action'
        }
        
        for key, value in section_map.items():
            if key in section:
                return value
        return 'other'

    def clean_markdown_format(self, text):
        """清理Markdown格式标记"""
        # 保留一些格式信息用于PPT处理
        text = re.sub(r'\*\*([^*]+)\*\*', r'【粗体】\1【/粗体】', text)  # 标记粗体
        text = re.sub(r'\*([^*]+)\*', r'【斜体】\1【/斜体】', text)      # 标记斜体
        text = re.sub(r'`([^`]+)`', r'【代码】\1【/代码】', text)        # 标记代码
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1', text)  # 移除链接但保留文字
        text = re.sub(r'^\s*[-*+]\s*', '• ', text, flags=re.MULTILINE)  # 转换列表项
        text = re.sub(r'^\s*(\d+)\.\s*', r'\1. ', text, flags=re.MULTILINE)  # 保留数字列表
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)  # 移除标题标记
        text = re.sub(r'\n\s*\n+', '\n\n', text)  # 规范化空行
        
        return text.strip()

    def extract_paper_info(self, sections):
        """从sections中提取论文基本信息"""
        info = {
            'title_cn': '',
            'title_en': '',
            'authors': '',
            'institutions': '',
            'arxiv_link': '',
            'date': '',
            'category': '',
            'contribution': ''
        }
        
        title_section = sections.get('title', '')
        if title_section:
            lines = title_section.split('\n')
            for line in lines:
                if 'arxiv.org/abs/' in line.lower():
                    match = re.search(r'https?://arxiv\.org/abs/([^)\s]+)', line)
                    if match:
                        info['arxiv_link'] = f"https://arxiv.org/abs/{match.group(1)}"
                elif '英文标题' in line:
                    info['title_en'] = line.split(':', 1)[1].strip() if ':' in line else ''
                elif '作者团队' in line:
                    info['authors'] = line.split(':', 1)[1].strip() if ':' in line else ''
                elif '实验室' in line or '机构' in line:
                    info['institutions'] = line.split(':', 1)[1].strip() if ':' in line else ''
                elif '发表日期' in line:
                    info['date'] = line.split(':', 1)[1].strip() if ':' in line else ''
                elif '分类' in line:
                    info['category'] = line.split(':', 1)[1].strip() if ':' in line else ''
                else:
                    if not info['title_cn']:
                        info['title_cn'] = line.strip()
        
        # 获取核心贡献
        contribution = sections.get('contribution', '')
        if contribution:
            info['contribution'] = self.clean_markdown_format(contribution)[:200] + '...' if len(contribution) > 200 else self.clean_markdown_format(contribution)
        
        return info

    def add_title_slide(self, paper_info):
        """添加封面页"""
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])  # 空白布局
        
        # 设置背景色
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = self.colors['background']
        
        # 主标题
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(1), Inches(12.33), Inches(1.5))
        title_frame = title_box.text_frame
        title_frame.text = paper_info['title_cn'] or '论文深度解读'
        
        title_para = title_frame.paragraphs[0]
        title_para.alignment = PP_ALIGN.CENTER
        title_run = title_para.runs[0]
        title_run.font.size = self.font_sizes['title']
        title_run.font.color.rgb = self.colors['title']
        title_run.font.bold = True
        
        # 英文标题
        if paper_info['title_en']:
            en_title_box = slide.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(12.33), Inches(1))
            en_title_frame = en_title_box.text_frame
            en_title_frame.text = paper_info['title_en']
            
            en_para = en_title_frame.paragraphs[0]
            en_para.alignment = PP_ALIGN.CENTER
            en_run = en_para.runs[0]
            en_run.font.size = self.font_sizes['subtitle']
            en_run.font.color.rgb = self.colors['text']
        
        # 作者和机构信息
        info_y = 3.5
        if paper_info['authors']:
            author_box = slide.shapes.add_textbox(Inches(0.5), Inches(info_y), Inches(12.33), Inches(0.5))
            author_frame = author_box.text_frame
            author_frame.text = f"作者：{paper_info['authors']}"
            author_para = author_frame.paragraphs[0]
            author_para.alignment = PP_ALIGN.CENTER
            author_run = author_para.runs[0]
            author_run.font.size = self.font_sizes['text']
            author_run.font.color.rgb = self.colors['text']
            info_y += 0.5
        
        if paper_info['institutions']:
            inst_box = slide.shapes.add_textbox(Inches(0.5), Inches(info_y), Inches(12.33), Inches(0.5))
            inst_frame = inst_box.text_frame
            inst_frame.text = f"机构：{paper_info['institutions']}"
            inst_para = inst_frame.paragraphs[0]
            inst_para.alignment = PP_ALIGN.CENTER
            inst_run = inst_para.runs[0]
            inst_run.font.size = self.font_sizes['text']
            inst_run.font.color.rgb = self.colors['text']
            info_y += 0.5
        
        # arXiv链接
        if paper_info['arxiv_link']:
            link_box = slide.shapes.add_textbox(Inches(0.5), Inches(info_y), Inches(12.33), Inches(0.5))
            link_frame = link_box.text_frame
            link_frame.text = paper_info['arxiv_link']
            link_para = link_frame.paragraphs[0]
            link_para.alignment = PP_ALIGN.CENTER
            link_run = link_para.runs[0]
            link_run.font.size = self.font_sizes['text']
            link_run.font.color.rgb = self.colors['secondary']
            info_y += 0.7
        
        # 核心贡献
        if paper_info['contribution']:
            contrib_box = slide.shapes.add_textbox(Inches(1), Inches(info_y), Inches(11.33), Inches(1.5))
            contrib_frame = contrib_box.text_frame
            contrib_frame.text = f"核心贡献：{paper_info['contribution']}"
            contrib_para = contrib_frame.paragraphs[0]
            contrib_para.alignment = PP_ALIGN.CENTER
            contrib_run = contrib_para.runs[0]
            contrib_run.font.size = self.font_sizes['text']
            contrib_run.font.color.rgb = self.colors['accent']
        
        # 底部标识
        footer_box = slide.shapes.add_textbox(Inches(0.5), Inches(6.5), Inches(12.33), Inches(0.5))
        footer_frame = footer_box.text_frame
        footer_frame.text = f"AI论文深度解读 | {datetime.now().strftime('%Y-%m-%d')}"
        footer_para = footer_frame.paragraphs[0]
        footer_para.alignment = PP_ALIGN.CENTER
        footer_run = footer_para.runs[0]
        footer_run.font.size = self.font_sizes['caption']
        footer_run.font.color.rgb = self.colors['text']

    def add_content_slide(self, title, content, slide_type='normal'):
        """添加内容页"""
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])  # 空白布局
        
        # 设置背景色
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = self.colors['background']
        
        # 标题
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12.33), Inches(0.8))
        title_frame = title_box.text_frame
        title_frame.text = title
        
        title_para = title_frame.paragraphs[0]
        title_para.alignment = PP_ALIGN.LEFT
        title_run = title_para.runs[0]
        title_run.font.size = self.font_sizes['subtitle']
        title_run.font.color.rgb = self.colors['title']
        title_run.font.bold = True
        
        # 添加装饰线
        line = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, 
            Inches(0.5), Inches(1.0), 
            Inches(12.33), Inches(0.05)
        )
        line.fill.solid()
        line.fill.fore_color.rgb = self.colors['accent']
        line.line.color.rgb = self.colors['accent']
        
        # 内容区域
        content_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.3), Inches(12.33), Inches(5.7))
        content_frame = content_box.text_frame
        content_frame.word_wrap = True
        
        # 处理不同类型的内容
        if slide_type == 'bullet_list':
            self._add_bullet_content(content_frame, content)
        elif slide_type == 'two_column':
            self._add_two_column_content(slide, content, 1.3)
        else:
            self._add_normal_content(content_frame, content)

    def _add_normal_content(self, text_frame, content):
        """添加普通文本内容"""
        paragraphs = content.split('\n\n')
        
        for i, para in enumerate(paragraphs):
            if para.strip():
                if i > 0:
                    # 添加新段落
                    p = text_frame.add_paragraph()
                else:
                    p = text_frame.paragraphs[0]
                
                # 处理格式标记
                self._format_paragraph(p, para.strip())

    def _add_bullet_content(self, text_frame, content):
        """添加项目符号内容"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if line.strip():
                if i > 0:
                    p = text_frame.add_paragraph()
                else:
                    p = text_frame.paragraphs[0]
                
                # 设置项目符号
                if line.strip().startswith('•') or line.strip().startswith('-'):
                    p.level = 0
                    text = line.strip()[1:].strip()
                elif line.strip().startswith('  •') or line.strip().startswith('  -'):
                    p.level = 1
                    text = line.strip()[3:].strip()
                else:
                    p.level = 0
                    text = line.strip()
                
                self._format_paragraph(p, text)

    def _add_two_column_content(self, slide, content, start_y):
        """添加两栏内容"""
        parts = content.split('\n---\n')  # 用---分隔两栏
        
        # 左栏
        left_box = slide.shapes.add_textbox(Inches(0.5), Inches(start_y), Inches(6), Inches(5.7))
        left_frame = left_box.text_frame
        left_frame.word_wrap = True
        if len(parts) > 0:
            self._add_normal_content(left_frame, parts[0])
        
        # 右栏
        right_box = slide.shapes.add_textbox(Inches(6.8), Inches(start_y), Inches(6), Inches(5.7))
        right_frame = right_box.text_frame
        right_frame.word_wrap = True
        if len(parts) > 1:
            self._add_normal_content(right_frame, parts[1])

    def _format_paragraph(self, paragraph, text):
        """格式化段落文本"""
        # 处理格式标记
        parts = re.split(r'【(粗体|斜体|代码)】([^【]*)【/\1】', text)
        
        if len(parts) == 1:
            # 没有特殊格式
            paragraph.text = text
            run = paragraph.runs[0]
            run.font.size = self.font_sizes['text']
            run.font.color.rgb = self.colors['text']
        else:
            # 有特殊格式
            paragraph.text = ""  # 清空
            i = 0
            while i < len(parts):
                if i % 3 == 0:
                    # 普通文本
                    if parts[i]:
                        run = paragraph.runs.add()
                        run.text = parts[i]
                        run.font.size = self.font_sizes['text']
                        run.font.color.rgb = self.colors['text']
                elif i % 3 == 1:
                    # 格式类型
                    format_type = parts[i]
                    if i + 1 < len(parts):
                        formatted_text = parts[i + 1]
                        run = paragraph.runs.add()
                        run.text = formatted_text
                        run.font.size = self.font_sizes['text']
                        
                        if format_type == '粗体':
                            run.font.bold = True
                            run.font.color.rgb = self.colors['title']
                        elif format_type == '斜体':
                            run.font.italic = True
                            run.font.color.rgb = self.colors['secondary']
                        elif format_type == '代码':
                            run.font.color.rgb = self.colors['accent']
                i += 1

    def add_background_slides(self, sections):
        """添加问题背景页面"""
        background_content = sections.get('background', '')
        if not background_content:
            return
        
        content = self.clean_markdown_format(background_content)
        
        # 分割内容为多个页面
        paragraphs = content.split('\n\n')
        current_page_content = []
        page_count = 0
        
        for para in paragraphs:
            if para.strip():
                current_page_content.append(para.strip())
                
                # 每页大约2-3个段落
                if len(current_page_content) >= 2 and len('\n\n'.join(current_page_content)) > 800:
                    page_count += 1
                    if page_count == 1:
                        title = "问题背景与动机"
                    else:
                        title = f"问题背景与动机 ({page_count})"
                    
                    page_content = '\n\n'.join(current_page_content)
                    self.add_content_slide(title, page_content)
                    current_page_content = []
        
        # 处理剩余内容
        if current_page_content:
            page_count += 1
            if page_count == 1:
                title = "问题背景与动机"
            else:
                title = f"问题背景与动机 ({page_count})"
            
            page_content = '\n\n'.join(current_page_content)
            self.add_content_slide(title, page_content)

    def add_method_slides(self, sections):
        """添加核心方法页面"""
        method_content = sections.get('method', '')
        if not method_content:
            return
        
        content = self.clean_markdown_format(method_content)
        
        # 检测子sections（通过###标题）
        subsections = re.split(r'\n### ([^\n]+)\n', content)
        
        if len(subsections) > 1:
            # 有子sections，每个子section一页
            self.add_content_slide("核心方法概览", subsections[0])
            
            for i in range(1, len(subsections), 2):
                if i + 1 < len(subsections):
                    subsection_title = f"核心方法：{subsections[i]}"
                    subsection_content = subsections[i + 1]
                    self.add_content_slide(subsection_title, subsection_content)
        else:
            # 没有子sections，按段落分页
            paragraphs = content.split('\n\n')
            current_page_content = []
            page_count = 0
            
            for para in paragraphs:
                if para.strip():
                    current_page_content.append(para.strip())
                    
                    # 每页控制内容长度
                    if len('\n\n'.join(current_page_content)) > 1000:
                        page_count += 1
                        if page_count == 1:
                            title = "核心方法"
                        else:
                            title = f"核心方法 ({page_count})"
                        
                        page_content = '\n\n'.join(current_page_content)
                        self.add_content_slide(title, page_content)
                        current_page_content = []
            
            # 处理剩余内容
            if current_page_content:
                page_count += 1
                if page_count == 1:
                    title = "核心方法"
                else:
                    title = f"核心方法 ({page_count})"
                
                page_content = '\n\n'.join(current_page_content)
                self.add_content_slide(title, page_content)

    def add_experiment_slides(self, sections):
        """添加实验结果页面"""
        experiment_content = sections.get('experiment', '')
        if not experiment_content:
            return
        
        content = self.clean_markdown_format(experiment_content)
        
        # 尝试识别表格数据
        if '|' in content:
            # 包含表格，特殊处理
            parts = content.split('\n\n')
            table_parts = []
            text_parts = []
            
            for part in parts:
                if '|' in part and part.count('|') > 3:
                    table_parts.append(part)
                else:
                    text_parts.append(part)
            
            # 文字内容页
            if text_parts:
                text_content = '\n\n'.join(text_parts)
                self.add_content_slide("实验设置与分析", text_content)
            
            # 表格数据页
            if table_parts:
                table_content = '\n\n'.join(table_parts)
                self.add_content_slide("实验结果数据", table_content, 'two_column')
        else:
            # 普通文本，按段落分页
            paragraphs = content.split('\n\n')
            current_page_content = []
            page_count = 0
            
            for para in paragraphs:
                if para.strip():
                    current_page_content.append(para.strip())
                    
                    if len('\n\n'.join(current_page_content)) > 900:
                        page_count += 1
                        if page_count == 1:
                            title = "实验结果分析"
                        else:
                            title = f"实验结果分析 ({page_count})"
                        
                        page_content = '\n\n'.join(current_page_content)
                        self.add_content_slide(title, page_content)
                        current_page_content = []
            
            # 处理剩余内容
            if current_page_content:
                page_count += 1
                if page_count == 1:
                    title = "实验结果分析"
                else:
                    title = f"实验结果分析 ({page_count})"
                
                page_content = '\n\n'.join(current_page_content)
                self.add_content_slide(title, page_content)

    def add_expert_slides(self, sections):
        """添加五专家会诊页面"""
        experts_content = sections.get('experts', '')
        if not experts_content:
            return
        
        content = self.clean_markdown_format(experts_content)
        
        # 识别五个专家的评价
        expert_sections = re.split(r'### ([^#\n]+专家评分[^#\n]*)', content)
        
        if len(expert_sections) > 1:
            # 每个专家一页
            for i in range(1, len(expert_sections), 2):
                if i + 1 < len(expert_sections):
                    expert_title = expert_sections[i].strip()
                    expert_content = expert_sections[i + 1].strip()
                    
                    # 清理标题格式
                    clean_title = re.sub(r'评分[：:]\s*\d+/10', '', expert_title)
                    
                    self.add_content_slide(clean_title, expert_content)
        else:
            # 没有明确分段，直接作为一页
            self.add_content_slide("专家会诊评价", content)

    def add_medical_slides(self, sections):
        """添加医疗机器人迁移页面"""
        medical_content = sections.get('medical', '')
        if not medical_content:
            return
        
        content = self.clean_markdown_format(medical_content)
        
        # 分为应用场景和迁移方案
        if len(content) > 1200:
            parts = content.split('\n\n')
            mid = len(parts) // 2
            
            part1 = '\n\n'.join(parts[:mid])
            part2 = '\n\n'.join(parts[mid:])
            
            self.add_content_slide("医疗机器人应用场景", part1)
            self.add_content_slide("技术迁移方案与挑战", part2)
        else:
            self.add_content_slide("医疗机器人迁移路径", content)

    def add_takeaways_slide(self, sections):
        """添加关键要点页面"""
        takeaways_content = sections.get('takeaways', '')
        if not takeaways_content:
            return
        
        content = self.clean_markdown_format(takeaways_content)
        
        # 转换为项目符号格式
        lines = content.split('\n')
        bullet_content = []
        
        for line in lines:
            if line.strip() and not line.startswith('#'):
                if not line.startswith('•') and not line.startswith('-'):
                    bullet_content.append(f"• {line.strip()}")
                else:
                    bullet_content.append(line.strip())
        
        formatted_content = '\n'.join(bullet_content)
        self.add_content_slide("核心学习要点", formatted_content, 'bullet_list')

    def add_action_slide(self, sections):
        """添加行动建议页面"""
        action_content = sections.get('action', '')
        if not action_content:
            # 生成通用行动建议
            action_content = """• 深入阅读论文原文，特别关注技术细节部分

• 查看作者团队的其他相关工作

• 尝试复现核心实验结果

• 思考如何将技术应用到自己的研究领域

• 关注后续相关工作的发展"""
        
        content = self.clean_markdown_format(action_content)
        
        # 确保是项目符号格式
        if '•' not in content:
            lines = content.split('\n')
            bullet_lines = []
            for line in lines:
                if line.strip():
                    bullet_lines.append(f"• {line.strip()}")
            content = '\n'.join(bullet_lines)
        
        self.add_content_slide("推荐行动清单", content, 'bullet_list')

    def add_conclusion_slide(self):
        """添加结尾页"""
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        
        # 设置背景色
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = self.colors['light_gray']
        
        # 感谢文字
        thanks_box = slide.shapes.add_textbox(Inches(2), Inches(2.5), Inches(9.33), Inches(2))
        thanks_frame = thanks_box.text_frame
        thanks_frame.text = "感谢观看\n\n欢迎讨论与交流"
        
        for para in thanks_frame.paragraphs:
            para.alignment = PP_ALIGN.CENTER
            for run in para.runs:
                run.font.size = self.font_sizes['title']
                run.font.color.rgb = self.colors['title']
                run.font.bold = True
        
        # 底部信息
        footer_box = slide.shapes.add_textbox(Inches(2), Inches(5.5), Inches(9.33), Inches(1))
        footer_frame = footer_box.text_frame
        footer_frame.text = f"AI论文深度解读 | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        footer_para = footer_frame.paragraphs[0]
        footer_para.alignment = PP_ALIGN.CENTER
        footer_run = footer_para.runs[0]
        footer_run.font.size = self.font_sizes['text']
        footer_run.font.color.rgb = self.colors['text']

    def generate_pptx(self, sections):
        """生成完整的PPT"""
        # 提取论文信息
        paper_info = self.extract_paper_info(sections)
        
        # 1. 封面页
        self.add_title_slide(paper_info)
        
        # 2. 问题背景（2-3页）
        self.add_background_slides(sections)
        
        # 3. 核心方法（8-12页）
        self.add_method_slides(sections)
        
        # 4. 实验结果（3-5页）
        self.add_experiment_slides(sections)
        
        # 5. 专家会诊（5页）
        self.add_expert_slides(sections)
        
        # 6. 医疗机器人迁移（2-3页）
        self.add_medical_slides(sections)
        
        # 7. 关键要点（1页）
        self.add_takeaways_slide(sections)
        
        # 8. 行动清单（1页）
        self.add_action_slide(sections)
        
        # 9. 结尾页
        self.add_conclusion_slide()
        
        return self.prs

def main():
    if len(sys.argv) != 3:
        print("使用方法: python3 generate-pptx.py input_report.md output_slides.pptx")
        print("示例: python3 generate-pptx.py paper_analysis.md presentation.pptx")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"错误：输入文件 {input_file} 不存在")
        sys.exit(1)
    
    try:
        # 检查python-pptx是否安装
        from pptx import Presentation
    except ImportError:
        print("错误：未安装python-pptx库")
        print("请运行: pip3 install python-pptx")
        sys.exit(1)
    
    try:
        # 读取输入文件
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 生成PPT
        generator = PPTGenerator()
        sections = generator.parse_markdown_report(content)
        prs = generator.generate_pptx(sections)
        
        # 保存PPT
        prs.save(output_file)
        
        slide_count = len(prs.slides)
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        
        print(f"✅ PPT幻灯片生成完成！")
        print(f"📊 输出文件: {output_file}")
        print(f"📄 幻灯片数量: {slide_count}页")
        print(f"💾 文件大小: {file_size:.2f}MB")
        print(f"🎨 主题: 浅色背景，蓝白配色")
        
        if slide_count < 15:
            print("⚠️  警告：幻灯片数量偏少，建议检查输入报告的完整性")
        elif slide_count > 35:
            print("⚠️  提醒：幻灯片数量较多，可能需要考虑内容精简")
    
    except Exception as e:
        print(f"❌ 生成PPT时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()