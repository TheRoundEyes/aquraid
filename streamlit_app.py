import streamlit as st
from PIL import Image
import fitz  # PyMuPDF
import pytesseract
import io
import time
import base64
from docx import Document  # Import Document class
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from streamlit_pdf_viewer import pdf_viewer

st.set_page_config(layout='wide')

openai_api_key = st.text_input('Enter your OPEN API Key here', type='password')

# Initialize the OpenAI embeddings if API key is provided
if openai_api_key:
    llm = OpenAI(api_key=openai_api_key)
    # Define the prompt template for comparison
    prompt_template = PromptTemplate(
        input_variables=["doc1", "doc2"],
        template="""Compare the following two documents and provide a detailed analysis:

        Document 1:
        {doc1}

        Document 2:
        {doc2}

        Please perform the following tasks:

        **Document Summaries:**
        1. Provide a summary of each document.

        **Key Differences:**
        1. Identify and list all the key differences between the two documents.

        **Proposal Form Verification:**
        1. Check if the proposal form is fully completed.
        2. Check if the proposal form is signed and dated.
        3. Verify if the date on the proposal form is prior to 30 days of the quotation.
        4. Determine if the business description provided is meaningful and compare if it matches or is similar to the Policy Schedule.
        5. Verify if turnover values for the current year, estimated next year, and previous year are declared. Display these values if present.

        For each of the above checks, indicate:
        - Yes/No for each point based on the content of the proposal form.

        **Risk Location Verification:**
        1. Verify if the proposal form contains a valid address.
        2. Check if the policy schedule shows the same address as the proposal form.
        3. Ensure that risk location details including factors like the location of properties, the policyholder’s usual residence, and the domicile of the company registration are accurately reflected.

        Provide the results in a clear and structured format, including a summary, a comparison section, and specific details for each verification point."""

    )

    ## Initialize the LLM chain with the prompt template
    chain = LLMChain(llm=llm, prompt=prompt_template)


    # Function to extract text from a PDF file

    def extract_text_from_pdf(file):
        text = ""
        pdf_document = fitz.open(stream=file.read(), filetype="pdf")
        num_pages = len(pdf_document)
        progress_bar = st.progress(0)

        for page_num in range(num_pages):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
            progress_bar.progress((page_num + 1) / num_pages)
            time.sleep(0.1)  # Simulate processing time

        return text


    # Function to extract text from a DOCX file
    def extract_text_from_docx(file):
        text = ""
        doc = Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text


    # Function to extract text from a TXT file
    def extract_text_from_txt(file):
        text = file.read().decode("utf-8")
        return text


    # Function to perform OCR on images
    def ocr_image(image):
        text = pytesseract.image_to_string(image)
        return text


    # Function to compare two documents using Langchain LLM
    def compare_documents(doc1, doc2):
        return chain.run({"doc1": doc1, "doc2": doc2})


    # Function to display PDF as HTML iframe
    # def display_pdf_iframe(uploaded_file):
    #     pdf_bytes_1 = uploaded_file_1.read()  # Convert to bytes
    #     pdf_viewer(pdf_bytes_1, height=600)

    # Function to display DOCX content
    def display_docx_content(text, key_suffix):
        st.text_area(f"DOCX Content {key_suffix}", text, height=600, key=f"docx_content_{key_suffix}")


    # Streamlit UI
    st.title("Aquraid")

    col1, col2,col3 = st.columns(2)

    with col1:
        uploaded_file_1 = st.file_uploader("Upload the Job Description", type=["pdf", "docx", "txt"], key="file1")
        uploaded_file_2 = st.file_uploader("Upload the Resume", type=["pdf", "docx", "txt"], key="file2")

        if uploaded_file_1:
            if uploaded_file_1.type == "application/pdf":
                st.write("Extracting text from the first PDF...")
                text_1 = extract_text_from_pdf(uploaded_file_1)
            elif uploaded_file_1.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                st.write("Extracting text from the first DOCX...")
                uploaded_file_1.seek(0)  # Reset file pointer before reading
                text_1 = extract_text_from_docx(uploaded_file_1)
            elif uploaded_file_1.type == "text/plain":
                st.write("Extracting text from the first TXT...")
                uploaded_file_1.seek(0)  # Reset file pointer before reading
                text_1 = extract_text_from_txt(uploaded_file_1)

        if uploaded_file_2:
            if uploaded_file_2.type == "application/pdf":
                st.write("Extracting text from the second PDF...")
                text_2 = extract_text_from_pdf(uploaded_file_2)
            elif uploaded_file_2.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                st.write("Extracting text from the second DOCX...")
                uploaded_file_2.seek(0)  # Reset file pointer before reading
                text_2 = extract_text_from_docx(uploaded_file_2)
            elif uploaded_file_2.type == "text/plain":
                st.write("Extracting text from the second TXT...")
                uploaded_file_2.seek(0)  # Reset file pointer before reading
                text_2 = extract_text_from_txt(uploaded_file_2)

        if uploaded_file_1 and uploaded_file_2:
            st.write("Comparing documents....")

            # Initialize the progress bar
            progress_bar = st.progress(0)

            # Simulate a lengthy process with incremental updates
            for i in range(1, 101):
                time.sleep(0.05)  # Simulate processing time
                progress_bar.progress(i)

            # Perform the document comparison
            comparison_result = compare_documents(text_1, text_2)

            # Close the progress bar
            progress_bar.empty()

            # Display the full comparison result in an expander
            with st.expander("Show Full Comparison Result"):
                st.write(comparison_result)

    with col2:
        if uploaded_file_1:
            if uploaded_file_1.type == "application/pdf":
                st.write("Displaying the first PDF:")
                uploaded_file_1.seek(0)  # Reset file pointer before displaying
                pdf_bytes_1 = uploaded_file_1.read()  # Convert to bytes
                pdf_viewer(pdf_bytes_1, height=600, key="pdf_viewer_1")  # Unique key for the first PDF
            elif uploaded_file_1.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                st.write("Displaying the first DOCX:")
                uploaded_file_1.seek(0)  # Reset file pointer before displaying
                text_1 = extract_text_from_docx(uploaded_file_1)
                display_docx_content(text_1, "1")
    with col3:
        if uploaded_file_2:
            if uploaded_file_2.type == "application/pdf":
                st.write("Displaying the second PDF:")
                uploaded_file_2.seek(0)  # Reset file pointer before displaying
                pdf_bytes_2 = uploaded_file_2.read()  # Convert to bytes
                pdf_viewer(pdf_bytes_2, height=600, key="pdf_viewer_2")  # Unique key for the second PDF
            elif uploaded_file_2.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                st.write("Displaying the second DOCX:")
                uploaded_file_2.seek(0)  # Reset file pointer before displaying
                text_2 = extract_text_from_docx(uploaded_file_2)
                display_docx_content(text_2, "2")

