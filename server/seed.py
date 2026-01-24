from random import randint, choice as rc
from faker import Faker
import os
from models import db, User, JournalEntry
from app import app

fake = Faker()

with app.app_context():
    print("Deleting existing data...")
    JournalEntry.query.delete()
    User.query.delete()

    fake = Faker()

    print("Creating users...")
    users = []
    usernames = []

    for i in range(10):
        username = fake.user_name()
        while username in usernames:
            username = fake.user_name()
        usernames.append(username)

        user = User(
            username=username,
        )
        user.password_hash = user.username + 'password'

        users.append(user)
    db.session.add_all(users)

    print("Creating journal entries...")
    journal_entries = []
    for i in range(30):
        journal_entry = JournalEntry(
            title=fake.sentence(nb_words=6),
            date=fake.date_time_this_year(),
            content=fake.paragraph(nb_sentences=5),
        )
        journal_entry.user = rc(users)
        journal_entries.append(journal_entry)
    db.session.add_all(journal_entries)
    db.session.commit()
    print("Seeding complete.")