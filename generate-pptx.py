#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate-pptx.py v4.0 - 论文精读报告 → 专业PPT
二丫亲自重写，解决文字溢出/空白页/不换行问题

用法: python3 generate-pptx.py report.md output.pptx [--pdf paper.pdf]
依赖: pip3 install python-pptx PyMuPDF matplotlib Pillow
"""

import sys, os, re, argparse
from datetime import datetime
from io import BytesIO

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Optional deps
try:
    import fitz  # PyMuPDF
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams['font.family'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

# ── 颜色方案 ──
C_TITLE    = RGBColor(27, 58, 92)    # #1B3A5C
C_TEXT     = RGBColor(51, 51, 51)    # #333333
C_ACCENT   = RGBColor(230, 126, 34)  # #E67E22
C_BLUE     = RGBColor(52, 152, 219)  # #3498DB
C_WHITE    = RGBColor(255, 255, 255)
C_LGRAY    = RGBColor(245, 245, 245)
C_MGRAY    = RGBColor(180, 180, 180)

# ── 布局常量 (16:9, inches) ──
SLIDE_W = 13.33
SLIDE_H = 7.5
MARGIN  = 0.7
TITLE_H = 0.7
LINE_Y  = 1.15
BODY_TOP = 1.35
BODY_W  = SLIDE_W - 2 * MARGIN
BODY_H  = SLIDE_H - BODY_TOP - 0.4  # leave bottom margin
BODY_W_WITH_IMG = 7.5  # when image on right
IMG_LEFT = 8.5
IMG_W    = 4.0

# Font sizes
F_COVER_TITLE = Pt(32)
F_COVER_SUB   = Pt(20)
F_SLIDE_TITLE = Pt(24)
F_BODY        = Pt(14)
F_BODY_SMALL  = Pt(12)
F_BULLET      = Pt(13)
F_CAPTION     = Pt(11)
F_FOOTER      = Pt(10)

# Max chars per slide (rough limit to avoid overflow)
MAX_CHARS_PER_SLIDE = 600


def make_run(paragraph, text, font_size=F_BODY, color=C_TEXT, bold=False, italic=False):
    """Add a run to a paragraph with formatting."""
    run = paragraph.add_run()
    run.text = text
    run.font.size = font_size
    run.font.color.rgb = color
    run.font.bold = bold
    run.font.italic = italic
    return run


def set_textbox(tf, word_wrap=True, anchor=MSO_ANCHOR.TOP):
    """Configure text frame basics."""
    tf.word_wrap = word_wrap
    tf.auto_size = None  # don't auto-resize
    try:
        tf.paragraphs[0].space_before = Pt(0)
        tf.paragraphs[0].space_after = Pt(4)
    except:
        pass


def add_body_text(tf, text, font_size=F_BODY, color=C_TEXT, is_bullet=False):
    """Add wrapped body text to a text frame, splitting by lines."""
    set_textbox(tf)
    lines = text.strip().split('\n')
    first = True
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if first:
            p = tf.paragraphs[0]
            first = False
        else:
            p = tf.add_paragraph()
        
        p.space_before = Pt(2)
        p.space_after = Pt(4)
        p.line_spacing = Pt(20)
        
        # Detect bullet
        bullet_text = None
        if line.startswith('• ') or line.startswith('- '):
            bullet_text = line[2:]
            p.level = 0
        elif line.startswith('  • ') or line.startswith('  - '):
            bullet_text = line[4:]
            p.level = 1
        
        display = bullet_text if bullet_text else line
        make_run(p, display, font_size=font_size, color=color)
    
    # If no content was added
    if first:
        make_run(tf.paragraphs[0], '', font_size=font_size)


def clean_md(text):
    """Strip markdown formatting."""
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'^#{1,4}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def split_text_pages(text, max_chars=MAX_CHARS_PER_SLIDE):
    """Split long text into page-sized chunks, respecting paragraph boundaries."""
    paragraphs = re.split(r'\n\n+', text.strip())
    pages = []
    current = []
    current_len = 0
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        plen = len(para)
        
        if current_len + plen > max_chars and current:
            pages.append('\n\n'.join(current))
            current = [para]
            current_len = plen
        else:
            current.append(para)
            current_len += plen
    
    if current:
        pages.append('\n\n'.join(current))
    
    return pages if pages else ['']


# ── PDF Figure Extraction ──

def extract_pdf_figures(pdf_path, min_w=200, min_h=150):
    """Extract large images from PDF."""
    if not HAS_FITZ or not pdf_path or not os.path.exists(pdf_path):
        return []
    
    figures = []
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(doc.page_count):
            page = doc[page_num]
            for img in page.get_images():
                try:
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    if pix.n >= 5:
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    if pix.width >= min_w and pix.height >= min_h:
                        figures.append({
                            'data': pix.tobytes("png"),
                            'w': pix.width, 'h': pix.height,
                            'page': page_num + 1
                        })
                    pix = None
                except:
                    pass
        doc.close()
    except:
        pass
    
    return figures


def render_latex(latex_str):
    """Render LaTeX formula to PNG bytes."""
    if not HAS_MPL:
        return None
    try:
        s = latex_str.strip().strip('$')
        fig = plt.figure(figsize=(6, 1.2))
        fig.patch.set_facecolor('white')
        fig.text(0.5, 0.5, f'${s}$', fontsize=14, ha='center', va='center')
        buf = BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=150,
                    facecolor='white', edgecolor='none')
        buf.seek(0)
        plt.close(fig)
        return buf.getvalue()
    except:
        return None


# ── Slide Builders ──

class SlideBuilder:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width = Inches(SLIDE_W)
        self.prs.slide_height = Inches(SLIDE_H)
        self.figures = []
        self.fig_idx = 0  # next figure to use
    
    def _blank_slide(self):
        """Add a blank slide with white background."""
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        bg = slide.background.fill
        bg.solid()
        bg.fore_color.rgb = C_WHITE
        return slide
    
    def _add_slide_title(self, slide, title):
        """Add title bar + accent line to a slide."""
        tb = slide.shapes.add_textbox(
            Inches(MARGIN), Inches(0.3), Inches(BODY_W), Inches(TITLE_H))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        make_run(p, title, F_SLIDE_TITLE, C_TITLE, bold=True)
        
        # accent line
        slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(MARGIN), Inches(LINE_Y), Inches(BODY_W), Inches(0.04)
        ).fill.solid()
        slide.shapes[-1].fill.fore_color.rgb = C_ACCENT
        slide.shapes[-1].line.fill.background()
    
    def _add_page_number(self, slide):
        """Add page number at bottom right."""
        n = len(self.prs.slides)
        tb = slide.shapes.add_textbox(
            Inches(SLIDE_W - 1.5), Inches(SLIDE_H - 0.4), Inches(1), Inches(0.3))
        tf = tb.text_frame
        make_run(tf.paragraphs[0], str(n), F_FOOTER, C_MGRAY)
        tf.paragraphs[0].alignment = PP_ALIGN.RIGHT
    
    def _next_figure(self):
        """Get next PDF figure if available."""
        if self.fig_idx < len(self.figures):
            fig = self.figures[self.fig_idx]
            self.fig_idx += 1
            return fig
        return None
    
    def _add_image(self, slide, img_bytes, left, top, width):
        """Insert image bytes into slide."""
        try:
            slide.shapes.add_picture(BytesIO(img_bytes), Inches(left), Inches(top), Inches(width))
            return True
        except:
            return False
    
    # ── Public methods ──
    
    def cover(self, title_cn, title_en='', authors='', institutions='', arxiv=''):
        """封面页"""
        slide = self._blank_slide()
        
        # Title
        y = 1.5
        tb = slide.shapes.add_textbox(Inches(1), Inches(y), Inches(11.33), Inches(1.5))
        tf = tb.text_frame; tf.word_wrap = True
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        make_run(p, title_cn or '论文深度解读', F_COVER_TITLE, C_TITLE, bold=True)
        y += 1.6
        
        if title_en:
            tb = slide.shapes.add_textbox(Inches(1), Inches(y), Inches(11.33), Inches(0.8))
            tf = tb.text_frame; tf.word_wrap = True
            p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
            make_run(p, title_en, F_COVER_SUB, C_TEXT)
            y += 0.9
        
        for label, val, color in [
            ('作者', authors, C_TEXT),
            ('机构', institutions, C_TEXT),
            ('', arxiv, C_BLUE),
        ]:
            if val:
                tb = slide.shapes.add_textbox(Inches(1), Inches(y), Inches(11.33), Inches(0.5))
                tf = tb.text_frame; tf.word_wrap = True
                p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
                text = f"{label}：{val}" if label else val
                make_run(p, text, F_BODY, color)
                y += 0.5
        
        # Footer
        tb = slide.shapes.add_textbox(Inches(1), Inches(6.5), Inches(11.33), Inches(0.4))
        tf = tb.text_frame
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        make_run(p, f"AI论文深度解读 | {datetime.now().strftime('%Y-%m-%d')}", F_CAPTION, C_MGRAY)
    
    def content_slide(self, title, text, use_figure=False):
        """Standard content slide. Optionally places a PDF figure on the right."""
        slide = self._blank_slide()
        self._add_slide_title(slide, title)
        
        fig = self._next_figure() if use_figure else None
        body_w = BODY_W_WITH_IMG if fig else BODY_W
        
        tb = slide.shapes.add_textbox(
            Inches(MARGIN), Inches(BODY_TOP), Inches(body_w), Inches(BODY_H))
        tf = tb.text_frame
        add_body_text(tf, text, font_size=F_BODY if len(text) < 500 else F_BODY_SMALL)
        
        if fig:
            self._add_image(slide, fig['data'], IMG_LEFT, BODY_TOP, IMG_W)
        
        self._add_page_number(slide)
    
    def section_slides(self, title, text, use_figures=True):
        """Auto-paginate long content into multiple slides."""
        pages = split_text_pages(clean_md(text))
        for i, page in enumerate(pages):
            t = title if len(pages) == 1 else f"{title} ({i+1}/{len(pages)})"
            self.content_slide(t, page, use_figure=use_figures)
    
    def formula_slide(self, title, formulas, caption_text=''):
        """Slide with rendered LaTeX formulas."""
        if not formulas:
            return
        slide = self._blank_slide()
        self._add_slide_title(slide, title)
        
        y = BODY_TOP + 0.2
        rendered = 0
        for f in formulas[:4]:
            img = render_latex(f)
            if img:
                self._add_image(slide, img, MARGIN + 1, y, 8)
                y += 1.6
                rendered += 1
        
        if caption_text:
            tb = slide.shapes.add_textbox(
                Inches(MARGIN), Inches(y + 0.2), Inches(BODY_W), Inches(1))
            tf = tb.text_frame; tf.word_wrap = True
            make_run(tf.paragraphs[0], caption_text, F_CAPTION, C_TEXT)
        
        if rendered:
            self._add_page_number(slide)
    
    def closing(self):
        """结尾页"""
        slide = self._blank_slide()
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = C_LGRAY
        
        tb = slide.shapes.add_textbox(Inches(2), Inches(2.5), Inches(9.33), Inches(2))
        tf = tb.text_frame
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        make_run(p, "感谢观看", F_COVER_TITLE, C_TITLE, bold=True)
        p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.CENTER; p2.space_before = Pt(16)
        make_run(p2, "欢迎讨论与交流", F_COVER_SUB, C_TEXT)
        
        tb2 = slide.shapes.add_textbox(Inches(2), Inches(5.5), Inches(9.33), Inches(0.5))
        tf2 = tb2.text_frame
        p3 = tf2.paragraphs[0]; p3.alignment = PP_ALIGN.CENTER
        make_run(p3, f"AI论文深度解读 | {datetime.now().strftime('%Y-%m-%d %H:%M')}", F_CAPTION, C_MGRAY)


# ── Report Parser ──

def parse_report(content):
    """Parse markdown report into {section_key: text} dict."""
    sections = {}
    current_key = 'header'
    current_lines = []
    
    for line in content.split('\n'):
        if line.startswith('## '):
            if current_lines:
                sections[current_key] = '\n'.join(current_lines)
            heading = line[3:].strip()
            current_key = heading
            current_lines = []
        elif line.startswith('# ') and current_key == 'header':
            current_lines.append(line[2:])
        else:
            current_lines.append(line)
    
    if current_lines:
        sections[current_key] = '\n'.join(current_lines)
    
    return sections


def find_section(sections, *keywords):
    """Find a section whose key contains any of the keywords."""
    for key, val in sections.items():
        for kw in keywords:
            if kw in key:
                return val
    return ''


def extract_formulas(text):
    """Extract LaTeX formulas from text."""
    formulas = []
    for m in re.finditer(r'\$\$([^$]+)\$\$', text):
        if len(m.group(1).strip()) > 3:
            formulas.append(m.group(1).strip())
    for m in re.finditer(r'(?<!\$)\$([^$\n]+)\$(?!\$)', text):
        if len(m.group(1).strip()) > 5:
            formulas.append(m.group(1).strip())
    return formulas


def extract_info_field(text, *keys):
    """Extract a field value from '关键词：值' patterns."""
    for line in text.split('\n'):
        for k in keys:
            if k in line and ('：' in line or ':' in line):
                sep = '：' if '：' in line else ':'
                return line.split(sep, 1)[1].strip()
    return ''


# ── Main ──

def main():
    parser = argparse.ArgumentParser(description='论文精读报告→PPT')
    parser.add_argument('input_report', help='Markdown报告文件')
    parser.add_argument('output_pptx', help='输出PPT文件')
    parser.add_argument('--pdf', help='论文PDF（可选，提取图片）')
    args = parser.parse_args()
    
    if not os.path.exists(args.input_report):
        print(f"❌ 文件不存在: {args.input_report}"); sys.exit(1)
    
    with open(args.input_report, 'r', encoding='utf-8') as f:
        content = f.read()
    
    sections = parse_report(content)
    
    # Extract paper metadata
    header = sections.get('header', '')
    title_cn = header.split('\n')[0].strip() if header else '论文深度解读'
    title_en = extract_info_field(header, '英文标题', 'English')
    authors = extract_info_field(header, '作者', 'Author')
    institutions = extract_info_field(header, '机构', '实验室', 'Lab', 'Institution')
    arxiv = ''
    m = re.search(r'https?://arxiv\.org/abs/\S+', content)
    if m:
        arxiv = m.group(0).rstrip(')')
    
    # Collect all formulas for dedicated slide
    all_formulas = extract_formulas(content)
    
    # Build PPT
    sb = SlideBuilder()
    
    # Extract PDF figures
    if args.pdf:
        sb.figures = extract_pdf_figures(args.pdf)
        print(f"📸 从PDF提取了 {len(sb.figures)} 张图片")
    
    # 1. Cover
    sb.cover(title_cn, title_en, authors, institutions, arxiv)
    
    # 2. Background / Problem
    bg = find_section(sections, '问题', '背景', '动机', 'Problem', 'Background')
    if bg:
        sb.section_slides("问题背景与动机", bg, use_figures=True)
    
    # 3. Method (biggest section, use figures)
    method = find_section(sections, '方法', '核心方法', 'Method', '技术')
    if method:
        sb.section_slides("核心方法详解", method, use_figures=True)
    
    # 4. Formula slide (if any)
    if all_formulas:
        sb.formula_slide("关键公式", all_formulas[:6])
    
    # 5. Experiments
    exp = find_section(sections, '实验', 'Experiment', '结果')
    if exp:
        sb.section_slides("实验结果分析", exp, use_figures=True)
    
    # 6. Takeaways
    tk = find_section(sections, '学到', '要点', 'Takeaway', '学习')
    if tk:
        sb.section_slides("核心学习要点", tk, use_figures=False)
    
    # 7. Medical robotics
    med = find_section(sections, '医疗', '机器人', '迁移', 'Medical', '启发')
    if med:
        sb.section_slides("医疗机器人启发", med, use_figures=False)
    
    # 8. Expert review
    exp_review = find_section(sections, '专家', '会诊', 'Expert')
    if exp_review:
        sb.section_slides("五专家会诊", exp_review, use_figures=False)
    
    # 9. Score / Summary
    score = find_section(sections, '评分', '综合', 'Score')
    summary = find_section(sections, '一句话', '精华', 'Summary')
    combined = (score + '\n\n' + summary).strip()
    if combined:
        sb.content_slide("综合评价", clean_md(combined))
    
    # 10. Action items
    action = find_section(sections, '行动', '推荐', 'Action', '建议')
    if action:
        sb.content_slide("推荐行动", clean_md(action))
    
    # 11. Closing
    sb.closing()
    
    # Save
    sb.prs.save(args.output_pptx)
    
    n_slides = len(sb.prs.slides)
    n_imgs = sum(1 for s in sb.prs.slides for sh in s.shapes 
                 if hasattr(sh, 'shape_type') and sh.shape_type == 13)
    fsize = os.path.getsize(args.output_pptx) / 1024 / 1024
    
    print(f"✅ PPT生成完成: {args.output_pptx}")
    print(f"   📄 {n_slides}页 | 🖼️ {n_imgs}张图 | 💾 {fsize:.1f}MB")
    
    if n_slides < 15:
        print("⚠️  页数偏少，检查报告完整性")


if __name__ == "__main__":
    main()
