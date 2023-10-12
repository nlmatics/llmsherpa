class Block:
    tag: str
    def __init__(self, block_json=None):
        self.tag = block_json['tag'] if block_json and 'tag' in block_json else None
        self.level = block_json['level'] if block_json and 'level' in block_json else -1
        self.sentences = block_json['sentences'] if block_json and 'sentences' in block_json else []
        self.children = []
    def add_child(self, node):
        self.children.append(node)
    def to_html(self):
        pass
    def to_text(self):
        pass
        
        
    # def children():
    # def descendents():
    # def paragraphs():
    # def tables():
    # def sentences():
    # def parent():
    # def sentences():
# n = Node(parsed_doc.json_dict['blocks'][0])
# for sent in n.sentences:
#     print(sent)
class Paragraph(Block):
    def __init__(self, para_json):
        super().__init__(para_json)
    def to_text(self):
        return "\n".join(self.sentences)
    def to_html(self):
        html_str = "<p>"
        html_str = html_str + self.to_text()
        html_str = html_str + "</p>"
        return html_str
    
class Section(Block):
    def __init__(self, section_json):
        super().__init__(section_json)
        self.title = "\n".join(self.sentences)
    def to_text(self):
        return self.title
    def to_html(self):
        html_str = f"<h{self.level + 1}>"
        html_str = html_str + self.to_text()
        html_str = html_str + f"</h{self.level + 1}>"
        return html_str

class ListItem(Block):
    def __init__(self, list_json):
        super().__init__(list_json)
    def to_text(self):
        return "\n".join(self.sentences)
    def to_html(self):
        html_str = f"<li>"
        html_str = html_str + self.to_text()
        html_str = html_str + f"</li>"
        return html_str

class List(Block):
    def __init__(self, list_json):
        self.x = 0
    
class TableCell(Block):
    def __init__(self, cell_json):
        super().__init__(cell_json)
        self.col_span = cell_json['col_span'] if 'col_span' in cell_json else 1
        self.cell_value = cell_json['cell_value']
        if not isinstance(self.cell_value, str):
            self.cell_node = Paragraph(self.cell_value)
        else:
            self.cell_node = None
    def to_text(self):
        cell_text = self.cell_value
        if self.cell_node:
            cell_text = self.cell_node.to_text()
        return cell_text
    def to_html(self):
        cell_html = self.cell_value
        if self.cell_node:
            cell_html = self.cell_node.to_html()
        if self.col_span == 1:
            html_str = f"<td colSpan={self.col_span}>{cell_html}</td>"
        else:
            html_str = f"<td>{cell_html}</td>"
        return html_str
            
class TableRow(Block):
    def __init__(self, row_json):
        self.cells = []
        if row_json['type'] == 'full_row':
            cell = TableCell(row_json)
            self.cells.append(cell)
        else:
            for cell_json in row_json['cells']:
                cell = TableCell(cell_json)
                self.cells.append(cell)
    def to_text(self):
        cell_text = ""
        for cell in self.cells:
            cell_text = cell_text + " | " + cell.to_text()
        return cell_text
    def to_html(self):
        html_str = "<tr>"
        for cell in self.cells:
            html_str = html_str + cell.to_html()
        html_str = html_str + "</tr>"
        return html_str

class TableHeader(Block):
    def __init__(self, row_json):
        super().__init__(row_json)
        self.cells = []
        for cell_json in row_json['cells']:
            cell = TableCell(cell_json)
            self.cells.append(cell)
    def to_html(self):
            html_str = "<th>"
            for cell in self.cells:
                html_str = html_str + cell.to_html()
            html_str = html_str + "</th>"
            return html_str
        
class Table(Block):
    def __init__(self, table_json, parent):
        # self.title = parent.name
        super().__init__(table_json)
        self.rows = []
        self.headers = []
        if 'table_rows' in table_json:
            for row_json in table_json['table_rows']:
                if row_json['type'] == 'table_header':
                    row = TableRow(row_json)
                    self.headers.append(row)
                else:
                    row = TableRow(row_json)
                    self.rows.append(row)
    def to_html(self):
        html_str = "<table>"
        for header in self.headers:
            html_str = html_str + header.to_html()
        for row in self.rows:
            html_str = html_str + row.to_html()
        html_str = html_str + "</table>"
        return html_str
    
class LayoutPDFReader:
    def debug(self, pdf_root):
        def iter_children(node, level):
            for child in node.children:
                print("-"*level, child.tag, f"({len(child.children)})", child.to_text())
                iter_children(child, level + 1)
        iter_children(pdf_root, 0)

    def read(self, blocks_json):
        root = Block()
        parent = None
        # table_node = None
        table_nodes = []
        sections = []
        # prev_list = None
        parent_stack = [root]
        prev_node = root
        parent = root
        list_stack = []
        for block in blocks_json:
            if block['tag'] != 'list_item' and len(list_stack) > 0:
                list_stack = []
            if block['tag'] == 'para':
                node = Paragraph(block)
                parent.add_child(node)
            elif block['tag'] == 'table':
                node = Table(block, prev_node)
                parent.add_child(node)
            elif block['tag'] == 'list_item':
                node = ListItem(block)
                # add lists as children to previous paragraph 
                # this handles examples like - The following items need to be addressed: 1) item 1 2) item 2 etc.
                if prev_node.tag == 'para' and prev_node.level == node.level:
                    list_stack.append(prev_node)
                # sometimes there are lists within lists in legal documents
                elif prev_node.tag == 'list_item':
                    if node.level > prev_node.level:
                        list_stack.append(prev_node)
                    elif node.level < prev_node.level:
                        while len(list_stack) > 0 and list_stack.pop().level > node.level:
                            pass
                        # list_stack.append(node)
                if len(list_stack) > 0:
                    list_stack[-1].add_child(node)
                else:
                    parent.add_child(node)
                    
            elif block['tag'] == 'header':
                node = Section(block)
                if node.level > parent.level:
                    parent_stack.append(node)
                    parent.add_child(node)
                else:
                    while len(parent_stack) > 0 and parent_stack.pop().level > node.level:
                        pass
                    parent_stack[-1].add_child(node)            
                    parent_stack.append(node)
                parent = node
            prev_node = node

        return root

