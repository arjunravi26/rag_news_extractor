from GoogleNews import GoogleNews
import pandas as pd


def get_google_news(user_request):
    '''
    Function is used to get recent 7 days news link based on user request

    Input: user_request<str>
    Returns: df<pd.DataFrame>
    '''
    googlenews = GoogleNews(period='7d')
    googlenews.search(user_request)

    all_results = []
    for i in range(1, 50):
        googlenews.getpage(i)
        result = googlenews.result()

        if result:
            all_results.extend(result)

        if len(all_results) >= 100:
            break

    df = pd.DataFrame(all_results).drop_duplicates(
        subset=['title'], keep='last').head(100)
    df.reset_index(drop=True, inplace=True)
    data = df.drop(columns = ['media', 'date', 'datetime', 'desc', 'img'])
    return data
