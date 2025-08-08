
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# App configuration
st.set_page_config(page_title="AVD Cost Estimator", layout="wide")

# Styling to match 3rdmill.tech
st.markdown("""
    <style>
        body {
            background-color: #f4f4f4;
            color: #333;
        }
        .stButton>button {
            background-color: #0078d4;
            color: white;
        }
        .stSlider>div>div {
            background-color: #0078d4;
        }
    </style>
""", unsafe_allow_html=True)

st.title("AVD Cost Estimator (Australia)")

# Sidebar inputs
st.sidebar.header("Configuration")

user_count = st.sidebar.slider("Number of Users", 10, 500, 10, step=10)

vm_options = {
    "B4ms": {"vCPU": 4, "RAM": 16, "Cost": 0.15},
    "D4s_v5": {"vCPU": 4, "RAM": 16, "Cost": 0.20},
    "D4dls_v5": {"vCPU": 4, "RAM": 16, "Cost": 0.22},
    "D4as_v5": {"vCPU": 4, "RAM": 16, "Cost": 0.21},
    "D8s_v5": {"vCPU": 8, "RAM": 32, "Cost": 0.40},
    "D8dls_v5": {"vCPU": 8, "RAM": 32, "Cost": 0.44},
    "D8as_v5": {"vCPU": 8, "RAM": 32, "Cost": 0.42},
    "E4s_v5": {"vCPU": 4, "RAM": 32, "Cost": 0.25},
    "E4dls_v5": {"vCPU": 4, "RAM": 32, "Cost": 0.27},
    "E4as_v5": {"vCPU": 4, "RAM": 32, "Cost": 0.26},
    "E8s_v5": {"vCPU": 8, "RAM": 64, "Cost": 0.50},
    "E8dls_v5": {"vCPU": 8, "RAM": 64, "Cost": 0.54},
    "E8as_v5": {"vCPU": 8, "RAM": 64, "Cost": 0.52}
}

vm_choice = st.sidebar.selectbox("Select VM Size", list(vm_options.keys()))
vm_info = vm_options[vm_choice]

fslogix_enabled = st.sidebar.checkbox("Include FSLogix", value=True)
fslogix_size = st.sidebar.slider("FSLogix Profile Size (GB)", 5, 100, 30, step=5) if fslogix_enabled else 0

os_disk_size = st.sidebar.slider("OS Disk Size (GB)", 64, 512, 128, step=32)

nat_gateway = st.sidebar.checkbox("Include NAT Gateway", value=True)
management_server = st.sidebar.checkbox("Include Management Server", value=True)
law_enabled = st.sidebar.checkbox("Include Log Analytics Workspace", value=False)

# Cost calculations
vm_cost = user_count * vm_info["Cost"] * 8 * 22  # 8 hours/day, 22 days/month
storage_cost = user_count * fslogix_size * 0.12 if fslogix_enabled else 0
os_disk_cost = user_count * os_disk_size * 0.10 / 128  # base cost for 128GB
nat_cost = 100 if nat_gateway else 0
mgmt_cost = 200 if management_server else 0
law_cost = 50 if law_enabled else 0
license_cost = user_count * 9  # Microsoft Business Standard AUD

total_cost = vm_cost + storage_cost + os_disk_cost + nat_cost + mgmt_cost + law_cost + license_cost

# Display results
st.header("Cost Breakdown")
cost_data = {
    "VM Cost": vm_cost,
    "FSLogix Storage": storage_cost,
    "OS Disk": os_disk_cost,
    "NAT Gateway": nat_cost,
    "Management Server": mgmt_cost,
    "Log Analytics": law_cost,
    "Licensing": license_cost
}
df = pd.DataFrame.from_dict(cost_data, orient='index', columns=["Cost (AUD)"])
df["Cost (AUD)"] = df["Cost (AUD)"].round(2)
st.dataframe(df)

# Pie chart
fig, ax = plt.subplots()
ax.pie(df["Cost (AUD)"], labels=df.index, autopct='%1.1f%%', startangle=90)
ax.axis('equal')
st.pyplot(fig)

# Download options
csv = df.to_csv().encode('utf-8')
st.download_button("Download CSV", csv, "avd_cost_breakdown.csv", "text/csv")

from fpdf import FPDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="AVD Cost Breakdown", ln=True, align='C')
for index, row in df.iterrows():
    pdf.cell(200, 10, txt=f"{index}: AUD {row['Cost (AUD)']}", ln=True)
pdf.output("avd_cost_breakdown.pdf")
with open("avd_cost_breakdown.pdf", "rb") as f:
    st.download_button("Download PDF", f, "avd_cost_breakdown.pdf", "application/pdf")
