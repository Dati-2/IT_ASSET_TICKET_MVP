
from flask import Flask, jsonify, request
from database import get_connection
import sqlite3

# Create Flask application
app = Flask(__name__)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response

# 1. TEST BACKEND
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "success",
        "message": "IT Asset Management Backend is running!"
    })


# 2. GET ALL EMPLOYEES
@app.route("/api/users", methods=["GET"])
def get_users():
    connection = get_connection()
    users = connection.execute(
        "SELECT * FROM users"
    ).fetchall()
    connection.close()

    return jsonify([dict(user) for user in users])


# 3. GET ONE EMPLOYEE
@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    connection = get_connection()
    user = connection.execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    connection.close()

    if user is None:
        return jsonify({"error": "Employee not found"}), 404

    return jsonify(dict(user))


# 4. ADD AN EMPLOYEE
@app.route("/api/users", methods=["POST"])
def add_user():
    data = request.get_json(silent=True) or {}

    required_fields = ["staff_code", "name", "email", "department"]

    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    connection = get_connection()

    try:
        cursor = connection.execute("""
            INSERT INTO users
            (staff_code, name, email, department, role)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data["staff_code"],
            data["name"],
            data["email"],
            data["department"],
            data.get("role", "Employee")
        ))

        connection.commit()
        new_id = cursor.lastrowid

        user = connection.execute(
            "SELECT * FROM users WHERE id = ?", (new_id,)
        ).fetchone()

        connection.close()

        return jsonify({
            "message": "Employee added successfully",
            "user": dict(user)
        }), 201

    except sqlite3.IntegrityError:
        connection.close()
        return jsonify({
            "error": "Staff code or email already exists"
        }), 409


# 5. UPDATE AN EMPLOYEE
@app.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json(silent=True) or {}

    required_fields = ["staff_code", "name", "email", "department"]

    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    connection = get_connection()

    existing_user = connection.execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()

    if existing_user is None:
        connection.close()
        return jsonify({"error": "Employee not found"}), 404

    try:
        connection.execute("""
            UPDATE users
            SET staff_code = ?,
                name = ?,
                email = ?,
                department = ?,
                role = ?
            WHERE id = ?
        """, (
            data["staff_code"],
            data["name"],
            data["email"],
            data["department"],
            data.get("role", "Employee"),
            user_id
        ))

        connection.commit()

        updated_user = connection.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()

        connection.close()

        return jsonify({
            "message": "Employee updated successfully",
            "user": dict(updated_user)
        })

    except sqlite3.IntegrityError:
        connection.close()
        return jsonify({
            "error": "Staff code or email already exists"
        }), 409


# 6. DELETE AN EMPLOYEE
@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    connection = get_connection()

    existing_user = connection.execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()

    if existing_user is None:
        connection.close()
        return jsonify({"error": "Employee not found"}), 404

    connection.execute(
        "DELETE FROM users WHERE id = ?", (user_id,)
    )

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Employee deleted successfully"
    })


# 7. GET ALL ASSETS
@app.route("/api/assets", methods=["GET"])
def get_assets():
    connection = get_connection()

    assets = connection.execute("""
        SELECT
            assets.*,
            users.name AS assigned_employee
        FROM assets
        LEFT JOIN users
        ON assets.assigned_to = users.id
    """).fetchall()

    connection.close()

    return jsonify([dict(asset) for asset in assets])

# 8. GET ONE ASSET
@app.route("/api/assets/<int:asset_id>", methods=["GET"])
def get_asset(asset_id):
    connection = get_connection()

    asset = connection.execute("""
        SELECT
            assets.*,
            users.name AS assigned_employee
        FROM assets
        LEFT JOIN users
        ON assets.assigned_to = users.id
        WHERE assets.id = ?
    """, (asset_id,)).fetchone()

    connection.close()

    if asset is None:
        return jsonify({"error": "Asset not found"}), 404

    return jsonify(dict(asset))

# 9. ADD A NEW ASSET
@app.route("/api/assets", methods=["POST"])
def add_asset():
    data = request.get_json(silent=True) or {}

    # Check required fields
    required_fields = ["name", "tag", "category"]

    for field in required_fields:
        if not data.get(field):
            return jsonify({
                "error": f"{field} is required"
            }), 400

    # Check assigned employee, if provided
    assigned_to = data.get("assigned_to")

    if assigned_to is not None:
        try:
            assigned_to = int(assigned_to)
        except (ValueError, TypeError):
            return jsonify({
                "error": "assigned_to must be a valid employee ID"
            }), 400

    connection = get_connection()

    try:
        if assigned_to is not None:
            employee = connection.execute(
                "SELECT id FROM users WHERE id = ?",
                (assigned_to,)
            ).fetchone()

            if employee is None:
                connection.close()
                return jsonify({
                    "error": "Employee not found"
                }), 404

        cursor = connection.execute("""
            INSERT INTO assets
            (name, tag, serial, category, assigned_to, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["name"],
            data["tag"],
            data.get("serial"),
            data["category"],
            assigned_to,
            data.get("status", "Available")
        ))

        connection.commit()

        new_id = cursor.lastrowid

        asset = connection.execute("""
            SELECT
                assets.*,
                users.name AS assigned_employee
            FROM assets
            LEFT JOIN users
            ON assets.assigned_to = users.id
            WHERE assets.id = ?
        """, (new_id,)).fetchone()

        connection.close()

        return jsonify({
            "message": "Asset registered successfully",
            "asset": dict(asset)
        }), 201

    except sqlite3.IntegrityError:
        connection.close()
        return jsonify({
            "error": "Asset tag or serial number already exists"
        }), 409

    # 10. UPDATE AN ASSET
@app.route("/api/assets/<int:asset_id>", methods=["PUT"])
def update_asset(asset_id):
    data = request.get_json(silent=True) or {}

    required_fields = ["name", "tag", "category"]

    for field in required_fields:
        if not data.get(field):
            return jsonify({
                "error": f"{field} is required"
            }), 400

    assigned_to = data.get("assigned_to")

    if assigned_to is not None:
        try:
            assigned_to = int(assigned_to)
        except (ValueError, TypeError):
            return jsonify({
                "error": "Invalid employee ID"
            }), 400

    connection = get_connection()

    existing_asset = connection.execute(
        "SELECT * FROM assets WHERE id = ?",
        (asset_id,)
    ).fetchone()

    if existing_asset is None:
        connection.close()
        return jsonify({
            "error": "Asset not found"
        }), 404

    try:
        if assigned_to is not None:
            employee = connection.execute(
                "SELECT id FROM users WHERE id = ?",
                (assigned_to,)
            ).fetchone()

            if employee is None:
                connection.close()
                return jsonify({
                    "error": "Employee not found"
                }), 404

        connection.execute("""
            UPDATE assets
            SET name = ?,
                tag = ?,
                serial = ?,
                category = ?,
                assigned_to = ?,
                status = ?
            WHERE id = ?
        """, (
            data["name"],
            data["tag"],
            data.get("serial") or None,
            data["category"],
            assigned_to,
            data.get("status", "Available"),
            asset_id
        ))

        connection.commit()

        updated_asset = connection.execute("""
            SELECT
                assets.*,
                users.name AS assigned_employee
            FROM assets
            LEFT JOIN users
            ON assets.assigned_to = users.id
            WHERE assets.id = ?
        """, (asset_id,)).fetchone()

        connection.close()

        return jsonify({
            "message": "Asset updated successfully",
            "asset": dict(updated_asset)
        })

    except sqlite3.IntegrityError:
        connection.close()
        return jsonify({
            "error": "Asset tag or serial number already exists"
        }), 409

# 11. DELETE AN ASSET
@app.route("/api/assets/<int:asset_id>", methods=["DELETE"])
def delete_asset(asset_id):
    connection = get_connection()

    existing_asset = connection.execute(
        "SELECT * FROM assets WHERE id = ?",
        (asset_id,)
    ).fetchone()

    if existing_asset is None:
        connection.close()
        return jsonify({
            "error": "Asset not found"
        }), 404

    connection.execute(
        "DELETE FROM assets WHERE id = ?",
        (asset_id,)
    )

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Asset deleted successfully"
    })

# 12. GET ALL TICKETS
@app.route("/api/tickets", methods=["GET"])
def get_tickets():
    connection = get_connection()

    tickets = connection.execute("""
        SELECT
            tickets.*,
            users.name AS reported_employee
        FROM tickets
        LEFT JOIN users
        ON tickets.reported_by = users.id
    """).fetchall()

    connection.close()

    return jsonify([dict(ticket) for ticket in tickets])

# 13. GET ONE TICKET
@app.route("/api/tickets/<int:ticket_id>", methods=["GET"])
def get_ticket(ticket_id):
    connection = get_connection()

    ticket = connection.execute("""
        SELECT
            tickets.*,
            users.name AS reported_employee
        FROM tickets
        LEFT JOIN users
        ON tickets.reported_by = users.id
        WHERE tickets.id = ?
    """, (ticket_id,)).fetchone()

    connection.close()

    if ticket is None:
        return jsonify({
            "error": "Ticket not found"
        }), 404

    return jsonify(dict(ticket))


# 14. CREATE A NEW TICKET
@app.route("/api/tickets", methods=["POST"])
def add_ticket():
    data = request.get_json(silent=True) or {}

    # Check required fields
    required_fields = ["title", "date_raised"]

    for field in required_fields:
        if not data.get(field):
            return jsonify({
                "error": f"{field} is required"
            }), 400

    # Validate ticket priority
    valid_priorities = ["Low", "Medium", "High"]

    priority = data.get("priority", "Medium")

    if priority not in valid_priorities:
        return jsonify({
            "error": "Priority must be Low, Medium, or High"
        }), 400

    # Validate ticket status
    valid_statuses = ["Open", "In Progress", "Resolved", "Closed"]

    status = data.get("status", "Open")

    if status not in valid_statuses:
        return jsonify({
            "error": "Invalid ticket status"
        }), 400

    # Check reporting employee, if provided
    reported_by = data.get("reported_by")

    if reported_by is not None:
        try:
            reported_by = int(reported_by)
        except (ValueError, TypeError):
            return jsonify({
                "error": "Invalid employee ID"
            }), 400

    connection = get_connection()

    if reported_by is not None:
        employee = connection.execute(
            "SELECT id FROM users WHERE id = ?",
            (reported_by,)
        ).fetchone()

        if employee is None:
            connection.close()
            return jsonify({
                "error": "Employee not found"
            }), 404

    cursor = connection.execute("""
        INSERT INTO tickets
        (title, description, reported_by, priority, status, date_raised)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data["title"],
        data.get("description"),
        reported_by,
        priority,
        status,
        data["date_raised"]
    ))

    connection.commit()

    new_id = cursor.lastrowid

    ticket = connection.execute("""
        SELECT
            tickets.*,
            users.name AS reported_employee
        FROM tickets
        LEFT JOIN users
        ON tickets.reported_by = users.id
        WHERE tickets.id = ?
    """, (new_id,)).fetchone()

    connection.close()

    return jsonify({
        "message": "Ticket created successfully",
        "ticket": dict(ticket)
    }), 201


# 15. UPDATE AN EXISTING TICKET
@app.route("/api/tickets/<int:ticket_id>", methods=["PUT"])
def update_ticket(ticket_id):
    data = request.get_json(silent=True) or {}

    connection = get_connection()

    # Check whether the ticket exists
    existing_ticket = connection.execute(
        "SELECT * FROM tickets WHERE id = ?",
        (ticket_id,)
    ).fetchone()

    if existing_ticket is None:
        connection.close()
        return jsonify({
            "error": "Ticket not found"
        }), 404

    # Keep existing values when a field is not supplied
    title = data.get("title", existing_ticket["title"])
    description = data.get("description", existing_ticket["description"])
    reported_by = data.get("reported_by", existing_ticket["reported_by"])
    priority = data.get("priority", existing_ticket["priority"])
    status = data.get("status", existing_ticket["status"])
    date_raised = data.get("date_raised", existing_ticket["date_raised"])
    resolution_notes = data.get("resolution_notes", existing_ticket["resolution_notes"])
    date_resolved = data.get("date_resolved", existing_ticket["date_resolved"])

    # Check required fields
    if not title or not date_raised:
        connection.close()
        return jsonify({
            "error": "Title and date_raised are required"
        }), 400

    # Validate ticket priority
    valid_priorities = ["Low", "Medium", "High"]

    if priority not in valid_priorities:
        connection.close()
        return jsonify({
            "error": "Priority must be Low, Medium, or High"
        }), 400

    # Validate ticket status
    valid_statuses = ["Open", "In Progress", "Resolved", "Closed"]

    if status not in valid_statuses:
        connection.close()
        return jsonify({
            "error": "Invalid ticket status"
        }), 400


    # Validate reporting employee
    if reported_by is not None:
        try:
            reported_by = int(reported_by)
        except (ValueError, TypeError):
            connection.close()
            return jsonify({
                "error": "Invalid employee ID"
            }), 400

        employee = connection.execute(
            "SELECT id FROM users WHERE id = ?",
            (reported_by,)
        ).fetchone()

        if employee is None:
            connection.close()
            return jsonify({
                "error": "Employee not found"
            }), 404

    # Update the ticket
    connection.execute("""
        UPDATE tickets
        SET title = ?,
            description = ?,
            reported_by = ?,
            priority = ?,
            status = ?,
            date_raised = ?,
            resolution_notes = ?,
            date_resolved = ?
        WHERE id = ?
    """, (
        title,
        description,
        reported_by,
        priority,
        status,
        date_raised,
        resolution_notes,
        date_resolved,
        ticket_id
    ))

    connection.commit()

    # Retrieve the updated ticket
    updated_ticket = connection.execute("""
        SELECT
            tickets.*,
            users.name AS reported_employee
        FROM tickets
        LEFT JOIN users
        ON tickets.reported_by = users.id
        WHERE tickets.id = ?
    """, (ticket_id,)).fetchone()

    connection.close()

    return jsonify({
        "message": "Ticket updated successfully",
        "ticket": dict(updated_ticket)
    }), 200

# 16. DELETE AN EXISTING TICKET
@app.route("/api/tickets/<int:ticket_id>", methods=["DELETE"])
def delete_ticket(ticket_id):
    connection = get_connection()

    # Check whether the ticket exists
    ticket = connection.execute(
        "SELECT * FROM tickets WHERE id = ?",
        (ticket_id,)
    ).fetchone()

    if ticket is None:
        connection.close()
        return jsonify({
            "error": "Ticket not found"
        }), 404

    # Delete the ticket
    connection.execute(
        "DELETE FROM tickets WHERE id = ?",
        (ticket_id,)
    )

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Ticket deleted successfully"
    }), 200


# START SERVER
if __name__ == "__main__":
    app.run(debug=True)
