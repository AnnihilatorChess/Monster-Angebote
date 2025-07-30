from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory
from datetime import datetime
import os
import psycopg2

# Database connection from Neon PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        app.logger.error(f"Database connection failed: {e}")
        return None


app = Flask(__name__)
app.secret_key = os.getenv("secret_key")


# Homepage, Offers
@app.route("/")
def index():
    today = datetime.today().date()
    con = get_db_connection()
    cursor = con.cursor()
    cursor.execute('''
        SELECT supermarket, start_date, end_date, price 
        FROM monster_offers
        WHERE end_date >= %s 
        ORDER BY start_date ASC
    ''', (today,))
    offers = cursor.fetchall()

    # represent dates in DD.MM
    modified_offers = [
        (offer[0].capitalize(), offer[1].strftime("%d.%m"), offer[2].strftime("%d.%m"), *offer[3:])
        for offer in offers
    ]
    con.close()
    return render_template("index.html", offers=modified_offers)


@app.route('/benachrichtigungen', methods=['POST', 'GET'])
def benachrichtigungen():
    if request.method == 'POST':
        email = request.form.get("email")
        action = request.form.get("action")

        if not email:
            flash("Bitte geben Sie eine gültige E-Mail-Adresse ein.", "danger")
            return redirect(url_for('benachrichtigungen'))

        con = get_db_connection()
        cursor = con.cursor()

        if action == "subscribe":
            name = request.form.get("name")
            if not name:
                name = None
            wholesaler_preference = not bool(request.form.get("wholesaler_preference"))

            try:
                cursor.execute('''
                    INSERT INTO emails (name, email, wholesalers, active)
                    VALUES (%s, %s, %s, TRUE)
                    ON CONFLICT (email)
                    DO UPDATE SET 
                        active = TRUE,
                        wholesalers = EXCLUDED.wholesalers;
                ''', (name, email, wholesaler_preference))
                con.commit()
                flash("Erfolgreich angemeldet!", "success")
            except Exception as e:
                flash("Anmeldung fehlgeschlagen.", "danger")

        elif action == "unsubscribe":
            try:
                cursor.execute("UPDATE emails SET active = FALSE WHERE email=%s", (email,))
                con.commit()
                flash("Erfolgreich abgemeldet!", "warning")
            except Exception as e:
                flash("Fehler beim Abmelden.", "danger")

        con.close()
        return redirect(url_for('benachrichtigungen'))

    return render_template('benachrichtigungen.html')


@app.route('/impressum')
def impressum():
    return render_template('impressum.html')


@app.route('/datenschutz')
def datenschutz():
    return render_template('datenschutz.html')


@app.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')


@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('static', 'sitemap.xml')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
