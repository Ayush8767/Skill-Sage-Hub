import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from wordcloud import WordCloud
import plotly.express as px
from fpdf import FPDF

# --------------------------
# Predefined Data
# --------------------------
job_roles = {
    "Data Analyst": ["Python", "SQL", "Excel", "Power BI", "Statistics"],
    "AI/ML Engineer": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch"],
    "Web Developer": ["HTML", "CSS", "JavaScript", "React", "SQL"],
    "Software Engineer": ["Java", "C++", "Data Structures", "Algorithms"],
}

learning_links = {
    "Python": "https://www.coursera.org/learn/python",
    "SQL": "https://www.w3schools.com/sql/",
    "Excel": "https://www.microsoft.com/en-us/learning/excel-training.aspx",
    "Power BI": "https://learn.microsoft.com/en-us/power-bi/",
    "Statistics": "https://www.khanacademy.org/math/statistics-probability",
    "Machine Learning": "https://www.coursera.org/learn/machine-learning",
    "Deep Learning": "https://www.deeplearning.ai/",
    "TensorFlow": "https://www.tensorflow.org/learn",
    "PyTorch": "https://pytorch.org/tutorials/",
    "HTML": "https://www.w3schools.com/html/",
    "CSS": "https://www.w3schools.com/css/",
    "JavaScript": "https://www.w3schools.com/js/",
    "React": "https://reactjs.org/tutorial/tutorial.html",
    "Java": "https://www.w3schools.com/java/",
    "C++": "https://www.learncpp.com/",
    "Data Structures": "https://www.geeksforgeeks.org/data-structures/",
    "Algorithms": "https://www.geeksforgeeks.org/fundamentals-of-algorithms/"
}

all_skills = sorted({skill for skills in job_roles.values() for skill in skills})

interview_qs = {
    "Data Analyst": ["Explain a project where you analyzed data.", "How do you handle missing data?", "Explain SQL joins."],
    "AI/ML Engineer": ["Describe a machine learning project you built.", "Explain overfitting and how to prevent it.", "Difference between supervised and unsupervised learning."],
    "Web Developer": ["Explain a project using React.", "How do you optimize website performance?", "Difference between REST and GraphQL."],
    "Software Engineer": ["Explain a complex algorithm you implemented.", "What is OOP and its principles?", "How do you debug code efficiently?"]
}

# --------------------------
# Helper Functions
# --------------------------
def extract_text_from_pdf(uploaded_file):
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_skills(text):
    text_lower = text.lower()
    found = [skill for skill in all_skills if skill.lower() in text_lower]
    return sorted(list(set(found)))

def suggest_skills(found_skills, target_role):
    role_skills = job_roles.get(target_role, [])
    missing = [s for s in role_skills if s not in found_skills]
    return missing

def generate_wordcloud(skills_list):
    if skills_list:
        wc = WordCloud(width=800, height=400, background_color="white").generate(" ".join(skills_list))
        plt.figure(figsize=(10,5))
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        st.pyplot(plt)

# --------------------------
# Streamlit Page Config
# --------------------------
st.set_page_config(page_title="SkillSage Hub", page_icon="🧠", layout="wide")
st.title("🧠 SkillSage Hub")

# --------------------------
# Sidebar
# --------------------------
with st.sidebar:
    st.header("Navigation")
    option = st.radio("Select Module", [
        "📄 Resume Analysis",
        "✏️ Create Resume",
        "📊 Resume Comparison",
        "📚 Learning Hub",
        "🎤 Interview Prep Helper",
        "📝 Resume Optimization Tips"
    ])
    st.markdown("---")
    theme = st.radio("Theme", ["Light", "Dark"])

if theme == "Dark":
    st.markdown("<style>body{background-color:#0E1117;color:white;}</style>", unsafe_allow_html=True)

# --------------------------
# Module 1: Resume Analysis
# --------------------------
if option == "📄 Resume Analysis":
    st.subheader("Upload Resume(s) for Analysis")
    uploaded_files = st.file_uploader("Upload PDF(s)", type=["pdf"], accept_multiple_files=True)
    if uploaded_files:
        resume_results = []
        for file in uploaded_files:
            st.markdown(f"### 📄 {file.name} Analysis")
            target_role = st.selectbox(f"Select Target Job Role for {file.name}", list(job_roles.keys()), key=file.name)
            text = extract_text_from_pdf(file)
            skills = extract_skills(text)
            missing_skills = suggest_skills(skills, target_role)
            job_fit = int((len(skills)/len(job_roles[target_role]))*100) if job_roles[target_role] else 0

            resume_results.append({
                "Resume File": file.name,
                "Target Role": target_role,
                "Detected Skills": skills,
                "Missing Skills": missing_skills,
                "Job Fit (%)": job_fit
            })

            with st.expander(f"📋 {file.name} Details", expanded=True):
                col1, col2 = st.columns([2,1])
                with col1:
                    st.markdown(f"**Target Role:** {target_role}")
                    st.markdown(f"✅ Detected Skills: {', '.join(skills) if skills else 'None'}")
                    st.markdown(f"❌ Missing Skills: {', '.join(missing_skills) if missing_skills else 'None'}")
                    st.markdown(
                        f"<div style='background-color:#ff4b4b;border-radius:5px;padding:2px;width:100%;'>"
                        f"<div style='background-color:#4CAF50;width:{job_fit}%;padding:5px;border-radius:5px;color:white;text-align:center;font-weight:bold;'>"
                        f"Job Fit: {job_fit}% | Missing Skills: {len(missing_skills)}"
                        f"</div></div>", unsafe_allow_html=True
                    )
                with col2:
                    if skills:
                        skill_counts = pd.Series(skills).value_counts().reset_index()
                        skill_counts.columns = ["Skill","Count"]
                        fig = px.bar(skill_counts, x="Skill", y="Count", text="Count")
                        fig.update_layout(title="Skill Count", xaxis_title="Skill", yaxis_title="Count")
                        st.plotly_chart(fig, use_container_width=True)

        # Skill Gap Tracker
        st.subheader("📊 Skill Gap Tracker")
        all_skills_union = sorted(list({s for r in resume_results for s in r["Missing Skills"]}))
        if all_skills_union:
            df_gap = pd.DataFrame(columns=["Resume"] + all_skills_union)
            for r in resume_results:
                row = {"Resume": r["Resume File"]}
                for skill in all_skills_union:
                    row[skill] = "❌" if skill in r["Missing Skills"] else "✅"
                df_gap = pd.concat([df_gap, pd.DataFrame([row])], ignore_index=True)
            st.dataframe(df_gap)
        else:
            st.info("No missing skills across uploaded resumes")

        # Word Cloud
        st.subheader("🌐 Overall Skills Word Cloud")
        overall_skills = sorted(list({s for r in resume_results for s in r["Detected Skills"]}))
        generate_wordcloud(overall_skills)

        # Learning Recommendations
        st.subheader("📚 Learning Recommendations")
        rec_table = []
        for skill in overall_skills:
            if skill in learning_links:
                rec_table.append({"Skill": skill, "Resource": learning_links[skill]})
        if rec_table:
            st.table(pd.DataFrame(rec_table))
        else:
            st.write("No recommendations available")

        # Download Reports
        report_csv = pd.DataFrame([
            {
                "Resume File": r["Resume File"],
                "Target Role": r["Target Role"],
                "Detected Skills": ", ".join(r["Detected Skills"]),
                "Missing Skills": ", ".join(r["Missing Skills"]),
                "Job Fit (%)": r["Job Fit (%)"]
            } for r in resume_results
        ])
        csv_buffer = BytesIO()
        report_csv.to_csv(csv_buffer, index=False)
        st.download_button("⬇️ Download CSV Report", csv_buffer, file_name="skill_report.csv", mime="text/csv")

        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
            report_csv.to_excel(writer, sheet_name="Skill Report", index=False)
        st.download_button("⬇️ Download Excel Report", excel_buffer, file_name="skill_report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# --------------------------
# Module 2: Create Resume
# --------------------------
elif option == "✏️ Create Resume":
    st.subheader("Create Your Resume")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    skills = st.multiselect("Select your skills", all_skills)
    target_job = st.selectbox("Target Job Role", list(job_roles.keys()))
    summary = st.text_area("Professional Summary / Objective")
    
    if st.button("Generate Resume PDF"):
        if not name or not email or not skills or not summary:
            st.warning("Please fill all fields to generate the resume.")
        else:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, f"{name}", ln=True, align="C")
            pdf.set_font("Arial", '', 12)
            pdf.cell(0, 10, f"Email: {email}", ln=True, align="C")
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, f"Target Job: {target_job}", ln=True)
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Professional Summary:", ln=True)
            pdf.set_font("Arial", '', 12)
            pdf.multi_cell(0, 8, summary)
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Skills:", ln=True)
            pdf.set_font("Arial", '', 12)
            pdf.multi_cell(0, 8, ", ".join(skills))
            
            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            st.download_button("⬇️ Download Resume PDF", pdf_bytes, file_name=f"{name}_resume.pdf", mime="application/pdf")
            st.success("Resume PDF generated successfully!")

# --------------------------
# Module 3: Resume Comparison
# --------------------------
elif option == "📊 Resume Comparison":
    uploaded_files = st.file_uploader("Upload two or more resumes", type=["pdf"], accept_multiple_files=True)
    if uploaded_files and len(uploaded_files) >= 2:
        resumes_data = []
        for file in uploaded_files:
            text = extract_text_from_pdf(file)
            skills = extract_skills(text)
            resumes_data.append({"file": file.name, "skills": skills})

        st.subheader("Comparison Table")
        all_skills_union = sorted(list({s for r in resumes_data for s in r["skills"]}))
        df = pd.DataFrame(columns=["Resume"] + all_skills_union)
        for r in resumes_data:
            row = {"Resume": r["file"]}
            for skill in all_skills_union:
                row[skill] = "✅" if skill in r["skills"] else "❌"
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        st.dataframe(df)
    else:
        st.info("Upload at least 2 resumes to compare.")

# --------------------------
# Module 4: Learning Hub
# --------------------------
elif option == "📚 Learning Hub":
    selected_skills = st.multiselect("Select your skills to get learning recommendations", all_skills)
    recommended = []
    for skill in selected_skills:
        if skill in learning_links:
            recommended.append({"Skill": skill, "Resource": learning_links[skill]})
    if recommended:
        st.table(pd.DataFrame(recommended))
    else:
        st.info("Select skills to see learning resources")

# --------------------------
# Module 5: Interview Prep Helper
# --------------------------
elif option == "🎤 Interview Prep Helper":
    target_job = st.selectbox("Select Target Job Role", list(job_roles.keys()))
    st.subheader(f"Common Interview Questions for {target_job}")
    for q in interview_qs.get(target_job, []):
        st.markdown(f"- {q}")

# --------------------------
# Module 6: Resume Optimization Tips
# --------------------------
elif option == "📝 Resume Optimization Tips":
    uploaded_file = st.file_uploader("Upload a resume PDF", type=["pdf"])
    if uploaded_file:
        text = extract_text_from_pdf(uploaded_file)
        skills = extract_skills(text)
        st.subheader("Detected Skills")
        st.write(", ".join(skills) if skills else "No skills detected")
        st.subheader("Optimization Tips")
        st.markdown("- Include missing keywords relevant to your target role.")
        st.markdown("- Use clear headings and bullet points.")
        st.markdown("- Keep professional summary concise and impactful.")
        st.markdown("- Highlight top skills at the top.")
        st.markdown("- Ensure formatting is ATS-friendly (avoid images for text).")


if __name__ == "__main__":
    import os
    import sys
    python_path = sys.executable  # Auto-detects your current Python path
    project_path = os.path.abspath(__file__)  # Gets current file’s full path
    os.system(f'"{python_path}" -m streamlit run "{project_path}"')
