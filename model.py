import pandas as pd
import re

motor = pd.read_csv("dataset/motor_vehicles.csv")
ipc = pd.read_csv("dataset/ipc.csv")
cyber = pd.read_csv("dataset/cyber_law.csv")
general = pd.read_csv("dataset/data.csv")

# 🔥 Normalize column names
motor.columns = ["section", "text"]
ipc.columns = ["section", "text"]
cyber.columns = ["section", "text"]
general.columns = ["article", "text"]


def search(query, domain):
    query = query.lower()
    results = []

    if domain == "motor":
        df = motor
    elif domain == "ipc":
        df = ipc
    elif domain == "cyber":
        df = cyber
    else:
        df = general

    numbers = re.findall(r'\d+', query)
    query_words = query.split()

    for _, row in df.iterrows():
        try:
            raw_key = str(row.get("section", row.get("article", ""))).lower()
            text = str(row["text"]).lower()

            # 🔥 extract number
            key_numbers = re.findall(r'\d+', raw_key)
            key_num = key_numbers[0] if key_numbers else ""

            score = 0

            # ✅ number match
            for num in numbers:
                if num == key_num:
                    score += 50

            # ✅ keyword match
            for word in query_words:
                if word in text or word in raw_key:
                    score += 5

            # ✅ special boosts
            if "article" in query and "article" in raw_key:
                score += 20

            if "drunk" in query and "alcohol" in text:
                score += 20

            if score > 0:
                results.append((score, raw_key, row["text"]))

        except Exception as e:
            print("ROW ERROR:", e)
            continue

    results.sort(reverse=True, key=lambda x: x[0])

    return [
        {"text": f"{r[1].title()}: {r[2]}"}
        for r in results[:1]
    ]