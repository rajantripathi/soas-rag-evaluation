"""Generate the pilot result figure and a readable PDF from manuscript Markdown."""
from pathlib import Path
import json
import re
import html
import posixpath
import os

ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'tmp/matplotlib'))
PUBLIC=ROOT/'research_outputs/reproducible_pilot'
PAPER=ROOT/'research_outputs/workshop_paper_2026/paper_final.md'


def figure():
    import matplotlib
    matplotlib.use('Agg')
    matplotlib.rcParams['svg.hashsalt']='en-uz-pilot-v1'
    import matplotlib.pyplot as plt
    import numpy as np
    metrics=json.loads((PUBLIC/'metrics.json').read_text())
    fig,axes=plt.subplots(1,2,figsize=(8.4,3.2),sharey=True)
    methods=['bm25','e5_prefixed','e5_unprefixed']
    for ax,language in zip(axes,['en','uz']):
        for offset,condition,label,color in [(-.19,'full','All resolved targets','#226e8f'),(.19,'removed_42','Half removed (seed 42)','#d6a24d')]:
            values=[next(m for m in metrics if m['subset']=='original' and m['language']==language and m['method']==method and m['condition']==condition and m['k']==3) for method in methods]
            bars=ax.bar(np.arange(3)+offset,[100*m['hit_rate'] for m in values],width=.36,color=color,label=label)
            ax.bar_label(bars,fmt='%.1f',fontsize=8,padding=3)
        ax.set_title('English (100 original questions)' if language=='en' else 'Uzbek (96 original questions)',fontsize=10)
        ax.set_xticks(range(3),['BM25','E5 + prefixes','E5, no prefixes'],fontsize=8)
        ax.set_ylim(0,110)
        ax.set_yticks([0,25,50,75,100])
        ax.spines[['top','right']].set_visible(False)
        ax.grid(axis='y',alpha=.15)
        ax.set_axisbelow(True)
    axes[0].set_ylabel('Source hit rate at 3 (%)',fontsize=9)
    handles,labels=axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='lower center',ncol=2,frameon=False,fontsize=9)
    fig.tight_layout(rect=(0,.10,1,1))
    fig.savefig(PUBLIC/'coverage_results.png',dpi=240)
    fig.savefig(PUBLIC/'coverage_results.svg',metadata={'Date':None})
    svg=PUBLIC/'coverage_results.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    plt.close(fig)


DEFAULT_FIGURES=[('Full Hit',PUBLIC/'coverage_results.png',3.2/8.4,'Figure 1. Source hit rate at 3 on original questions. Complete and seed-42 reduced corpora share the same background articles. The reduced corpus excludes half the designated source pages.')]


def pdf(paper=PAPER,out=ROOT/'output/pdf/en-uz-retrieval-pilot.pdf',link_base='research_outputs/workshop_paper_2026/',
        title='Controlled Source Availability in an English-Uzbek Retrieval Pilot',
        footer_text='English-Uzbek retrieval pilot | Working preprint manuscript',figures=None):
    figures=list(DEFAULT_FIGURES if figures is None else figures)
    from markdown_it import MarkdownIt
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    fonts=[Path('/System/Library/Fonts/Supplemental'),Path('/usr/share/fonts/truetype/dejavu')]
    for folder in fonts:
        regular=folder/('Arial.ttf' if 'Supplemental' in str(folder) else 'DejaVuSans.ttf')
        bold=folder/('Arial Bold.ttf' if 'Supplemental' in str(folder) else 'DejaVuSans-Bold.ttf')
        if regular.exists():
            pdfmetrics.registerFont(TTFont('Paper',str(regular)))
            pdfmetrics.registerFont(TTFont('Paper-Bold',str(bold)))
            pdfmetrics.registerFontFamily('Paper',normal='Paper',bold='Paper-Bold',italic='Paper',boldItalic='Paper-Bold')
            break
    else:
        raise RuntimeError('Install Arial or DejaVu Sans to build the PDF')
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle('PaperBody',fontName='Paper',fontSize=9.2,leading=13.2,spaceAfter=6,splitLongWords=True))
    styles.add(ParagraphStyle('PaperTitle',fontName='Paper-Bold',fontSize=20,leading=24,spaceAfter=14))
    styles.add(ParagraphStyle('PaperH2',fontName='Paper-Bold',fontSize=12,leading=16,spaceBefore=12,spaceAfter=6,keepWithNext=True))
    styles.add(ParagraphStyle('PaperH3',fontName='Paper-Bold',fontSize=10,leading=14,spaceBefore=8,spaceAfter=4,keepWithNext=True))
    styles.add(ParagraphStyle('PaperTable',fontName='Paper',fontSize=7.8,leading=10.5,spaceAfter=0))
    styles.add(ParagraphStyle('TableCaption',fontName='Paper-Bold',fontSize=8.4,leading=11,spaceAfter=5,keepWithNext=True))
    styles.add(ParagraphStyle('PaperCaption',fontName='Paper',fontSize=8,leading=11,spaceAfter=8))

    def inline(token):
        value=[]
        for child in token.children or []:
            if child.type=='text': value.append(html.escape(child.content))
            elif child.type=='code_inline': value.append('<font face="Paper">'+html.escape(child.content)+'</font>')
            elif child.type=='strong_open': value.append('<b>')
            elif child.type=='strong_close': value.append('</b>')
            elif child.type=='em_open': value.append('<i>')
            elif child.type=='em_close': value.append('</i>')
            elif child.type in ('softbreak','hardbreak'): value.append(' ')
            elif child.type=='link_open':
                href=child.attrGet('href')
                if not href.startswith(('https://','http://')):
                    href='https://github.com/rajantripathi/soas-rag-evaluation/blob/main/'+posixpath.normpath(link_base+href)
                value.append('<a color="#226e8f" href="'+html.escape(href,quote=True)+'">')
            elif child.type=='link_close': value.append('</a>')
        return ''.join(value)

    text=Path(paper).read_text().replace('—','-').replace('–','-').replace('‑','-')
    tokens=MarkdownIt('commonmark').enable('table').parse(text)
    story=[]; i=0; pending_caption=None; in_bullets=False; list_number=None; item_prefix=""
    while i<len(tokens):
        token=tokens[i]
        if token.type=='ordered_list_open':
            list_number=int(token.attrGet('start') or 1)
        elif token.type=='ordered_list_close':
            list_number=None
        elif token.type=='bullet_list_open':
            in_bullets=True
        elif token.type=='bullet_list_close':
            in_bullets=False
        elif token.type=='list_item_open' and list_number is not None:
            item_prefix=f'[{list_number}] '
            list_number+=1
        elif token.type=='list_item_open' and in_bullets:
            item_prefix='\u2022 '
        if token.type=='heading_open':
            level=int(token.tag[1]); style='PaperTitle' if level==1 else 'PaperH2' if level==2 else 'PaperH3'
            story.append(Paragraph(inline(tokens[i+1]),styles[style]));i+=3;continue
        if token.type=='paragraph_open':
            value=item_prefix+inline(tokens[i+1])
            item_prefix=''
            style='TableCaption' if value.startswith('<b>Table ') else 'PaperBody'
            paragraph=Paragraph(value,styles[style])
            if style=='TableCaption': pending_caption=paragraph
            else: story.append(paragraph)
            i+=3;continue
        if token.type=='table_open':
            data=[];row=[];i+=1
            while tokens[i].type!='table_close':
                t=tokens[i]
                if t.type=='tr_open': row=[]
                elif t.type=='inline': row.append(Paragraph(inline(t),styles['PaperTable']))
                elif t.type=='tr_close': data.append(row)
                i+=1
            columns=len(data[0]);widths=[495/columns]*columns
            table=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e9f0f3')),
                                      ('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.5,colors.HexColor('#748a95')),
                                      ('LINEBELOW',(0,1),(-1,-1),.25,colors.HexColor('#d8dfe3')),
                                      ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
            story.append(KeepTogether(([pending_caption] if pending_caption else [])+[table,Spacer(1,10)]))
            pending_caption=None
            for figure_spec in list(figures):
                trigger,image,aspect,caption=figure_spec
                if any(trigger in x.text for x in data[0]):
                    story.append(KeepTogether([Image(str(image),width=495,height=495*aspect),
                                               Paragraph(caption,styles['PaperCaption'])]))
                    figures.remove(figure_spec)
            i+=1;continue
        if token.type=='hr': story.append(Spacer(1,5))
        i+=1
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    def footer(canvas,doc):
        canvas.saveState();canvas.setFont('Paper',7)
        canvas.setFillColor(colors.HexColor('#68747c'))
        canvas.drawString(50,27,footer_text)
        canvas.drawRightString(545,27,str(doc.page));canvas.restoreState()
    doc=SimpleDocTemplate(str(out),pagesize=(595.28,841.89),leftMargin=50,rightMargin=50,topMargin=44,bottomMargin=44,
                          title=title,author='Rajan Prasad Tripathi')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    print(out)


if __name__=='__main__':
    figure();pdf()
