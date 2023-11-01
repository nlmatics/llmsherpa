import urllib3
import os
import json
from urllib.parse import urlparse
from llmsherpa.readers import Document

class LayoutPDFReader:
    """
    Reads PDF content and understands hierarchical layout of the document sections and structural components such as paragraphs, sentences, tables, lists, sublists

    Parameters
    ----------
    parser_api_url: str
        API url for LLM Sherpa. Use customer url for your private instance here            
    
    """
    def __init__(self, parser_api_url):
        """
            Constructs a LayoutPDFReader from a parser endpoint.

            Parameters
            ----------
            parser_api_url: str
                API url for LLM Sherpa. Use customer url for your private instance here            
        """
        self.parser_api_url = parser_api_url
        self.download_connection = urllib3.PoolManager()
        self.api_connection = urllib3.PoolManager()

    def _download_pdf(self, pdf_url):
        
        # some servers only allow browers user_agent to download
        user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
        # add authorization headers if using external API (see upload_pdf for an example)
        download_headers = {"User-Agent": user_agent}
        download_response = self.download_connection.request("GET", pdf_url, headers=download_headers)
        file_name = os.path.basename(urlparse(pdf_url).path)
        # note you can change the file name here if you'd like to something else
        if download_response.status == 200:
            pdf_file = (file_name, download_response.data, 'application/pdf')
        return pdf_file

    def _parse_pdf(self, pdf_file):
        auth_header = {}
        parser_response = self.api_connection.request("POST", self.parser_api_url, fields={'file': pdf_file})
        return parser_response

    def read_pdf(self, path_or_url, contents=None):
        """
        Reads pdf from a url or path

        Parameters
        ----------
        path_or_url: str
            path or url to the pdf file e.g. https://someexapmple.com/myfile.pdf or /home/user/myfile.pdf
        contents: bytes
            contents of the pdf file. If contents is given, path_or_url is ignored. This is useful when you already have the pdf file contents in memory such as if you are using streamlit or flask.
        """
        # file contents were given
        if contents is not None:
            pdf_file = (path_or_url, contents, 'application/pdf')
        else:
            is_url = urlparse(path_or_url).scheme != ""
            if is_url:
                pdf_file = self._download_pdf(path_or_url)
            else:
                file_name = os.path.basename(path_or_url)
                with open(path_or_url, "rb") as f:
                    file_data = f.read()
                    pdf_file = (file_name, file_data, 'application/pdf')
        parser_response = self._parse_pdf(pdf_file)
        response_json = json.loads(parser_response.data.decode("utf-8"))
        blocks = response_json['return_dict']['result']['blocks']
        return Document(blocks)