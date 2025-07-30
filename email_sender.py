import logging
from logging.handlers import RotatingFileHandler
import psycopg2
import os
from dotenv import load_dotenv
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from datetime import datetime

# logging setup
handler = RotatingFileHandler(
    "monster_scraper.log", maxBytes=1000000, backupCount=5
)
logging.basicConfig(
    handlers=[handler],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Database connection from Neon PostgreSQL
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


def fetch_receivers():
    """ Returns List of tuples where the first entry is a string containing the email and the second is a boolean"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
            SELECT email, wholesalers
            FROM emails 
            WHERE active = TRUE
            ''')
    emails = cursor.fetchall()
    conn.close()
    return emails


def send_mails():
    """ Sends mail to each receiver of fetch_receivers() """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT 
        monster_offers.start_date, 
        monster_offers.end_date, 
        monster_offers.price, 
        monster_offers.supermarket,
        supermarkets.wholesaler
    FROM monster_offers
    JOIN supermarkets ON monster_offers.chain_id = supermarkets.id
    WHERE monster_offers.email_sent = false;
    ''')

    offers_wholesaler = cursor.fetchall()
    if offers_wholesaler:
        offers = [offer for offer in offers_wholesaler if not offer[4]]

        password = os.getenv("email_password")
        sender_email = "noreply@monster-angebote.at"
        subject = "Neue Monster Energy Angebote!"

        receivers = fetch_receivers()
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.zoho.eu", 465, context=context) as server:
            server.login(sender_email, password)

            # sending an individual mail for each receiver
            for receiver, wholesaler in receivers:

                if wholesaler:
                    offer_pool = offers_wholesaler  # use all offers for wholesaler = True
                else:
                    offer_pool = offers             # use only non wholesaler offers for wholesaler = False

                body = f"""
                    <html>
                    <head>
                        <style>
                            body {{
                                font-family: 'Arial', sans-serif;
                                color: #333;
                                font-size: 16px;
                                margin: 0;
                                padding: 0;
                            }}
                            h1 {{
                                font-family: 'Verdana', sans-serif;
                                color: #28a745;
                            }}
                            .offer-container {{
                                border: 1px solid #ddd;
                                border-radius: 10px;
                                max-width: 300px;
                                padding: 10px;
                                margin: 10px 0;
                                background-color: #f9f9f9;
                            }}
                            .offer-title {{
                                font-size: 18px;
                                font-weight: bold;
                                color: #28a745;
                            }}
                            .offer-list {{
                                padding-left: 20px;
                            }}
                            a.button {{
                                display: inline-block;
                                padding: 10px 15px;
                                background-color: #28a745;
                                color: white;
                                text-decoration: none;
                                border-radius: 5px;
                                font-weight: bold;
                            }}
                            .info {{
                                font-size: 10px;
                            }}
                        </style>
                    </head>
                    <body>
                        <p>Hey, es gibt neue <strong>Monster Energy</strong> Angebote!</p>
                    """
                # Add each offer dynamically
                if offer_pool:
                    for offer in offer_pool:
                        body += f"""
                        <div class="offer-container">
                            <p class="offer-title">🏪 Angebot bei {offer[3].capitalize()}</p>
                            <ul class="offer-list">
                                <li><strong>💰 Preis:</strong> {offer[2]:.2f} €</li>
                                <li><strong>📅 Zeitraum:</strong> {offer[0].day:02d}.{offer[0].month:02d} - {offer[1].day:02d}.{offer[1].month:02d}</li>
                            </ul>
                        </div>
                        """
                else:
                    continue

                # Add the footer and closing HTML tags
                body += """
                    <p class="info">Für mehr Angebote, Infos oder abbestellen der Emails:</p>
                    <p><a href="https://monster-angebote.at" class="button">🔗 Website besuchen</a></p>
                </body>
                </html>
                """
                message = MIMEMultipart()
                message["From"] = sender_email
                message["Subject"] = subject
                receiver = receiver
                message["To"] = receiver
                message.attach(MIMEText(body, "html"))
                text = message.as_string()
                server.sendmail(sender_email, receiver, text)
                logging.info(f"email sent to {receiver}")

        # set email_sent to True
        cursor.execute('''
        UPDATE monster_offers
        SET email_sent = TRUE
        WHERE email_sent = FALSE;
        ''')
        conn.commit()

    conn.close()


if __name__ == "__main__":
    try:
        send_mails()
    except Exception as e:
        logging.error(f"Error occurred while sending mails: {e}")

