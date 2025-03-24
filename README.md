# Overview

The Patron Reading History Web App, history4patrons, is a Flask-based web application designed to allow staff users to retrieve a patron reading history from the library's database. Library staff can input a patron record number to download a CSV file containing the patron's reading history, provided they have opted-in to the library's Reading History feature.

# Purpose

This application was created to streamline access to library reading history data for patrons while ensuring secure and efficient interaction with the underlying database. The app enforces input validation and provides informative feedback to enhance usability and prevent errors.

Under the current procedure, it takes 10 steps to export the Patron Reading History via the Discovery Layer catalog (Encore):

1. Go to the Poudre Libraries website
2. Click on the My Account link
3. Type your Library Barcode Number and PIN in the respective fields.
4. Click "Submit"
5. Click "My History"
6. Click "Export Reading History"
7. Type your email address
8. Click the Submit button
9. Go to your email provider (e.g. Outlook, Gmail, etc)
10. You'll see an email with the subject line "From the library catalog"
    - The content of the message will list all unique entries available on your reading history

![Screenshot of a visual diagram showing the steps to export the Patron Reading History via Encore.](/assets/images/Patron-Reading-History_Encore-Steps.png)

The Patron Reading History web app simplifies the process to 4 steps:

1. Access the application in a web browser at http://127.0.0.1:5000
2. Type the patron's record number
3. Click Submit
4. Save the .csv file on your work desktop computer 


![Screenshot of a visual diagram showing the steps to export the Patron Reading History via the patron reading history web app.](/assets/images/Patron-Reading-History_History4Patrons-Steps.png)


# Features

1.	Input Form: A web interface where users can enter their patron record number.
2.	Validation: Both client-side and server-side validation to ensure input integrity.
3.	Dynamic CSV Generation: Generates and downloads a CSV file containing the reading history.
4.	Error Handling: Provides feedback for invalid inputs and scenarios without data.
5.	Secure Database Interaction: Uses SQLAlchemy for database queries and connection management.


# Required Libraries

Ensure the following Python libraries are installed:
```Python
pip install flask sqlalchemy psycopg2 pandas

```
 
**Library Purpose:**

-	Flask: Framework to build the web application.
-	SQLAlchemy: ORM for database interaction.
-	psycopg2: PostgreSQL database adapter.
-	pandas: Data manipulation and CSV generation.



# Application Workflow

1.	The user visits the web page and enters their patron record number in the input box.
2.	Input is validated both on the client (using JavaScript) and server-side (using Python regular expressions).
3.	The application queries the database for reading history records associated with the entered patron record number.
4.	If records are found, a CSV file is generated dynamically and provided for download.
5.	Appropriate error messages are displayed if no records are found or the input is invalid.
    


# Validation Rules

**Client-Side Validation (JavaScript):**

1.	The input must:
-	Start with the letter "p".
-	End with the letter "a".
-	Contain only numeric values in between.
-	Be at most 10 characters long.
2.	Invalid inputs trigger an alert, preventing form submission.

**Server-Side Validation (Python):**

1.	The input must match the regular expression: ^p[a-zA-Z0-9]*a$.
2.	If validation fails, the user is shown an error message on the web page.



# Database Interaction

The app uses SQLAlchemy to interact with the library's database. The query retrieves data from the sierra_view.reading_history and sierra_view.bib_record_property views.

Query:

``` SQL

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

```



# Error Handling

**Scenarios and Responses:**

1.	**Invalid Input:**
-	Client-Side: Displays an alert indicating the input does not meet validation rules.
-	Server-Side: Displays an error message: "Invalid patron record number. The value must start with 'p', end with 'a', and be alphanumeric."
2.	**No Records Found:**
-	Message displayed: "Please make sure the patron record number entered is valid, or the patron has opted-in for the Reading History feature."


# File Naming Convention

The generated CSV file follows the pattern:

patron-record-number_Reading-History.csv

Example: p12345a_Reading-History.csv



# Deployment

1.	Locate the file history4patrons.py.
2.	Run the Flask application locally:

```Python

python history4patrons.py

```
 
3.	Access the application in a web browser at http://127.0.0.1:5000.
