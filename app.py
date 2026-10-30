
import streamlit as st
import pandas as pd
import database


# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="Customer Relationship Manager",
    page_icon="📊",
    layout="wide",
)

database.initialize_database()

LEAD_STATUSES = [
    "New",
    "Contacted",
    "Qualified",
    "Proposal",
    "Won",
    "Lost",
]

LEAD_SOURCES = [
    "Website",
    "WhatsApp",
    "Referral",
    "Social Media",
    "Cold Call",
    "Other",
]


def clean_str(val):
    """Safely convert database values (including None and NaN) to strings."""
    if val is None or pd.isna(val):
        return ""
    return str(val)


# -----------------------------
# Dashboard
# -----------------------------
def show_dashboard():
    leads = database.get_all_leads()

    total_leads = len(leads)
    new_leads = int((leads["status"] == "New").sum()) if not leads.empty else 0
    contacted_leads = int((leads["status"] == "Contacted").sum()) if not leads.empty else 0
    won_leads = int((leads["status"] == "Won").sum()) if not leads.empty else 0

    st.title("CRM Dashboard")
    st.write("An overview of your customer and sales leads.")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Leads", total_leads)
    col2.metric("New Leads", new_leads)
    col3.metric("Contacted", contacted_leads)
    col4.metric("Won Deals", won_leads)

    st.subheader("Recent Leads")

    if leads.empty:
        st.info("No leads yet. Add your first lead to get started.")
    else:
        display_columns = [
            "id",
            "name",
            "company",
            "email",
            "phone",
            "whatsapp_number",
            "status",
            "source",
            "created_at",
        ]

        st.dataframe(
            leads[display_columns],
            use_container_width=True,
            hide_index=True,
        )


# -----------------------------
# Add lead
# -----------------------------
def add_lead_page():
    st.title("Add New Lead")
    st.write("Enter the details of a potential customer.")

    with st.form("add_lead_form", clear_on_submit=True):
        name = st.text_input("Full Name *")
        company = st.text_input("Company")
        email = st.text_input("Email Address")

        col1, col2 = st.columns(2)

        with col1:
            phone = st.text_input("Phone Number (Calls)")

        with col2:
            whatsapp_number = st.text_input("WhatsApp Number")

        col3, col4 = st.columns(2)

        with col3:
            source = st.selectbox("Lead Source", LEAD_SOURCES)

        with col4:
            status = st.selectbox("Lead Status", LEAD_STATUSES)

        notes = st.text_area("Notes")

        submitted = st.form_submit_button(
            "Save Lead",
            use_container_width=True,
        )

        if submitted:
            if not name.strip():
                st.error("Please enter the lead's name.")
            elif email.strip() and (
                "@" not in email.strip()
                or "." not in email.strip().split("@")[-1]
            ):
                st.error("Please enter a valid email address.")
            else:
                try:
                    lead_id = database.add_lead(
                        name=name,
                        company=company,
                        email=email,
                        phone=phone,
                        whatsapp_number=whatsapp_number,
                        source=source,
                        status=status,
                        notes=notes,
                    )

                    st.success(
                        f"Lead saved successfully! Lead ID: {lead_id}"
                    )

                except ValueError as error:
                    st.error(str(error))


# -----------------------------
# Manage leads
# -----------------------------
def manage_leads_page():
    st.title("Manage Leads")
    st.write("Search and manage your saved leads.")

    search_text = st.text_input(
        "Search leads",
        placeholder="Search by name, company, email, or phone",
    )

    status_filter = st.selectbox(
        "Filter by status",
        ["All"] + LEAD_STATUSES,
    )

    leads = database.search_leads(
        search_text=search_text,
        status=status_filter,
    )

    st.caption(f"{len(leads)} lead(s) found")

    if leads.empty:
        st.info("No matching leads found.")
        return

    display_columns = [
        "id",
        "name",
        "company",
        "email",
        "phone",
        "whatsapp_number",
        "source",
        "status",
        "created_at",
    ]

    st.dataframe(
        leads[display_columns],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.subheader("Edit or Delete a Lead")

    lead_ids = leads["id"].astype(int).tolist()

    selected_id = st.selectbox(
        "Select a lead ID",
        lead_ids,
        format_func=lambda lead_id: (
            f"ID {lead_id} — "
            f"{leads.loc[leads['id'] == lead_id, 'name'].iloc[0]}"
        ),
    )

    selected_lead = leads.loc[
        leads["id"] == selected_id
    ].iloc[0]

    # Quick action for direct WhatsApp chat
    wa_num = clean_str(selected_lead.get("whatsapp_number")) or clean_str(selected_lead.get("phone"))
    clean_digits = "".join(filter(str.isdigit, wa_num))
    if clean_digits:
        st.markdown(
            f'<a href="https://wa.me/{clean_digits}" target="_blank" '
            f'style="display:inline-block;padding:7px 15px;background-color:#25D366;color:white;border-radius:6px;text-decoration:none;font-weight:600;font-size:14px;margin-bottom:12px;">'
            f'💬 Open WhatsApp Chat ({wa_num})</a>',
            unsafe_allow_html=True,
        )

    with st.form("edit_lead_form"):
        edited_name = st.text_input(
            "Full Name *",
            value=clean_str(selected_lead["name"]),
        )
        edited_company = st.text_input(
            "Company",
            value=clean_str(selected_lead["company"]),
        )
        edited_email = st.text_input(
            "Email Address",
            value=clean_str(selected_lead["email"]),
        )

        col1, col2 = st.columns(2)

        with col1:
            edited_phone = st.text_input(
                "Phone Number (Calls)",
                value=clean_str(selected_lead["phone"]),
            )

        with col2:
            edited_whatsapp_number = st.text_input(
                "WhatsApp Number",
                value=clean_str(selected_lead.get("whatsapp_number")),
                help="WhatsApp number with country code",
            )

        current_source = selected_lead["source"]
        source_index = (
            LEAD_SOURCES.index(current_source)
            if current_source in LEAD_SOURCES
            else LEAD_SOURCES.index("Other")
        )

        edited_source = st.selectbox(
            "Lead Source",
            LEAD_SOURCES,
            index=source_index,
        )

        current_status = selected_lead["status"]
        status_index = (
            LEAD_STATUSES.index(current_status)
            if current_status in LEAD_STATUSES
            else 0
        )

        edited_status = st.selectbox(
            "Lead Status",
            LEAD_STATUSES,
            index=status_index,
        )

        edited_notes = st.text_area(
            "Notes",
            value=clean_str(selected_lead["notes"]),
        )

        update_submitted = st.form_submit_button(
            "Update Lead",
            use_container_width=True,
        )

        if update_submitted:
            if not edited_name.strip():
                st.error("The lead's name is required.")
            elif edited_email.strip() and (
                "@" not in edited_email.strip()
                or "." not in edited_email.strip().split("@")[-1]
            ):
                st.error("Please enter a valid email address.")
            else:
                try:
                    database.update_lead(
                        lead_id=int(selected_id),
                        name=edited_name,
                        company=edited_company,
                        email=edited_email,
                        phone=edited_phone,
                        whatsapp_number=edited_whatsapp_number,
                        source=edited_source,
                        status=edited_status,
                        notes=edited_notes,
                    )

                    st.success("Lead updated successfully.")
                    st.rerun()

                except ValueError as error:
                    st.error(str(error))

    with st.expander("Delete this lead"):
        st.warning(
            "Deleting a lead permanently removes it from the database."
        )

        confirm_delete = st.checkbox(
            f"Confirm deletion of lead ID {selected_id}"
        )

        if st.button(
            "Delete Lead",
            type="secondary",
            disabled=not confirm_delete,
        ):
            try:
                database.delete_lead(int(selected_id))
                st.success("Lead deleted successfully.")
                st.rerun()

            except ValueError as error:
                st.error(str(error))


# -----------------------------
# Sidebar navigation
# -----------------------------
st.sidebar.title("Customer CRM")
st.sidebar.caption("Small Business Edition")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Add Lead",
        "Manage Leads",
    ],
)

st.sidebar.divider()
st.sidebar.caption("Built with Python, Streamlit, and SQLite")


# -----------------------------
# Display selected page
# -----------------------------
if page == "Dashboard":
    show_dashboard()
elif page == "Add Lead":
    add_lead_page()
elif page == "Manage Leads":
    manage_leads_page()
