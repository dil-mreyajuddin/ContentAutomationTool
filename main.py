import os
import tempfile
import pandas as pd
import streamlit as st
from business_logic import pdf_operations, aws_operations, automation

st.set_page_config(page_title="Content Extraction Automation Tool", page_icon=":robot:", layout="wide")
# Add logo and title to header
st.markdown(
    """
    <div class="header">
    <img src="https://www.diligent.com/_next/image?url=%2Flogo%2Fdiligent_logo_fullcolor_rgb.svg&w=256&q=75" style="width: 100px; height: auto;">
    <h1>Compliance Content Automation Tool</h1>
</div>
    """,
    unsafe_allow_html=True
)
try:
    uploaded_file = st.file_uploader("Upload a PDF file", type=['pdf'])
    start_page = st.number_input("Start Page", value=1, min_value=1)
    end_page = st.number_input("End Page", value=1, min_value=1)
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        if st.button("Process PDF"):
            # Split the PDF into images
            output_folder = pdf_operations.split_pdf(tmp_file_path, start_page, end_page)
            progress_bar = st.progress(0)
            text = ''
            num_files = len(os.listdir(output_folder))
            for i, filename in enumerate(os.listdir(output_folder)):
                page_content = aws_operations.perform_aws_ocr(output_folder, uploaded_file.name, filename)
                text = text + page_content
                progress_bar.progress((i + 1) / num_files, f"Processing page {i + 1} of {num_files}")
            # Perform automation
            with open(f"text.txt", "w") as file:
                file.write(text)
            automation.generate_excel_from_content(text)
            st.success("PDF processed successfully and Excel Template Generated Successfully.")
            st.markdown(
                """
                <div style="display: flex; flex-direction: column; align-items: center; text-align: center;">
                    <div class="header">
                        <img src="https://media1.tenor.com/m/TnQguYlVipYAAAAd/friends-phoebe.gif" style="width: 500px; height: 200px;">
                        <h2>You just saved enough time to binge-watch FRIENDS again!</h2>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            excel_file_path = "ocr_framework1.xlsx"
            if os.path.exists(excel_file_path):
                st.write("Excel Sheets:")
                excel_file = pd.ExcelFile(excel_file_path)
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)
                    st.write(f"**{sheet_name}**:")
                    st.write(df)
                # Download button for Excel file
                st.download_button(
                    label="Download Excel",
                    data=open(excel_file_path, "rb").read(),
                    file_name="generated_excel.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
except Exception as e:
    st.exception(f"Error Processing the PDF file: {e}")
