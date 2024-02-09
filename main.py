import streamlit as st
from dotenv import load_dotenv
import pickle 
from PyPDF2 import PdfReader
from streamlit_extras.add_vertical_space import add_vertical_space
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
import os 

# Sidebar contents
with st.sidebar:
    st.title('LLM Chat Bot 4 PDF')
    st.markdown('''
    ## About
    This app is an LLM-powered chatbot built using:
    - [Streamlist](https://www.streamlit.io/)
    - [LangChain](http://langchain.org)
    - [OpenAI](https://openai.com/blog/gpt-3-launches/)
    ''')
    add_vertical_space(5)
    st.write('Made with <3')

load_dotenv()

def main():
    st.header("Chat with PDF!")


    # upload a PDF file
    pdf = st.file_uploader("Upload your PDF", type='pdf')

    ## st.write(pdf)
    if pdf is not None:
        pdf_reader = PdfReader(pdf)
 
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text=text)

        # embeddings

        store_name = pdf.name[:-4]

        if os.path.exists(f"{store_name}.pkl"):
            with open(f"{store_name}.pkl", "rb") as f:
                VectorStore = pickle.load(f)
            #st.write('Embeddings loaded from the Disk')
        else:
            embeddings = OpenAIEmbeddings()
            VectorStore = FAISS.from_texts(chunks, embedding=embeddings)
            with open(f"{store_name}.pkl", "wb") as f:
                pickle.dump(VectorStore, f)

        # accept user question/query

        query = st.text_input("Ask Questions about your PDF file:")               
        st.write(query)

        if query:
            docs = VectorStore.similarity_search(query=query, k=3)

            llm = OpenAI(model_name='gpt-3.5-turbo',
             temperature = 0,
             max_tokens = 256)
            chain = load_qa_chain(llm=llm, chain_type="stuff")
            with get_openai_callback() as cb:
                response = chain.run(input_documents=docs, question=query)
                print(cb)
            st.write(response)





if __name__ == '__main__':
    main()