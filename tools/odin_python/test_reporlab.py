from reportlab.lib.pagesizes import LETTER, inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Custom DocTemplate that adds bookmarks for internal linking
class MyDocTemplate(SimpleDocTemplate):
    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        self.bookmarkList = []
    
    def afterFlowable(self, flowable):
        # If the flowable has a bookmark attribute, create a bookmark for it
        if hasattr(flowable, 'bookmark'):
            self.canv.bookmarkPage(flowable.bookmark)
            # Optional: add to outline (table of contents)
            # self.canv.addOutlineEntry(flowable.getPlainText(), flowable.bookmark, level=0, closed=False)

styles = getSampleStyleSheet()

# Create the document using our custom template
doc = MyDocTemplate("internal_links_custom.pdf", pagesize=LETTER,
                    rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
story = []

# Create a top anchor and assign a bookmark attribute
top_title = Paragraph('<a name="top"/>Internal Linking Example', styles['Title'])
top_title.bookmark = "top"

story.append(top_title)
story.append(Spacer(1, 0.3 * inch))

# Table of Contents with internal links using HTML anchor tags
toc_html = ('<a href="#section1">Go to Section 1</a><br/>'
            '<a href="#section2">Go to Section 2</a><br/>'
            '<a href="#section3">Go to Section 3</a>')
story.append(Paragraph(toc_html, styles['Normal']))
story.append(PageBreak())

# Create several sections with anchors and back-to-top links
for i in range(1, 4):
    # Define a section title with an anchor and set its bookmark attribute
    section_title = Paragraph(f'<a name="section{i}"/>Section {i}', styles['Heading1'])
    section_title.bookmark = f'section{i}'
    story.append(section_title)
    story.append(Spacer(1, 0.2 * inch))
    
    # Add some example paragraph text
    text = ("This is an example paragraph for Section {}. ".format(i)) * 5
    story.append(Paragraph(text, styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))
    
    # Example table
    data = [
        ['Column 1', 'Column 2'],
        ['Data 1', 'Data 2']
    ]
    table = Table(data, colWidths=[3*inch, 3*inch])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2 * inch))
    
    # Back-to-top link using HTML anchor (this will now work correctly)
    back_to_top = Paragraph('<a href="#top">Back to top</a>', styles['Normal'])
    story.append(back_to_top)
    
    # Insert a page break between sections except after the last one
    if i < 3:
        story.append(PageBreak())

# Build the PDF document
doc.build(story)
