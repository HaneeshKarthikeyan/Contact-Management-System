from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Use your MySQL password, if any
    'database': 'crm_lite'
}

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Contacts route
@app.route('/contacts')
def contacts():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT contacts.id, contacts.name, contacts.email, contacts.phone, organizations.name AS organization_name
            FROM contacts
            LEFT JOIN organizations ON contacts.organization_id = organizations.id
        """)
        contacts = cursor.fetchall()

        cursor.execute("SELECT id, name FROM organizations")
        organizations = cursor.fetchall()

        conn.close()
        return render_template('contacts.html', contacts=contacts, organizations=organizations)
    except mysql.connector.Error as err:
        return f"Database error: {err}"

# Add Contact
@app.route('/add_contact', methods=['POST'])
def add_contact():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    organization_id = request.form['organization_id']

    if not organization_id:  # Handle the case where no organization is selected
        organization_id = None

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Check if the organization exists
        if organization_id is not None:
            cursor.execute("SELECT id FROM organizations WHERE id = %s", (organization_id,))
            organization = cursor.fetchone()
            if not organization:
                conn.close()
                return "Error: The selected organization does not exist."

        # Insert the contact
        cursor.execute(
            "INSERT INTO contacts (name, email, phone, organization_id) VALUES (%s, %s, %s, %s)",
            (name, email, phone, organization_id),
        )
        conn.commit()
        conn.close()

        return redirect(url_for('contacts'))
    except mysql.connector.Error as err:
        return f"Database error: {err}"

# Organizations route
@app.route('/organizations')
def organizations():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM organizations")
        organizations = cursor.fetchall()
        conn.close()
        return render_template('organizations.html', organizations=organizations)
    except mysql.connector.Error as err:
        return f"Database error: {err}"

# Add Organization
@app.route('/add_organization', methods=['POST'])
def add_organization():
    name = request.form['name']
    description = request.form['description']

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO organizations (name, description) VALUES (%s, %s)", (name, description))
        conn.commit()
        conn.close()

        return redirect(url_for('organizations'))
    except mysql.connector.Error as err:
        return f"Database error: {err}"

# Interactions route
@app.route('/interactions')
def interactions():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT interactions.id, contacts.name AS contact_name, interactions.interaction_type, interactions.notes, interactions.interaction_date
            FROM interactions
            JOIN contacts ON interactions.contact_id = contacts.id
        """)
        interactions = cursor.fetchall()

        cursor.execute("SELECT id, name FROM contacts")
        contacts = cursor.fetchall()

        conn.close()
        return render_template('interactions.html', interactions=interactions, contacts=contacts)
    except mysql.connector.Error as err:
        return f"Database error: {err}"

# Add Interaction
@app.route('/add_interaction', methods=['POST'])
def add_interaction():
    try:
        contact_id = request.form['contact_id']
        interaction_type = request.form['interaction_type']
        notes = request.form['notes']
        interaction_date = request.form['interaction_date']

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO interactions (contact_id, interaction_type, notes, interaction_date) VALUES (%s, %s, %s, %s)",
            (contact_id, interaction_type, notes, interaction_date),
        )
        conn.commit()
        conn.close()

        return redirect(url_for('interactions'))
    except KeyError as e:
        return f"Missing form key: {e}"
    except mysql.connector.Error as err:
        return f"Database error: {err}"

if __name__ == '__main__':
    app.run(debug=True)