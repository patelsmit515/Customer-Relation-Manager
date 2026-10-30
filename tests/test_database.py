import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import database


def main():
    database.initialize_database()
    print("Database initialized successfully.")

    # Add a sample lead
    lead_id = database.add_lead(
        name="Asha Patel",
        company="Demo Company",
        email="asha@example.com",
        phone="9876543210",
        whatsapp_number="9876543210",
        source="WhatsApp",
        status="New",
        notes="Interested in learning about our services.",
    )

    print(f"Sample lead added with ID: {lead_id}")

    # Display all leads
    print("\nAll leads:")
    print(database.get_all_leads().to_string(index=False))

    # Search leads
    print("\nSearch results for 'Asha':")
    print(database.search_leads("Asha").to_string(index=False))

    # Update the sample lead
    database.update_lead(
        lead_id=lead_id,
        name="Asha Patel",
        company="Demo Company",
        email="asha@example.com",
        phone="9876543210",
        whatsapp_number="9876543210",
        source="WhatsApp",
        status="Contacted",
        notes="Contacted for an initial discussion.",
    )

    print("\nAfter updating the lead:")
    print(database.search_leads("Asha").to_string(index=False))

    print("\nDatabase checks completed.")


if __name__ == "__main__":
    main()
