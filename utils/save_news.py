import os
from utils.google_news import get_google_news
from utils.extract_news import download_latest_news



def save_news(user_request):
    data = get_google_news(user_request)
    data = download_latest_news(data)
    folder_name = "NEWS_data"
    os.makedirs(folder_name, exist_ok=True)

    for index, row in data.iterrows():
        with open(os.path.join(folder_name, f"description_{index + 1}.txt"), "w", encoding="utf-8") as f:
            f.write(row['description'])

    print("Descriptions have been saved in the 'NEWS_data' folder.")
    return folder_name