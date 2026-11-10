import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configure Page Layout
st.set_page_config(
    page_title="Label Quotation Request Manager",
    page_icon="🏷️",
    layout="wide"
)

st.title("🏷️ Label Quotation Request Manager")
st.markdown("Submit detailed label specifications to generate a prepress & production quotation.")

# Establish Connection to Google Sheets
# Uses .streamlit/secrets.toml for service account credentials
conn = st.connection("gsheets", type=GSheetsConnection)

# Form Section
with st.form("label_quote_form", clear_on_submit=True):
    st.subheader("1. Client Information")
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("Company / Client Name*")
        contact_person = st.text_input("Contact Person*")
    with col2:
        contact_email = st.text_input("Contact Email*")
        contact_phone = st.text_input("Contact Phone")

    st.subheader("2. Label & Job Specifications")
    label_desc = st.text_input("Label Description / Part Name* (e.g. 50ml Shampoo Front Label)")
    
    col3, col4, col5 = st.columns(3)
    with col3:
        print_process = st.selectbox(
            "Print Process",
            ["Digital (UV Inkjet)", "Flexographic", "Hybrid (Digital + Flexo)", "Screen Printing"]
        )
        substrate = st.selectbox(
            "Substrate / Material",
            [
                "White Polypropylene (PP)",
                "Clear Polypropylene (PP)",
                "Silver Metallic PP",
                "Semi-Gloss Paper",
                "Direct Thermal Paper",
                "Textured Wine Stock",
                "300µm PBL Laminate Roll",
                "Other (Specify in Notes)"
            ]
        )
    with col4:
        adhesive = st.selectbox(
            "Adhesive Type",
            ["Permanent Acrylic", "Removable", "Deep Freeze / Cold Temp", "High Tack", "Wash-off"]
        )
        format_type = st.radio("Supply Format", ["Rolls", "Sheets", "Individual Cut"], horizontal=True)

    with col5:
        finish = st.selectbox(
            "Protective Finish",
            ["None", "Gloss Varnish", "Matt Varnish", "Gloss Lamination", "Matt Lamination", "UV Spot Varnish"]
        )
        treatments = st.multiselect(
            "Special Enhancements",
            ["Cold Foil", "Hot Foil", "Embossing", "Silk Screen White", "Variable Data / Barcodes"]
        )

    st.subheader("3. Dimensions & Roll Specs")
    col6, col7, col8 = st.columns(3)
    with col6:
        width_mm = st.number_input("Width (mm)*", min_value=1.0, value=50.0, step=0.5)
        height_mm = st.number_input("Height / Die Length (mm)*", min_value=1.0, value=80.0, step=0.5)
        corner_radius = st.number_input("Corner Radius (mm)", min_value=0.0, value=2.0, step=0.5)

    with col7:
        core_size = st.selectbox("Core Size (mm)", [76, 40, 25])
        max_od = st.number_input("Max Outer Diameter (mm)", min_value=0, value=200, step=10)
    
    with col8:
        unwind_dir = st.selectbox(
            "Unwind Direction",
            ["Off-Top (Off Top First)", "Off-Bottom (Off Bottom First)", "Off-Right", "Off-Left"]
        )
        quantity_tiers = st.text_input("Quantity Tiers* (comma-separated, e.g. 5000, 10000, 25000)")

    st.subheader("4. Logistics & Special Instructions")
    col9, col10 = st.columns(2)
    with col9:
        spot_colors = st.text_input("Spot / PMS Colors (e.g. Pantone 286 C, Pantone Gold)")
        lead_time = st.number_input("Target Lead Time (Business Days)", min_value=1, value=5)
    with col10:
        delivery_location = st.text_input("Delivery Location / Destination")
        additional_notes = st.text_area("Additional Notes / Die-Line Details")

    # Form Submission Trigger
    submitted = st.form_submit_button("🚀 Submit Quotation Request", use_container_width=True)

if submitted:
    # Basic Form Validation
    if not client_name or not contact_email or not label_desc or not quantity_tiers:
        st.error("Please fill in all required fields marked with an asterisk (*).")
    else:
        try:
            # Prepare row data for Google Sheets
            new_row = {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Request ID": f"REQ-{int(datetime.now().timestamp())}",
                "Client / Company Name": client_name,
                "Contact Person": contact_person,
                "Contact Email": contact_email,
                "Contact Phone": contact_phone,
                "Label Description": label_desc,
                "Print Process (Digital/Flexo/Hybrid)": print_process,
                "Substrate / Material": substrate,
                "Adhesive Type": adhesive,
                "Width (mm)": width_mm,
                "Height (mm)": height_mm,
                "Corner Radius (mm)": corner_radius,
                "Roll or Sheet Format": format_type,
                "Core Size (mm)": core_size,
                "Max Outer Diameter (mm)": max_od,
                "Unwind Direction": unwind_dir,
                "Quantity Tiers": quantity_tiers,
                "Spot Colors / PMS": spot_colors,
                "Protective Finish (Varnish/Lamination)": finish,
                "Special Treatments (Foil/Emboss)": ", ".join(treatments) if treatments else "None",
                "Target Lead Time (Days)": lead_time,
                "Delivery Location": delivery_location,
                "Additional Notes": additional_notes
            }

            # Fetch existing data from sheet, append new row, and update Google Sheets
            existing_data = conn.read(ttl=0)
            updated_df = pd.concat([existing_data, pd.DataFrame([new_row])], ignore_index=True)
            conn.update(data=updated_df)

            st.success("✅ Quotation request submitted and logged successfully to Google Sheets!")
            st.balloons()
            
        except Exception as e:
            st.error(f"Failed to submit request: {e}")