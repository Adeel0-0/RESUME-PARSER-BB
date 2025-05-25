# app.py
import streamlit as st
import json
from fpdf import FPDF
from parser import parse_resume
from utils.extract_pdf import extract_text_from_pdf
from utils.extract_docx import extract_text_from_docx
from utils.ocr import extract_text_from_image
from utils.job_finder import fetch_jobs

# Streamlit Config
st.set_page_config(page_title="Resume Parser", layout="wide")

# Custom CSS for better styling
st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    span.badge {
        background-color: transparent;
        padding: 5px 10px;
        border-radius: 10px;
        margin: 3px;
        display: inline-block;
        font-size: 0.9rem;
        border: 1px solid #ccc;
    }
    </style>
""", unsafe_allow_html=True)

# App Title
st.title("📄 Resume Parser with ChatGPT + Job Suggestions")

# File Upload
uploaded = st.file_uploader("Upload a resume (PDF, DOCX, JPG/PNG)", type=["pdf", "docx", "png", "jpg"])
if uploaded:
    with open("temp_" + uploaded.name, "wb") as f:
        f.write(uploaded.getbuffer())

    ext = uploaded.name.split('.')[-1].lower()
    if ext == "pdf":
        raw_text = extract_text_from_pdf("temp_" + uploaded.name)
    elif ext == "docx":
        raw_text = extract_text_from_docx("temp_" + uploaded.name)
    else:
        raw_text = extract_text_from_image("temp_" + uploaded.name)

    st.subheader("🔍 Extracted Text")
    st.text_area("", raw_text, height=200)

    if st.button("Parse with ChatGPT"):
        with st.spinner("Parsing…"):
            result = parse_resume(raw_text)
            st.subheader("📑 Resume Summary")

            if "error" in result:
                st.error(result["error"])
                st.text(result["raw_response"])
            else:
                st.markdown("### 🛠 Raw Parsed Fields")
                st.json(result)

                def get_field(field_names):
                    for key in result.keys():
                        for name in field_names:
                            if name.lower() in key.lower().replace("_", "").replace(" ", ""):
                                return result[key]
                    return "N/A"

                # 👤 Profile Info
                st.markdown("### 👤 Candidate Profile")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Name:** {get_field(['name'])}")
                    st.markdown(f"**Email:** {get_field(['email'])}")
                    st.markdown(f"**Phone:** {get_field(['phone'])}")
                    st.markdown(f"**Location:** {get_field(['location', 'address'])}")
                with col2:
                    st.markdown("")

                # 🛠️ Skills
                st.markdown("### 🛠️ Skills")
                skills = get_field(['skills'])
                if isinstance(skills, str):
                    skills = [s.strip() for s in skills.split(',')]
                skill_html = " ".join([f"<span class='badge'>{s}</span>" for s in skills])
                st.markdown(skill_html, unsafe_allow_html=True)

                # 🎓 Education
                st.markdown("### 🎓 Education")
                education = get_field(['education'])
                if isinstance(education, str):
                    st.markdown(education)
                elif isinstance(education, list):
                    for edu in education:
                        st.markdown(f"- {edu}")
                else:
                    st.write(education)

                # 💻 Projects
                st.markdown("### 💻 Projects")
                projects = get_field(['projects'])
                if isinstance(projects, str):
                    st.markdown(projects)
                elif isinstance(projects, list):
                    for proj in projects:
                        st.markdown(f"- {proj}")
                else:
                    st.write(projects)

                # 📜 Certifications
                st.markdown("### 📜 Certifications")
                certs = get_field(['certifications', 'certs'])
                if isinstance(certs, str):
                    st.markdown(certs)
                elif isinstance(certs, list):
                    for c in certs:
                        st.markdown(f"- {c}")
                else:
                    st.write(certs)

                # 🧩 Extracurricular Activities
                st.markdown("### 🧩 Extracurricular Activities")
                extra = get_field(['extracurriculars', 'activities'])
                if isinstance(extra, str):
                    st.markdown(extra)
                elif isinstance(extra, list):
                    for e in extra:
                        st.markdown(f"- {e}")
                else:
                    st.write(extra)

                # 💼 Job Suggestions
                st.markdown("### 💼 Top Job Suggestions")
                location = get_field(['location', 'address'])
                jobs = fetch_jobs(skills, location)

                for job in jobs:
                    if "error" in job:
                        st.error(job["error"])
                    else:
                        st.markdown(f"**🧑‍💼 {job['title']}** at `{job['company']}`")
                        st.markdown(f"🌍 Location: {job['location']}")
                        st.markdown(f"[🔗 View Job Posting]({job['url']})\n")

                # 📥 Download Section
                st.markdown("### 📥 Download Resume Data")

                # JSON Download
                st.download_button("📄 Download JSON", json.dumps(result, indent=2), file_name="parsed_resume.json")

                # Fix for PDF Unicode Error
                def sanitize_text(text):
                    return (
                        str(text)
                        .replace("–", "-")
                        .replace("—", "-")
                        .replace("•", "*")
                        .replace("’", "'")
                        .replace("“", '"')
                        .replace("”", '"')
                        .replace("\u2022", "*")
                        .encode("latin-1", errors="replace")
                        .decode("latin-1")
                    )

                # PDF Download
                def generate_pdf_from_result(result: dict) -> bytes:
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    pdf.cell(200, 10, txt="Resume Summary", ln=True, align='C')
                    pdf.ln(10)

                    for key, value in result.items():
                        sanitized_key = sanitize_text(key)
                        if isinstance(value, list):
                            pdf.multi_cell(0, 10, f"{sanitized_key}:", align="L")
                            for item in value:
                                pdf.multi_cell(0, 10, f"- {sanitize_text(item)}", align="L")
                        else:
                            pdf.multi_cell(0, 10, f"{sanitized_key}: {sanitize_text(value)}", align="L")
                        pdf.ln(4)

                    return bytes(pdf.output(dest='S').encode('latin-1'))

                pdf_bytes = generate_pdf_from_result(result)
                st.download_button("🧾 Download PDF", data=pdf_bytes, file_name="parsed_resume.pdf", mime="application/pdf")

                # Clean up temporary file
                import os                                                                                                                                                                       
                os.remove("temp_" + uploaded.name)
                st.success("Temporary file cleaned up.")
                st.balloons()
                st.info("You can now use the parsed data for further processing or job applications.")
                st.markdown("Thank you for using the Resume Parser! If you have any feedback, please let us know.")
                st.markdown("Made  by [SYED MOHAMMAD ADEEL](https://github.com/Adeel0-0)")
              

# Footer
st.markdown("""
    <style>
    footer {
        text-align: center;
        padding: 1rem;
        background-color: #f1f1f1;
        border-top: 1px solid #ccc;
    }
    </style>
""", unsafe_allow_html=True)