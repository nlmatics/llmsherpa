import unittest
import json
import os
import re
from llmsherpa.readers import LayoutReader
from llmsherpa.readers import Document


class TestLayoutReader(unittest.TestCase):

    def clean_text(self, correct_text):
        correct_text = re.sub("\n *", "\n", correct_text)
        correct_text = re.sub("^\n", "", correct_text)
        correct_text = re.sub("\n$", "", correct_text)
        return correct_text

    def read_layout(self, file_name):
        with open(os.path.join(os.path.dirname(__file__), file_name)) as f:
            doc_data = json.load(f)
            reader = LayoutReader()
            doc = reader.read(doc_data)
        # reader.debug(pdf)
        return doc

    def get_document(self, file_name):
        with open(os.path.join(os.path.dirname(__file__), file_name)) as f:
            doc_data = json.load(f)
            doc = Document(doc_data)
        return doc

    def test_list_child_of_header(self):
        pdf = self.read_layout("list_test.json")
        self.assertEqual(len(pdf.children[0].children), 3)
        self.assertEqual(pdf.children[0].children[0].tag, "list_item")
        # self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")

    def test_list_child_of_para(self):
        doc = self.read_layout("list_test.json")
        self.assertEqual(doc.children[0].children[2].tag, "para")
        self.assertEqual(len(doc.children[0].children[2].children), 2)
        self.assertEqual(doc.children[0].children[2].children[0].tag, "list_item")

    def test_nested_lists(self):
        doc = self.read_layout("nested_list_test.json")
        self.assertEqual(len(doc.children[0].children), 2)
        self.assertEqual(len(doc.children[0].children[0].children), 2)
        self.assertEqual(len(doc.children[1].children[0].children[1].children), 2)
        parent_text = """
        Article II
        Section 1
        1.2 One point two
        """
        parent_text = self.clean_text(parent_text)
        self.assertEqual(
            doc.children[1].children[0].children[1].children[0].parent_text(),
            parent_text,
        )

    def test_nested_lists_with_para(self):
        doc = self.read_layout("nested_list_test.json")
        self.assertEqual(doc.children[2].children[0].tag, "para")
        self.assertEqual(len(doc.children[2].children), 2)
        self.assertEqual(len(doc.children[2].children[0].children), 2)
        self.assertEqual(doc.children[2].children[1].tag, "para")

    def test_nested_headers(self):
        doc = self.read_layout("header_test.json")
        self.assertEqual(len(doc.children[0].children), 2)
        self.assertEqual(len(doc.children[0].children[0].children), 2)
        self.assertEqual(len(doc.children[1].children[0].children[1].children), 2)
        self.assertEqual(
            doc.children[1].children[0].children[1].parent_text(),
            "Article II > Section 1",
        )

    def test_ooo_nested_headers(self):
        # OutOfOrder Header test case
        doc = self.read_layout("ooo_header_test.json")
        self.assertEqual(len(doc.children[0].children), 0)
        self.assertEqual(len(doc.children[1].children), 0)
        self.assertEqual(len(doc.children[2].children), 2)
        self.assertEqual(len(doc.children[2].children[0].children), 2)
        self.assertEqual(len(doc.children[3].children[0].children[1].children), 2)
        self.assertEqual(
            doc.children[3].children[0].children[1].parent_text(),
            "Article II > Section 1",
        )

    def test_ooo_nested_header_children(self):
        # OutOfOrder Header children test case
        doc = self.read_layout("ooo_header_child_test.json")
        self.assertEqual(len(doc.children[0].children), 0)
        self.assertEqual(len(doc.children[1].children), 3)
        self.assertEqual(len(doc.children[1].children[0].children), 0)
        self.assertEqual(len(doc.children[1].children[1].children), 2)
        self.assertEqual(len(doc.children[1].children[2].children), 3)
        self.assertEqual(len(doc.children[1].children[2].children[0].children), 0)

    def test_table(self):
        doc = self.read_layout("table_test.json")
        tables = doc.tables()
        correct_html = "<table><th><td colSpan=1></td><td colSpan=1>SQuAD 1.1 EM/F1</td><td colSpan=1>SQuAD 2.0 EM/F1</td><td colSpan=1>MNLI m/mm</td><td colSpan=1>SST Acc</td><td colSpan=1>QQP Acc</td><td colSpan=1>QNLI Acc</td><td colSpan=1>STS-B Acc</td><td colSpan=1>RTE Acc</td><td colSpan=1>MRPC Acc</td><td colSpan=1>CoLA Mcc</td></th><tr><td colSpan=1>BERT</td><td colSpan=1>84.1/90.9</td><td colSpan=1>79.0/81.8</td><td colSpan=1>86.6/-</td><td colSpan=1>93.2</td><td colSpan=1>91.3</td><td colSpan=1>92.3</td><td colSpan=1>90.0</td><td colSpan=1>70.4</td><td colSpan=1>88.0</td><td colSpan=1>60.6</td></tr><tr><td colSpan=1>UniLM</td><td colSpan=1>-/-</td><td colSpan=1>80.5/83.4</td><td colSpan=1>87.0/85.9</td><td colSpan=1>94.5</td><td colSpan=1>-</td><td colSpan=1>92.7</td><td colSpan=1>-</td><td colSpan=1>70.9</td><td colSpan=1>-</td><td colSpan=1>61.1</td></tr><tr><td colSpan=1>XLNet</td><td colSpan=1>89.0/94.5</td><td colSpan=1>86.1/88.8</td><td colSpan=1>89.8/-</td><td colSpan=1>95.6</td><td colSpan=1>91.8</td><td colSpan=1>93.9</td><td colSpan=1>91.8</td><td colSpan=1>83.8</td><td colSpan=1>89.2</td><td colSpan=1>63.6</td></tr><tr><td colSpan=1>RoBERTa</td><td colSpan=1>88.9/94.6</td><td colSpan=1>86.5/89.4</td><td colSpan=1>90.2/90.2</td><td colSpan=1>96.4</td><td colSpan=1>92.2</td><td colSpan=1>94.7</td><td colSpan=1>92.4</td><td colSpan=1>86.6</td><td colSpan=1>90.9</td><td colSpan=1>68.0</td></tr><tr><td colSpan=1>BART</td><td colSpan=1>88.8/94.6</td><td colSpan=1>86.1/89.2</td><td colSpan=1>89.9/90.1</td><td colSpan=1>96.6</td><td colSpan=1>92.5</td><td colSpan=1>94.9</td><td colSpan=1>91.2</td><td colSpan=1>87.0</td><td colSpan=1>90.4</td><td colSpan=1>62.8</td></tr></table>"
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0].to_html(), correct_html)

    def test_paragraph_iterator(self):
        doc = self.read_layout("nested_list_test.json")
        paras = doc.paragraphs()
        self.assertEqual(len(paras), 2)
        correct_text = """
        Following are our disclaimers:
        a) Disclaimer 1
        b) Disclaimer 2
        """
        correct_text = self.clean_text(correct_text)
        self.assertEqual(
            paras[0].to_text(include_children=True, recurse=True),
            correct_text.replace("  *", ""),
        )

    def test_chunk_iterator(self):
        doc = self.read_layout("chunk_test.json")
        chunks = doc.chunks()

        self.assertEqual(chunks[2].to_text(), "Article II")
        correct_text = """
        Article I
        Article II
        Section 1
        1.1 One point one
        1.2 One point two
        1.2.1 One point two point one
        1.2.2 One point two point two
        Section 2
        2.1 Two point one
        2.2 Two point two
        """
        correct_text = self.clean_text(correct_text)

        # context_text = "Article I\n" + correct_text
        self.assertEqual(chunks[2].to_context_text(), correct_text)
        correct_text = """
        Disclaimer
        Following are our disclaimers:
        a) Disclaimer 1
        b) Disclaimer 2
        """
        correct_text = self.clean_text(correct_text)
        self.assertEqual(chunks[3].to_context_text(), correct_text)

    def test_meta_data(self):
        doc = self.read_layout("table_test.json")
        chunks = doc.chunks()

        self.assertEqual(chunks[0].page_idx, 5)
        self.assertEqual(chunks[0].block_idx, 112)
        self.assertEqual(chunks[0].top, 64.8)
        self.assertEqual(chunks[0].left, 130.05)

    def test_to_text(self):
        doc = self.get_document("to_text_test.json")

        correct_text = "Lecture notes\nCS229\nPart VI\n"
        self.assertEqual(doc.to_text(), correct_text)

    def test_to_html(self):
        doc = self.get_document("to_html_test.json")

        correct_html = (
            "<html><h1>Heading 1</h1><h2>Heading 2</h2><h2>Heading 3</h2></html>"
        )
        self.assertEqual(doc.to_html(), correct_html)

    def test_to_markdown(self):
        doc = self.get_document("to_markdown_test.json")

        correct_markdown = (
            "# Heading 1\n\nParagraph 1\n## Heading 2\n\n## Heading 3\n\n\n"
        )
        self.assertEqual(doc.to_markdown(), correct_markdown)


if __name__ == "__main__":
    unittest.main()
