class Block:
    """
    A block is a node in the layout tree. It can be a paragraph, a list item, a table, or a section header. 
    This is the base class for all blocks such as Paragraph, ListItem, Table, Section.

    Attributes
    ----------
    tag: str
        tag of the block e.g. para, list_item, table, header
    level: int
        level of the block in the layout tree
    page_idx: int
        page index of the block in the document. It starts from 0 and is -1 if the page number is not available
    block_idx: int
        id of the block as returned from the server. It starts from 0 and is -1 if the id is not available
    top: float
        top position of the block in the page and it is -1 if the position is not available - only available for tables
    left: float
        left position of the block in the page and it is -1 if the position is not available - only available for tables
    bbox: [float]
        bounding box of the block in the page and it is [] if the bounding box is not available
    sentences: list
        list of sentences in the block
    children: list
        list of immediate child blocks, but not the children of the children
    parent: Block
        parent of the block
    block_json: dict
        json returned by the parser API for the block
    """
    tag: str
    def __init__(self, block_json=None):
        self.tag = block_json['tag'] if block_json and 'tag' in block_json else None
        self.level = block_json['level'] if block_json and 'level' in block_json else -1
        self.page_idx = block_json['page_idx'] if block_json and 'page_idx' in block_json else -1
        self.block_idx = block_json['block_idx'] if block_json and 'block_idx' in block_json else -1
        self.top = block_json['top'] if block_json and 'top' in block_json else -1
        self.left = block_json['left'] if block_json and 'left' in block_json else -1
        self.bbox = block_json['bbox'] if block_json and 'bbox' in block_json else []
        self.sentences = block_json['sentences'] if block_json and 'sentences' in block_json else []
        self.children = []
        self.parent = None
        self.block_json = block_json

    def add_child(self, node):
        """
        Adds a child to the block. Sets the parent of the child to self.
        """
        self.children.append(node)
        node.parent = self

    def to_html(self, include_children=False, recurse=False):
        """
        Converts the block to html. This is a virtual method and should be implemented by the derived classes.
        """
        pass

    def to_text(self, include_children=False, recurse=False):
        """
        Converts the block to text. This is a virtual method and should be implemented by the derived classes.
        """
        pass

    def parent_chain(self):
        """
        Returns the parent chain of the block consisting of all the parents of the block until the root.
        """
        chain = []
        parent = self.parent
        while parent:
            chain.append(parent)
            parent = parent.parent
        chain.reverse()
        return chain

    def parent_text(self):
        """
        Returns the text of the parent chain of the block. This is useful for adding section information to the text.
        """
        parent_chain = self.parent_chain()
        header_texts = []
        para_texts = []
        for p in parent_chain:
            if p.tag == "header":
                header_texts.append(p.to_text()) 
            elif p.tag in ['list_item', 'para']:
                para_texts.append(p.to_text())
        text = " > ".join(header_texts)
        if len(para_texts) > 0:
            text +="\n".join(para_texts)
        return text                

    def to_context_text(self, include_section_info=True):
        """
        Returns the text of the block with section information. This provides context to the text.
        """
        text = ""
        if include_section_info:
            text += self.parent_text() + "\n"
        if self.tag in ['list_item', 'para', 'table']:
            text += self.to_text(include_children=True, recurse=True)
        else:
            text += self.to_text()
        return text
    
    def iter_children(self, node, level, node_visitor):
        """
        Iterates over all the children of the node and calls the node_visitor function on each child.
        """
        for child in node.children:
            node_visitor(child)
            # print("-"*level, child.tag, f"({len(child.children)})", child.to_text())
            if child.tag not in ['list_item', 'para', 'table']:
                self.iter_children(child, level + 1, node_visitor)

    def paragraphs(self):
        """
        Returns all the paragraphs in the block. This is useful for getting all the paragraphs in a section.
        """
        paragraphs = []
        def para_collector(node):
            if node.tag == 'para':
                paragraphs.append(node)
        self.iter_children(self, 0, para_collector)
        return paragraphs
       
    def chunks(self):
        """
        Returns all the chunks in the block. Chunking automatically splits the document into paragraphs, lists, and tables without any prior knowledge of the document structure.
        """
        chunks = []
        def chunk_collector(node):
            if node.tag in ['para', 'list_item', 'table']:
                chunks.append(node)
        self.iter_children(self, 0, chunk_collector)
        return chunks
    
    def tables(self):
        """
        Returns all the tables in the block. This is useful for getting all the tables in a section.
        """
        tables = []
        def chunk_collector(node):
            if node.tag in ['table']:
                tables.append(node)
        self.iter_children(self, 0, chunk_collector)        
        return tables

    def sections(self):
        """
        Returns all the sections in the block. This is useful for getting all the sections in a document.
        """
        sections = []
        def chunk_collector(node):
            if node.tag in ['header']:
                sections.append(node)
        self.iter_children(self, 0, chunk_collector)
        return sections

class Paragraph(Block):
    """
    A paragraph is a block of text. It can have children such as lists. A paragraph has tag 'para'.
    """
    def __init__(self, para_json):
        super().__init__(para_json)
    def to_text(self, include_children=False, recurse=False):
        """
        Converts the paragraph to text. If include_children is True, then the text of the children is also included. If recurse is True, then the text of the children's children are also included.
        
        Parameters
        ----------
        include_children: bool
            If True, then the text of the children are also included
        recurse: bool
            If True, then the text of the children's children are also included
        """
        para_text = "\n".join(self.sentences)
        if include_children:
            for child in self.children:
                para_text += "\n" + child.to_text(include_children=recurse, recurse=recurse)
        return para_text    
    def to_html(self, include_children=False, recurse=False):
        """
        Converts the paragraph to html. If include_children is True, then the html of the children is also included. If recurse is True, then the html of the children's children are also included.

        Parameters
        ----------
        include_children: bool
            If True, then the html of the children are also included
        recurse: bool
            If True, then the html of the children's children are also included
        """
        html_str = "<p>"
        html_str = html_str + "\n".join(self.sentences)
        if include_children:
            if len(self.children) > 0:
                html_str += "<ul>"
                for child in self.children:
                    html_str = html_str + child.to_html(include_children=recurse, recurse=recurse)
                html_str += "</ul>"
        html_str = html_str + "</p>"
        return html_str
    
class Section(Block):
    """
    A section is a block of text. It can have children such as paragraphs, lists, and tables. A section has tag 'header'.

    Attributes
    ----------
    title: str
        title of the section
    """
    def __init__(self, section_json):
        super().__init__(section_json)
        self.title = "\n".join(self.sentences)
    def to_text(self, include_children=False, recurse=False):
        """
        Converts the section to text. If include_children is True, then the text of the children is also included. If recurse is True, then the text of the children's children are also included.

        Parameters
        ----------
        include_children: bool
            If True, then the text of the children are also included
        recurse: bool
            If True, then the text of the children's children are also included
        """
        text = self.title
        if include_children:
            for child in self.children:
                text += "\n" + child.to_text(include_children=recurse, recurse=recurse)
        return text    

    def to_html(self, include_children=False, recurse=False):
        """
        Converts the section to html. If include_children is True, then the html of the children is also included. If recurse is True, then the html of the children's children are also included.

        Parameters
        ----------
        include_children: bool
            If True, then the html of the children are also included
        recurse: bool
            If True, then the html of the children's children are also included
        """
        html_str = f"<h{self.level + 1}>"
        html_str = html_str + self.title
        html_str = html_str + f"</h{self.level + 1}>"
        if include_children:
            for child in self.children:
                html_str += child.to_html(include_children=recurse, recurse=recurse)
        return html_str

class ListItem(Block):
    """
    A list item is a block of text. It can have child list items. A list item has tag 'list_item'.
    """
    def __init__(self, list_json):
        super().__init__(list_json)

    def to_text(self, include_children=False, recurse=False):
        """
        Converts the list item to text. If include_children is True, then the text of the children is also included. If recurse is True, then the text of the children's children are also included.
        
        Parameters
        ----------
        include_children: bool
            If True, then the text of the children are also included
        recurse: bool
            If True, then the text of the children's children are also included
        """
        text = "\n".join(self.sentences)
        if include_children:
            for child in self.children:
                text += "\n" + child.to_text(include_children=recurse, recurse=recurse)
        return text    

    def to_html(self, include_children=False, recurse=False):
        """
        Converts the list item to html. If include_children is True, then the html of the children is also included. If recurse is True, then the html of the children's children are also included.
        
        Parameters
        ----------
        include_children: bool
            If True, then the html of the children are also included
        recurse: bool
            If True, then the html of the children's children are also included
        """
        html_str = f"<li>"
        html_str = html_str + "\n".join(self.sentences)
        if include_children:
            if len(self.children) > 0:
                html_str += "<ul>"
                for child in self.children:
                    html_str = html_str + child.to_html(include_children=recurse, recurse=recurse)
                html_str += "</ul>"        
        html_str = html_str + f"</li>"
        return html_str

    
class TableCell(Block):
    """
    A table cell is a block of text. It can have child paragraphs. A table cell has tag 'table_cell'.
    A table cell is contained within table rows.
    """
    def __init__(self, cell_json):
        super().__init__(cell_json)
        self.col_span = cell_json['col_span'] if 'col_span' in cell_json else 1
        self.cell_value = cell_json['cell_value']
        if not isinstance(self.cell_value, str):
            self.cell_node = Paragraph(self.cell_value)
        else:
            self.cell_node = None
    def to_text(self):
        """
        Returns the cell value of the text. If the cell value is a paragraph node, then the text of the node is returned.
        """
        cell_text = self.cell_value
        if self.cell_node:
            cell_text = self.cell_node.to_text()
        return cell_text
    def to_html(self):
        """
        Returns the cell value ashtml. If the cell value is a paragraph node, then the html of the node is returned.
        """
        cell_html = self.cell_value
        if self.cell_node:
            cell_html = self.cell_node.to_html()
        if self.col_span == 1:
            html_str = f"<td colSpan={self.col_span}>{cell_html}</td>"
        else:
            html_str = f"<td>{cell_html}</td>"
        return html_str
            
class TableRow(Block):
    """
    A table row is a block of text. It can have child table cells.
    """
    def __init__(self, row_json):
        self.cells = []
        if row_json['type'] == 'full_row':
            cell = TableCell(row_json)
            self.cells.append(cell)
        else:
            for cell_json in row_json['cells']:
                cell = TableCell(cell_json)
                self.cells.append(cell)
    def to_text(self, include_children=False, recurse=False):
        """
        Returns text of a row with text from all the cells in the row delimited by '|'
        """
        cell_text = ""
        for cell in self.cells:
            cell_text = cell_text + " | " + cell.to_text()
        return cell_text
    def to_html(self, include_children=False, recurse=False):
        """
        Returns html for a <tr> with html from all the cells in the row as <td>
        """
        html_str = "<tr>"
        for cell in self.cells:
            html_str = html_str + cell.to_html()
        html_str = html_str + "</tr>"
        return html_str

class TableHeader(Block):
    """
    A table header is a block of text. It can have child table cells.
    """
    def __init__(self, row_json):
        super().__init__(row_json)
        self.cells = []
        for cell_json in row_json['cells']:
            cell = TableCell(cell_json)
            self.cells.append(cell)
    def to_text(self, include_children=False, recurse=False):
        """
        Returns text of a row with text from all the cells in the row delimited by '|' and the header row is delimited by '---'
        Text is returned in markdown format.
        """
        cell_text = ""
        for cell in self.cells:
            cell_text = cell_text + " | " + cell.to_text()
        cell_text += "\n"
        for cell in self.cells:
            cell_text = cell_text + " | " + "---"           
        return cell_text
    def to_html(self, include_children=False, recurse=False):
        """
        Returns html for a <th> with html from all the cells in the row as <td>
        """
        html_str = "<th>"
        for cell in self.cells:
            html_str = html_str + cell.to_html()
        html_str = html_str + "</th>"
        return html_str
        
class Table(Block):
    """
    A table is a block of text. It can have child table rows. A table has tag 'table'.
    """
    def __init__(self, table_json, parent):
        # self.title = parent.name
        super().__init__(table_json)
        self.rows = []
        self.headers = []
        self.name = table_json["name"]
        if 'table_rows' in table_json:
            for row_json in table_json['table_rows']:
                if row_json['type'] == 'table_header':
                    row = TableHeader(row_json)
                    self.headers.append(row)
                else:
                    row = TableRow(row_json)
                    self.rows.append(row)
    def to_text(self, include_children=False, recurse=False):
        """
        Returns text of a table with text from all the rows in the table delimited by '\n'
        """
        text = ""
        for header in self.headers:
            text = text + header.to_text() + "\n"
        for row in self.rows:
            text = text + row.to_text() + "\n"
        return text
                   
    def to_html(self, include_children=False, recurse=False):
        """
        Returns html for a <table> with html from all the rows in the table as <tr>
        """
        html_str = "<table>"
        for header in self.headers:
            html_str = html_str + header.to_html()
        for row in self.rows:
            html_str = html_str + row.to_html()
        html_str = html_str + "</table>"
        return html_str

class LayoutReader:
    """
    Reads the layout tree from the json returned by the parser API.
    """
    def debug(self, pdf_root):
        def iter_children(node, level):
            for child in node.children:
                print("-"*level, child.tag, f"({len(child.children)})", child.to_text())
                iter_children(child, level + 1)
        iter_children(pdf_root, 0)

    def read(self, blocks_json):
        """
        Reads the layout tree from the json returned by the parser API. Constructs a tree of Block objects.
        """
        root = Block()
        parent = None
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
                    while len(parent_stack) > 1 and parent_stack.pop().level > node.level:
                        pass
                    parent_stack[-1].add_child(node)            
                    parent_stack.append(node)
                parent = node
            prev_node = node

        return root

class Document:
    """
    A document is a tree of blocks. It is the root node of the layout tree.
    """
    def __init__(self, blocks_json):
        self.reader = LayoutReader()
        self.root_node = self.reader.read(blocks_json)
        self.json = blocks_json
    def chunks(self):
        """
        Returns all the chunks in the document. Chunking automatically splits the document into paragraphs, lists, and tables without any prior knowledge of the document structure.
        """
        return self.root_node.chunks()
    def tables(self):
        """
        Returns all the tables in the document. This is useful for getting all the tables in a document.
        """
        return self.root_node.tables()
    def sections(self):
        """
        Returns all the sections in the document. This is useful for getting all the sections in a document.
        """
        return self.root_node.sections()
    def to_text(self):
        """
        Returns text of a document by iterating through all the sections '\n'
        """
        text = ""
        for section in self.sections():
            text = text + section.to_text(include_children=True, recurse=True) + "\n"
        return text
                   
    def to_html(self):
        """
        Returns html for the document by iterating through all the sections
        """
        html_str = "<html>"
        for section in self.sections():
            html_str = html_str + section.to_html(include_children=True, recurse=True)
        html_str = html_str + "</html>"
        return html_str
