from src.processing.due_date_extractor import extract_due_date

phrases = [
    "voor vrijdag",
    "volgende maandag",
    "binnen twee weken",
    "op 10 juni",
    "eind Q2",
    "before next Friday"
]

for phrase in phrases:
    date = extract_due_date(phrase)
    print(f"{phrase:25} → {date}")
