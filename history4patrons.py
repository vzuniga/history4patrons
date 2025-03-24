from flask import Flask, request, send_file, render_template_string
from sqlalchemy import create_engine
import pandas as pd
from io import BytesIO
import re

# Initialize Flask App
app = Flask(__name__)

# Database connection configuration
DB_HOST = "sierra-db-hostname"
DB_NAME = "name-of-the-db"
DB_USER = "user"
DB_PASSWORD = "password"
DB_PORT = "1032"

# SQLAlchemy connection string
DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URI)

# Query for reading history
def fetch_reading_history(patron_record_number):
    query = """
        SELECT
            brp.best_title AS "Title",
            brp.best_author AS "Author",
            id2reckey(rh.item_record_metadata_id) || 'a' AS "Item Number",
            TO_CHAR(rh.checkout_gmt::DATE, 'MM/DD/YYYY') AS "Checkedout Date"
        FROM sierra_view.reading_history rh
        LEFT JOIN sierra_view.bib_record_property brp
            ON rh.bib_record_metadata_id = brp.bib_record_id
        WHERE rh.patron_record_metadata_id = reckey2id(%s)
        ORDER BY rh.checkout_gmt DESC;
    """
    # Execute query and return as DataFrame
    return pd.read_sql_query(query, engine, params=(patron_record_number,))

# Validate patron record number
def is_valid_patron_number(patron_record_number):
    # Ensure the input starts with 'p', ends with 'a', is alphanumeric, and is not too long
    return bool(re.match(r'^p[a-zA-Z0-9]*a$', patron_record_number)) and len(patron_record_number) <= 20

# Flask Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    error_message = None  # Initialize error message variable

    if request.method == 'POST':
        patron_record_number = request.form['patron_record_number'].strip()

        # Server-side validation
        if not is_valid_patron_number(patron_record_number):
            error_message = "Invalid patron record number. The value must start with 'p', end with 'a', and be alphanumeric."
        else:
            # Fetch reading history
            reading_history = fetch_reading_history(patron_record_number)

            # Check if results are found
            if reading_history.empty:
                error_message = "Please make sure the patron record number entered is valid, or the patron has opted-in for the Reading History feature."
            else:
                # Valid submission: Generate CSV
                csv_filename = f"{patron_record_number}_Reading-History.csv"
                output = BytesIO()
                reading_history.to_csv(output, index=False)
                output.seek(0)

                return send_file(
                    output,
                    mimetype="text/csv",
                    as_attachment=True,
                    download_name=csv_filename
                )

    # Render the form dynamically with error message
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Patron Reading History</title>
            <script>
                // Clear error message after form submission
                function clearErrorOnSubmit() {
                    setTimeout(() => {
                        const errorMessage = document.getElementById('error-message');
                        const form = document.getElementById('patron-form');
                        if (errorMessage) {
                            errorMessage.innerText = '';
                        }
                        form.reset();
                    }, 500);
                }
            </script>
        </head>
        <body>
            <h1>Patron Reading History</h1>
            <form id="patron-form" method="post" action="/" onsubmit="clearErrorOnSubmit();">
                <label for="patron_record_number">Enter Patron Record Number:</label><br>
                <input type="text" id="patron_record_number" name="patron_record_number" required><br><br>
                <input type="submit" value="Submit">
            </form>
            {% if error_message %}
            <p id="error-message" style="color: red;">{{ error_message }}</p>
            {% endif %}
        </body>
        </html>
    ''', error_message=error_message)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
