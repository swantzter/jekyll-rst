import re

from docutils import nodes, utils
from docutils.writers import html4css1
from docutils.core import publish_parts
from docutils.parsers.rst import roles, directives, Directive


class Writer(html4css1.Writer):
    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = HTML5Translator


class HTML5Translator(html4css1.HTMLTranslator):
    sollbruchstelle = re.compile(
        r'.+\W\W.+|[-?].+', re.U)  # wrap point inside word

    def should_be_compact_paragraph(self, node):
        if(isinstance(node.parent, nodes.block_quote)):
            return 0
        return html4css1.HTMLTranslator.should_be_compact_paragraph(self, node)

    def visit_section(self, node):
        self.section_level += 1
        self.body.append(
            self.starttag(node, 'section'))

    def depart_section(self, node):
        self.section_level -= 1
        self.body.append('</section>\n')

    def visit_kbd(self, node):
        self.body.append(self.starttag(node, 'kbd', ''))

    def depart_kbd(self, node):
        self.body.append('</kbd>')

    def visit_table(self, node):
        self.context.append(self.compact_p)
        self.compact_p = True
        classes = ' '.join([self.settings.table_style]).strip()
        self.body.append(self.starttag(node, 'div', CLASS="table-container"))
        self.body.append(
            self.starttag(node, 'table', CLASS=classes))

    def depart_table(self, node):
        self.compact_p = self.context.pop()
        self.body.append('</table>\n')
        self.body.append('</div>\n')

    def visit_literal(self, node):
        self.body.append(
            self.starttag(node, 'code', '', CLASS='docutils literal'))
        text = node.astext()
        for token in self.words_and_spaces.findall(text):
            if token.strip():
                self.body.append(self.encode(token))
            elif token in ('\n', ' '):
                # Allow breaks at whitespace:
                self.body.append(token)
            else:
                # Protect runs of multiple spaces; the last space can wrap:
                self.body.append('&nbsp;' * (len(token) - 1) + ' ')
        self.body.append('</code>')
        # Content already processed:
        raise nodes.SkipNode

    def depart_literal(self, node):
        # skipped unless literal element is from "code" role:
        self.body.append('</code>')


class kbd(nodes.Inline, nodes.TextElement):
    """Node for kbd element"""


def inline_roles(role, raw, text, *args):
    if role == 'kbd':
        return [kbd('kbd', text)], []


nodes._add_node_class_names('kbd')
roles.register_local_role('kbd', inline_roles)

if __name__ == '__main__':
    import sys
    parts = publish_parts(writer=Writer(),
                          source=open(sys.argv[1]).read())
    print(parts['html_body'])
