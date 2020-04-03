import html

from kts.settings import cfg
from kts.ui.highlighting import highlighter


class HTMLRepr:
    def _repr_html_(self):
        return f'<div class="kts">{self.html}</div>'


class Column(HTMLRepr):
    def __init__(self, elements, border=False, style=""):
        self.elements = elements
        self.style = style
        self.border = border

    @property
    def html(self):
        css_class = ""
        if self.border:
            css_class += 'wrapper-border'
        stacked = "\n".join([e.html for e in self.elements])
        return f"""<div class="{css_class} wrapper" style="{self.style}">{stacked}</div>"""


class Pool(HTMLRepr):
    def __init__(self, elements):
        self.elements = elements

    @property
    def html(self):
        stacked = "\n".join([e.html for e in self.elements])
        return f"""<div class="pool">{stacked}</div>"""


class Field(HTMLRepr):
    def __init__(self, string, bold=True, accent=True, bg=True, style=""):
        self.string = str(string).replace('\n', '<br>')
        self.bold = bold
        self.accent = accent
        self.bg = bg
        self.style = style

    @property
    def html(self):
        css_class = "field"
        if self.bold:
            css_class += " field-bold"
        if self.bg:
            css_class += " field-bg"
        if self.accent:
            css_class += " field-accent"
        else:
            css_class += " field-third"
        return f"""<div class="{css_class}" style="{self.style}">{self.string}</div>"""


class Annotation(HTMLRepr):
    def __init__(self, string, style=""):
        self.string = string
        self.style = style

    @property
    def html(self):
        return f"""<div class="annotation" style="{self.style}">{self.string}</div>"""


class Title(HTMLRepr):
    def __init__(self, string, style=""):
        self.string = string
        self.style = style

    @property
    def html(self):
        return f"""<div class="title" style="{self.style}">{self.string.upper()}</div>"""


class TitleWithCross(HTMLRepr):
    def __init__(self, string, css_id):
        self.string = string
        self.css_id = css_id

    @property
    def html(self):
        return f"""<div class="title-with-cross">
            <div></div>
            <div class="title">{self.string.upper()}</div>
            <label class="cross-circle" for="{self.css_id}">
                <div class="cross-before"></div>
                <div class="cross-after"></div>
            </label>
        </div>"""


class Code(HTMLRepr):
    def __init__(self, code):
        self.code = code
        self.html_code = highlighter.highlight(code)

    @property
    def html(self):
        return f"""<div class="code"><pre>{self.html_code}</pre></div>"""


class CollapsibleColumn(HTMLRepr):
    def __init__(self, elements, thumbnail, css_id, outer=False, border=False):
        self.elements = elements
        self.thumbnail = thumbnail
        self.css_id = css_id
        self.outer = outer
        self.border = border

    @property
    def html(self):
        stacked = "\n".join([e.html for e in self.elements])
        if self.outer:
            check_class = "check-outer"
        else:
            check_class = "check"
        column_class = ""
        if self.border:
            column_class += 'wrapper-border'
        return f"""<input type="checkbox" class="{check_class}" id="{self.css_id}"/>
            <div class="wrapper {column_class}" id="collapsible">{self.thumbnail.html}<div class="inner-wrapper" id="hidden">{stacked}</div>
        </div>"""


class InnerColumn(HTMLRepr):
    def __init__(self, elements):
        self.elements = elements

    @property
    def html(self):
        stacked = "\n".join([e.html for e in self.elements])
        return f"""<div class="inner-column">{stacked}</div>"""


class Row(HTMLRepr):
    def __init__(self, elements):
        self.elements = elements

    @property
    def html(self):
        stacked = "\n".join([e.html for e in self.elements])
        return f"""<div class="row">{stacked}</div>"""


class AlignedColumns(HTMLRepr):
    def __init__(self, columns, title=None, bg=True, style=None):
        self.columns = columns
        self.title = title
        self.bg = bg
        self.style = style

    @property
    def html(self):
        n_cols = len(self.columns)
        res = f"""<div {'class="wrapper"' if self.bg and not self.title else ''} style="display: inline-grid; grid-template-columns: {'auto ' * n_cols if not self.style else self.style};">"""
        for row in zip(*self.columns):
            res += ''.join(row) + '\n'
        res += "</div>"
        if self.title is not None:
            res = f"""<div {'class="wrapper"' if self.bg and self.title else ''} style="display: inline-grid; grid-template-rows: auto auto;">{Title(self.title, style="margin-bottom: 5px;").html}{res}</div>"""
        return res


class Output(HTMLRepr):
    def __init__(self, string):
        self.string = string

    @property
    def html(self):
        lines = self.string.split('\n')[::-1]
        inner_css = '\n'.join([f"<div>{html.escape(line)}</div>" for line in lines])
        return f"""<div class="output">{inner_css}</div>"""


class ThumbnailField(HTMLRepr):
    def __init__(self, string, css_id, bold=True, accent=True, first=True, bg=True, style=""):
        self.string = string
        self.css_id = css_id
        self.bold = bold
        self.accent = accent
        self.bg = bg
        self.first = first
        self.style = style

    @property
    def html(self):
        css_class = "field"
        if self.bold:
            css_class += " field-bold"
        if self.bg:
            css_class += " field-bg"
        if self.accent:
            css_class += " field-accent"
        else:
            css_class += " field-third"
        if self.first:
            css_class += " thumbnail-first"
        else:
            css_class += " thumbnail-second"
        return f"""<label class="{css_class} thumbnail" style="{self.style}" for="{self.css_id}">{self.string}</label>"""


class Progress(HTMLRepr):
    def __init__(self, value=None, total=None,  style=""):
        self.value = value
        self.total = total
        self.style = style

    @property
    def html(self):
        if isinstance(self.value, int) and isinstance(self.total, int):
            return f"""<progress value="{self.value}" max="{self.total}" style="{self.style}"></progress>"""
        else:
            return f"""<progress max="1" style="{self.style}"></progress>"""


class DF(HTMLRepr):
    def __init__(self, df):
        self.df = df

    @property
    def html(self):
        return f"""<div class="df">{self.df._repr_html_()}</div>"""


class Raw(HTMLRepr):
    def __init__(self, html):
        self.html = html


class CSS(HTMLRepr):
    def __init__(self, style):
        self.style = style

    @property
    def html(self):
        return f'<div><style scoped>\n{self.style}\n</style></div>\n'


class CurrentTheme(HTMLRepr):
    def __init__(self):
        self.sample_code = """@decorator\ndef func(arg):\n    return arg + 1"""

    @property
    def html(self):
        return Column([
            CSS(cfg._highlighter.css),
            CSS(cfg._theme.css),
            Title('theme'),
            Annotation('annotation'),
            Field('field'),
            Annotation('code'),
            Code(self.sample_code),
        ]).html
