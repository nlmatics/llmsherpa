# LLM Sherpa

LLM Sherpa provides strategic APIs to accelerate large language model (LLM) use cases.

## LayoutPDFReader

Most PDF to text parsers do not provide layout information. Often times, even the sentences are split with arbritrary CR/LFs making it very difficult to find paragraph boundaries. This poses various challenges in chunking and adding long running contextual information such as section header to the passages while indexing/vectorizing PDFs for LLM applications such as retrieval augmented generation (RAG). 

LayoutPDFReader solves this problem by parsing PDFs along with hierarchical layout information such as:

1. Sections and subsections along with their levels.
2. Paragraphs - combines lines.
3. Links between sections and paragraphs.
4. Tables along with the section the tables are found in.
5. Lists and nested lists.
6. Join content spread across pages.
7. Removal of repeating headers and footers.
8. Watermark removal.

With LayoutPDFReader, developers can find optimal chunks of text to vectorize, and a solution for limited context window sizes of LLMs. 

You can experiment with the library directly in Google Colab [here](https://colab.research.google.com/drive/1hx5Y2TxWriAuFXcwcjsu3huKyn39Q2id?usp=sharing)

Here's a [writeup](https://open.substack.com/pub/ambikasukla/p/efficient-rag-with-document-layout?r=ft8uc&utm_campaign=post&utm_medium=web) explaining the problem and our approach. 

Here'a LlamaIndex [blog](https://medium.com/@kirankurup/mastering-pdfs-extracting-sections-headings-paragraphs-and-tables-with-cutting-edge-parser-faea18870125) explaining the need for smart chunking. 

API Reference: [https://llmsherpa.readthedocs.io/](https://llmsherpa.readthedocs.io/)

### Important Notes

 * The LayoutPDFReader is tested on a wide variety of PDFs. That being said, it is still challenging to get every PDF parsed correctly.
* OCR is currently not supported. Only PDFs with a text layer are supported.

> [!NOTE]
> LLMSherpa uses a free and open api server. The server does not store your PDFs except for temporary storage during parsing.

> [!IMPORTANT]
> Private hosting is now available via [Microsoft Azure Marketplace](https://azuremarketplace.microsoft.com/en-us/marketplace/apps/nlmaticscorp1686371242615.layout_pdf_parser?tab=Overview)!


*For on premise hosting options, premium support or custom license options, create a custom licensing ticket [here](https://nlmatics.atlassian.net/servicedesk/customer/portals).*


### Installation

```bash
pip install llmsherpa
```

### Read a PDF file

The first step in using the LayoutPDFReader is to provide a url or file path to it and get back a document object.

```python
from llmsherpa.readers import LayoutPDFReader

llmsherpa_api_url = "https://readers.llmsherpa.com/api/document/developer/parseDocument?renderFormat=all"
pdf_url = "https://arxiv.org/pdf/1910.13461.pdf" # also allowed is a file path e.g. /home/downloads/xyz.pdf
pdf_reader = LayoutPDFReader(llmsherpa_api_url)
doc = pdf_reader.read_pdf(pdf_url)

```

### Install LlamaIndex

In the following examples, we will use [LlamaIndex](https://www.llamaindex.ai/) for simplicity. Install the library if you haven't already.

```bash
pip install llama-index
```

### Setup OpenAI

```python
import openai
openai.api_key = #<Insert API Key>
```

### Vector search and Retrieval Augmented Generation with Smart Chunking

LayoutPDFReader does smart chunking keeping related text due to document structure together:

* All list items are together including the paragraph that precedes the list.
* Items in a table are chuncked together
* Contextual information from section headers and nested section headers is included

The following code creates a LlamaIndex query engine from LayoutPDFReader document chunks

```python
from llama_index.readers.schema.base import Document
from llama_index import VectorStoreIndex

index = VectorStoreIndex([])
for chunk in doc.chunks():
    index.insert(Document(text=chunk.to_context_text(), extra_info={}))
query_engine = index.as_query_engine()
```

Let's run one query:

```python
response = query_engine.query("list all the tasks that work with bart")
print(response)
```

We get the following response:

```
BART works well for text generation, comprehension tasks, abstractive dialogue, question answering, and summarization tasks.
```

Let's try another query that needs answer from a table:

```python
response = query_engine.query("what is the bart performance score on squad")
print(response)
```

Here's the response we get:

```
The BART performance score on SQuAD is 88.8 for EM and 94.6 for F1.
```

### Summarize a Section using prompts

LayoutPDFReader offers powerful ways to pick sections and subsections from a large document and use LLMs to extract insights from a section.

The following code looks for the Fine-tuning section of the document:

```python
from IPython.core.display import display, HTML
selected_section = None
# find a section in the document by title
for section in doc.sections():
    if section.title == '3 Fine-tuning BART':
        selected_section = section
        break
# use include_children=True and recurse=True to fully expand the section. 
# include_children only returns at one sublevel of children whereas recurse goes through all the descendants
HTML(section.to_html(include_children=True, recurse=True))
```

Running the above code yields the following HTML output:

> <h3>3 Fine-tuning BART</h3><p>The representations produced by BART can be used in several ways for downstream applications.</p><h4>3.1 Sequence Classiﬁcation Tasks</h4><p>For sequence classiﬁcation tasks, the same input is fed into the encoder and decoder, and the ﬁnal hidden state of the ﬁnal decoder token is fed into new multi-class linear classiﬁer.\nThis approach is related to the CLS token in BERT; however we add the additional token to the end so that representation for the token in the decoder can attend to decoder states from the complete input (Figure 3a).</p><h4>3.2 Token Classiﬁcation Tasks</h4><p>For token classiﬁcation tasks, such as answer endpoint classiﬁcation for SQuAD, we feed the complete document into the encoder and decoder, and use the top hidden state of the decoder as a representation for each word.\nThis representation is used to classify the token.</p><h4>3.3 Sequence Generation Tasks</h4><p>Because BART has an autoregressive decoder, it can be directly ﬁne tuned for sequence generation tasks such as abstractive question answering and summarization.\nIn both of these tasks, information is copied from the input but manipulated, which is closely related to the denoising pre-training objective.\nHere, the encoder input is the input sequence, and the decoder generates outputs autoregressively.</p><h4>3.4 Machine Translation</h4><p>We also explore using BART to improve machine translation decoders for translating into English.\nPrevious work Edunov et al.\n(2019) has shown that models can be improved by incorporating pre-trained encoders, but gains from using pre-trained language models in decoders have been limited.\nWe show that it is possible to use the entire BART model (both encoder and decoder) as a single pretrained decoder for machine translation, by adding a new set of encoder parameters that are learned from bitext (see Figure 3b).</p><p>More precisely, we replace BART’s encoder embedding layer with a new randomly initialized encoder.\nThe model is trained end-to-end, which trains the new encoder to map foreign words into an input that BART can de-noise to English.\nThe new encoder can use a separate vocabulary from the original BART model.</p><p>We train the source encoder in two steps, in both cases backpropagating the cross-entropy loss from the output of the BART model.\nIn the ﬁrst step, we freeze most of BART parameters and only update the randomly initialized source encoder, the BART positional embeddings, and the self-attention input projection matrix of BART’s encoder ﬁrst layer.\nIn the second step, we train all model parameters for a small number of iterations.</p>

Now, let's create a custom summary of this text using a prompt:

```python
from llama_index.llms import OpenAI
context = selected_section.to_html(include_children=True, recurse=True)
question = "list all the tasks discussed and one line about each task"
resp = OpenAI().complete(f"read this text and answer question: {question}:\n{context}")
print(resp.text)
```

The above code results in following output:

```
Tasks discussed in the text:

1. Sequence Classification Tasks: The same input is fed into the encoder and decoder, and the final hidden state of the final decoder token is used for multi-class linear classification.
2. Token Classification Tasks: The complete document is fed into the encoder and decoder, and the top hidden state of the decoder is used as a representation for each word for token classification.
3. Sequence Generation Tasks: BART can be fine-tuned for tasks like abstractive question answering and summarization, where the encoder input is the input sequence and the decoder generates outputs autoregressively.
4. Machine Translation: BART can be used to improve machine translation decoders by incorporating pre-trained encoders and using the entire BART model as a single pretrained decoder. The new encoder parameters are learned from bitext.
```

### Analyze a Table using prompts

With LayoutPDFReader, you can iterate through all the tables in a document and use the power of LLMs to analyze a Table
Let's look at the 6th table in this document. If you are using a notebook, you can display the table as follows:

```python
from IPython.core.display import display, HTML
HTML(doc.tables()[5].to_html())
```
The output table structure looks like this:

|  | SQuAD 1.1 EM/F1 | SQuAD 2.0 EM/F1 | MNLI m/mm | SST Acc | QQP Acc | QNLI Acc | STS-B Acc | RTE Acc | MRPC Acc | CoLA Mcc
 | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
 | BERT | 84.1/90.9 | 79.0/81.8 | 86.6/- | 93.2 | 91.3 | 92.3 | 90.0 | 70.4 | 88.0 | 60.6
 | UniLM | -/- | 80.5/83.4 | 87.0/85.9 | 94.5 | - | 92.7 | - | 70.9 | - | 61.1
 | XLNet | 89.0/94.5 | 86.1/88.8 | 89.8/- | 95.6 | 91.8 | 93.9 | 91.8 | 83.8 | 89.2 | 63.6
 | RoBERTa | 88.9/94.6 | 86.5/89.4 | 90.2/90.2 | 96.4 | 92.2 | 94.7 | 92.4 | 86.6 | 90.9 | 68.0
 | BART | 88.8/94.6 | 86.1/89.2 | 89.9/90.1 | 96.6 | 92.5 | 94.9 | 91.2 | 87.0 | 90.4 | 62.8

Now let's ask a question to analyze this table:

```python
from llama_index.llms import OpenAI
context = doc.tables()[5].to_html()
resp = OpenAI().complete(f"read this table and answer question: which model has the best performance on squad 2.0:\n{context}")
print(resp.text)
```

The above question will result in the following output:
```
The model with the best performance on SQuAD 2.0 is RoBERTa, with an EM/F1 score of 86.5/89.4.
```

That's it! LayoutPDFReader also supports tables with nested headers and header rows.

Here's an example with nested headers:
```
from IPython.core.display import display, HTML
HTML(doc.tables()[6].to_html())
```

 |  | CNN/DailyMail |  |  | XSum |  | -
 | --- | --- | --- | --- | --- | --- | ---
  |  | R1 | R2 | RL | R1 | R2 | RL
 | --- | --- | --- | --- | --- | --- | ---
 | Lead-3 | 40.42 | 17.62 | 36.67 | 16.30 | 1.60 | 11.95
 | PTGEN (See et al., 2017) | 36.44 | 15.66 | 33.42 | 29.70 | 9.21 | 23.24
 | PTGEN+COV (See et al., 2017) | 39.53 | 17.28 | 36.38 | 28.10 | 8.02 | 21.72
 | UniLM | 43.33 | 20.21 | 40.51 | - | - | -
 | BERTSUMABS (Liu & Lapata, 2019) | 41.72 | 19.39 | 38.76 | 38.76 | 16.33 | 31.15
 | BERTSUMEXTABS (Liu & Lapata, 2019) | 42.13 | 19.60 | 39.18 | 38.81 | 16.50 | 31.27
 | BART | 44.16 | 21.28 | 40.90 | 45.14 | 22.27 | 37.25

Now let's ask an interesting question:

```python
from llama_index.llms import OpenAI
context = doc.tables()[6].to_html()
question = "tell me about R1 of bart for different datasets"
resp = OpenAI().complete(f"read this table and answer question: {question}:\n{context}")
print(resp.text)
```
And we get the following answer:

```
R1 of BART for different datasets:

- For the CNN/DailyMail dataset, the R1 score of BART is 44.16.
- For the XSum dataset, the R1 score of BART is 45.14.
```


### Get the Raw JSON

To get the complete json returned by llmsherpa service and process it differently, simply get the json attribute

```python
doc.json
```