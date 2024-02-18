from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import OpenAI, OpenAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()

def docVectorization(document, query):
    openAIKey = os.getenv('OPENAI_API_KEY')
    docReader = PdfReader(document)
    rawText = ''
    for i, page in enumerate(docReader.pages): 
        text = page.extract_text()
        if text:
            rawText += text
    # splitting text to smaller chunks
    textSplitter = CharacterTextSplitter(
        separator = '\n',
        chunk_size = 100,
        chunk_overlap = 50, # striding over text
        length_function = len,
    )
    texts = textSplitter.split_text(rawText)
    embeddings = OpenAIEmbeddings(openai_api_key=openAIKey)
    docsearch = FAISS.from_texts(texts, embeddings)
    chain = load_qa_chain(OpenAI(), 
                      chain_type="stuff") # we are going to stuff all the docs in at once
    docs = docsearch.similarity_search(query)
    #return chain.run(input_documents=docs, question=query)
    # Assuming that 'docs' is a list of documents and 'query' is your question
    input_data = {
        "input_documents": docs,
        "question": query,
    }

    # Then you call the 'invoke' method with this combined input
    result = chain.invoke(input=input_data)

    #result = chain.invoke(input_documents=docs, question=query)
    return result['output_text']

# Example usage
if __name__ == "__main__":
    document = '../assets/Sample EHR.pdf'
    query = 'I have severe back pain!'
    print(docVectorization(document, query))
