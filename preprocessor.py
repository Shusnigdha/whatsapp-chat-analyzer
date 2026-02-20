import re
import pandas as pd

def preprocess(data):
    pattern = r"\d{2}/\d{2}/\d{2},\s\d{1,2}:\d{2}[\s\u202f]*[ap]m\s-\s"

    msgs = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({"user_msgs" : msgs, "date" : dates})
    df["date"] = pd.to_datetime(df["date"], format = "%d/%m/%y, %I:%M %p - ")

    users = []
    msgss = []
    for msgs in df["user_msgs"]:
        i = re.split(r"([^:]+):\s(.*)", msgs)
        if i[1:]:
            users.append(i[1])
            msgss.append(i[2])
        else:
            users.append("group_notification")
            msgss.append(i[0])

    df["users"] = users
    df["msgs"] = msgss
    df.drop(["user_msgs"], axis = 1, inplace = True)

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month_name()
    df["month_num"] = df["date"].dt.month
    df["day"] = df["date"].dt.day
    df["hour"] = df["date"].dt.hour
    df["minute"] = df["date"].dt.minute
    df["only_date"] = df["date"].dt.date

    return df