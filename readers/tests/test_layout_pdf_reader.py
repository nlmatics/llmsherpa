import unittest
import json
import os
from readers.layout_pdf_reader import LayoutPDFReader


class TestLayoutPDFReader(unittest.TestCase):

    def read_pdf(self, file_name):
        with open(os.path.join(os.path.dirname(__file__), file_name)) as f:
            pdf_data = json.load(f)
            reader = LayoutPDFReader()
            pdf = reader.read(pdf_data)
        # reader.debug(pdf)
        return pdf

    def test_list_child_of_header(self):
        pdf = self.read_pdf("list_test.json")
        self.assertEqual(len(pdf.children[0].children), 3)
        self.assertEqual(pdf.children[0].children[0].tag,  'list_item')
        # self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")

    def test_list_child_of_para(self):
        pdf = self.read_pdf("list_test.json")
        self.assertEqual(pdf.children[0].children[2].tag,  'para')
        self.assertEqual(len(pdf.children[0].children[2].children),  2)
        self.assertEqual(pdf.children[0].children[2].children[0].tag,  'list_item')

    def test_nested_lists(self):
        pdf = self.read_pdf("nested_list.json")
        self.assertEqual(len(pdf.children[0].children),  2)
        self.assertEqual(len(pdf.children[0].children[0].children),  2)
        self.assertEqual(len(pdf.children[1].children[0].children[1].children),  2)

    def test_nested_lists_with_para(self):
        pdf = self.read_pdf("nested_list.json")
        self.assertEqual(pdf.children[2].children[0].tag,  'para')
        self.assertEqual(len(pdf.children[2].children), 2)
        self.assertEqual(len(pdf.children[2].children[0].children),  2)
        self.assertEqual(pdf.children[2].children[1].tag,  'para')
 
    def test_nested_headers(self):
        pdf = self.read_pdf("header_test.json")
        self.assertEqual(len(pdf.children[0].children),  2)
        self.assertEqual(len(pdf.children[0].children[0].children),  2)
        self.assertEqual(len(pdf.children[1].children[0].children[1].children),  2)

if __name__ == '__main__':
    unittest.main()