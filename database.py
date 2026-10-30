
import sqlite3
from pathlib import Path

import pandas as pd


# Project paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "crm.db"


def get_connection():
    """Create a connection to the SQLite database."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """Create the leads table and apply database migrations."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                company TEXT,
                email TEXT,
                phone TEXT,
                whatsapp_number TEXT,
                source TEXT,
                status TEXT NOT NULL DEFAULT 'New',
                notes TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Upgrade databases created before the WhatsApp field existed.
        columns = connection.execute(
            "PRAGMA table_info(leads)"
        ).fetchall()

        column_names = [column["name"] for column in columns]

        if "whatsapp_number" not in column_names:
            connection.execute(
                "ALTER TABLE leads ADD COLUMN whatsapp_number TEXT"
            )


def add_lead(
    name,
    company="",
    email="",
    phone="",
    whatsapp_number="",
    source="Other",
    status="New",
    notes="",
):
    """Add a new lead to the database."""
    name = name.strip()

    if not name:
        raise ValueError("Lead name is required.")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO leads (
                name,
                company,
                email,
                phone,
                whatsapp_number,
                source,
                status,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                company.strip(),
                email.strip(),
                phone.strip(),
                whatsapp_number.strip(),
                source,
                status,
                notes.strip(),
            ),
        )

        return cursor.lastrowid


def get_all_leads():
    """Return all leads as a pandas DataFrame."""
    with get_connection() as connection:
        return pd.read_sql_query(
            "SELECT * FROM leads ORDER BY id DESC",
            connection,
        )


def search_leads(search_text="", status="All"):
    """Search leads by name, company, email, or phone number."""
    query = """
        SELECT * FROM leads
        WHERE (
            name LIKE ?
            OR company LIKE ?
            OR email LIKE ?
            OR phone LIKE ?
            OR whatsapp_number LIKE ?
        )
    """

    search_pattern = f"%{search_text.strip()}%"
    parameters = [search_pattern] * 5

    if status != "All":
        query += " AND status = ?"
        parameters.append(status)

    query += " ORDER BY id DESC"

    with get_connection() as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=parameters,
        )


def update_lead(
    lead_id,
    name,
    company="",
    email="",
    phone="",
    whatsapp_number="",
    source="Other",
    status="New",
    notes="",
):
    """Update an existing lead."""
    name = name.strip()

    if not name:
        raise ValueError("Lead name is required.")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE leads
            SET name = ?,
                company = ?,
                email = ?,
                phone = ?,
                whatsapp_number = ?,
                source = ?,
                status = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                name,
                company.strip(),
                email.strip(),
                phone.strip(),
                whatsapp_number.strip(),
                source,
                status,
                notes.strip(),
                lead_id,
            ),
        )

        if cursor.rowcount == 0:
            raise ValueError(f"No lead found with ID {lead_id}.")


def delete_lead(lead_id):
    """Delete a lead by its ID."""
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM leads WHERE id = ?",
            (lead_id,),
        )

        if cursor.rowcount == 0:
            raise ValueError(f"No lead found with ID {lead_id}.")
