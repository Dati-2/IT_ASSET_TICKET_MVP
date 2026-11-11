
import random
from datetime import date, timedelta
from database import get_connection

# Connect to the SQLite database
connection = get_connection()
cursor = connection.cursor()

# Prevent duplicate sample records
existing_users = cursor.execute(
    "SELECT COUNT(*) FROM users"
).fetchone()[0]

if existing_users > 0:
    print("Sample data already exists. No new records added.")
    connection.close()
    raise SystemExit

# Sample employee information
first_names = [
    "John", "Mary", "David", "Grace", "Peter",
    "Sarah", "Daniel", "Esther", "Michael", "Ruth",
    "James", "Faith", "Samuel", "Deborah", "Joseph"
]

last_names = [
    "Okon", "Bassey", "Ekanem", "Johnson", "Williams",
    "Brown", "Adams", "Obi", "Adebayo", "Okafor",
    "Mensah", "Ibrahim", "Bello", "Thomas", "George"
]

departments = [
    "Information Technology",
    "Human Resources",
    "Finance",
    "Operations",
    "Risk Management",
    "Customer Service",
    "Internal Audit",
    "Compliance",
    "Marketing",
    "Administration"
]

roles = ["Employee", "Employee", "Employee", "Manager"]

# 1. CREATE 600 EMPLOYEES
for i in range(1, 601):
    first = random.choice(first_names)
    last = random.choice(last_names)
    name = f"{first} {last}"

    email = f"employee{i:04d}@example.com"
    staff_code = f"EMP{i:04d}"
    department = random.choice(departments)
    role = random.choice(roles)

    cursor.execute("""
        INSERT INTO users
        (staff_code, name, email, department, role)
        VALUES (?, ?, ?, ?, ?)
    """, (staff_code, name, email, department, role))

# Get employee IDs
user_ids = [
    row[0] for row in
    cursor.execute("SELECT id FROM users").fetchall()
]

# 2. CREATE 500 IT ASSETS
asset_types = [
    "Laptop", "Desktop Computer", "Monitor",
    "Printer", "Keyboard", "Router", "Scanner"
]

for i in range(1, 501):
    category = random.choice(asset_types)
    name = f"{category} {i:03d}"
    tag = f"AST{i:04d}"
    serial = f"SN{i:06d}"

    number = random.random()

    if number < 0.75:
        assigned_to = random.choice(user_ids)
        status = "Assigned"
    elif number < 0.90:
        assigned_to = None
        status = "Available"
    elif number < 0.97:
        assigned_to = None
        status = "Under Maintenance"
    else:
        assigned_to = None
        status = "Retired"

    cursor.execute("""
        INSERT INTO assets
        (name, tag, serial, category, assigned_to, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, tag, serial, category, assigned_to, status))

# 3. CREATE 200 SUPPORT TICKETS
issues = [
    "Laptop not starting",
    "Network connection problem",
    "Printer not working",
    "Email access issue",
    "Slow computer performance",
    "Software installation request",
    "Monitor display problem",
    "Keyboard not responding",
    "System access request",
    "Internet connectivity issue"
]

priorities = ["Low", "Medium", "High", "Critical"]
statuses = ["Open", "In Progress", "Resolved", "Closed"]

today = date.today()

for i in range(1, 201):
    title = random.choice(issues)
    description = f"Sample support request: {title.lower()}."
    reported_by = random.choice(user_ids)
    priority = random.choice(priorities)
    status = random.choice(statuses)

    days_ago = random.randint(0, 365)
    raised_date = today - timedelta(days=days_ago)

    if status in ["Resolved", "Closed"]:
        days_until_resolution = random.randint(0, days_ago)
        resolved_date = raised_date + timedelta(
            days=days_until_resolution
        )
        resolution_notes = "Issue resolved by IT support."
        date_resolved = resolved_date.isoformat()
    else:
        resolution_notes = None
        date_resolved = None

    cursor.execute("""
        INSERT INTO tickets
        (title, description, reported_by, priority,
         status, date_raised, resolution_notes, date_resolved)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        title,
        description,
        reported_by,
        priority,
        status,
        raised_date.isoformat(),
        resolution_notes,
        date_resolved
    ))

# Save all records
connection.commit()

# Display the number of records created
print("DATABASE POPULATED SUCCESSFULLY!")
print("Employees:", cursor.execute(
    "SELECT COUNT(*) FROM users"
).fetchone()[0])

print("Assets:", cursor.execute(
    "SELECT COUNT(*) FROM assets"
).fetchone()[0])

print("Tickets:", cursor.execute(
    "SELECT COUNT(*) FROM tickets"
).fetchone()[0])

connection.close()
