from flask import Flask, render_template, request, redirect
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")


# Create table automatically
def create_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS players (
        id SERIAL PRIMARY KEY,
        name TEXT,
        country TEXT,
        base_price INT,
        current_bid INT
    )
    """)

    conn.commit()
    cur.close()
    conn.close()


# Insert sample players (only once)
def insert_players():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM players")
    count = cur.fetchone()[0]

    if count == 0:

        players = [
            ("Virat Kohli","India",50000,50000),
            ("Steve Smith","Australia",50000,50000),
            ("Joe Root","England",50000,50000),
            ("Kane Williamson","New Zealand",50000,50000),
            ("Babar Azam","Pakistan",50000,50000)
        ]

        for p in players:
            cur.execute(
                "INSERT INTO players (name,country,base_price,current_bid) VALUES (%s,%s,%s,%s)",
                p
            )

    conn.commit()
    cur.close()
    conn.close()


@app.route("/")
def index():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM players")
    players = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("index.html", players=players)


@app.route("/bid/<int:id>", methods=["POST"])
def bid(id):

    bid_amount = int(request.form["bid"])

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT current_bid FROM players WHERE id=%s",(id,))
    current = cur.fetchone()[0]

    if bid_amount > current:
        cur.execute(
            "UPDATE players SET current_bid=%s WHERE id=%s",
            (bid_amount,id)
        )

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    create_table()
    insert_players()
    app.run()