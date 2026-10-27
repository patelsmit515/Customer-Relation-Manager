
import streamlit as st
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


# -----------------------------
# Helper functions
# -----------------------------
def show_dashboard():
    """Display CRM summary metrics."""
    leads = database.get_all_leads()

    total_leads = len(leads)
    new_leads = (
        int((leads["status"] == "New").sum())
        if not leads.empty else 0
    )
    contacted_leads = (
        int((leads["status"] == "Contacted").sum())
        if not leads.empty else 0
    )
    won_leads = (
        int((leads["status"] == "Won").sum())
        if not leads.empty else 0
    )

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
            "status",
            "source",
            "created_at",
        ]

        st.dataframe(
            leads[display_columns].head(10),
            use_container_width=True,
            hide_index=True,
        )


def add_lead_page():
    """Display the form for adding a lead."""
    st.title("Add New Lead")
    st.write("Enter the details of a potential customer.")

    with st.form("add_lead_form", clear_on_submit=True):
        name = st.text_input("Full Name *")
        company = st.text_input("Company")
        email = st.text_input("Email Address")
        phone = st.text_input("Phone Number")

        col1, col2 = st.columns(2)

        with col1:
            source = st.selectbox("Lead Source", LEAD_SOURCES)

        with col2:
            status = st.selectbox(
                "Lead Status",
                LEAD_STATUSES,
            )

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
                        source=source,
                        status=status,
                        notes=notes,
                    )

                    st.success(
                        f"Lead saved successfully! Lead ID: {lead_id}"
                    )

                except ValueError as error:
                    st.error(str(error))


def manage_leads_page():
    """Display, search, filter, edit, and delete leads."""
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

    with st.form("edit_lead_form"):
        edited_name = st.text_input(
            "Full Name *",
            value=str(selected_lead["name"] or ""),
        )
        edited_company = st.text_input(
            "Company",
            value=str(selected_lead["company"] or ""),
        )
        edited_email = st.text_input(
            "Email Address",
            value=str(selected_lead["email"] or ""),
        )
        edited_phone = st.text_input(
            "Phone Number",
            value=str(selected_lead["phone"] or ""),
        )

        current_source = selected_lead["source"]
        source_index = (
            LEAD_SOURCES.index(current_source)
            if current_source in LEAD_SOURCES else
            LEAD_SOURCES.index("Other")
        )

        edited_source = st.selectbox(
            "Lead Source",
            LEAD_SOURCES,
            index=source_index,
        )

        current_status = selected_lead["status"]
        status_index = (
            LEAD_STATUSES.index(current_status)
            if current_status in LEAD_STATUSES else 0
        )

        edited_status = st.selectbox(
            "Lead Status",
            LEAD_STATUSES,
            index=status_index,
        )

        edited_notes = st.text_area(
            "Notes",
            value=str(selected_lead["notes"] or ""),
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
