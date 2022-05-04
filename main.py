import time
import requests
import datetime
import pandas as pd

from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


def get_available(building_name, url):
    result = requests.get(url, headers=headers)
    soup = BeautifulSoup(result.text, "html.parser")
    table = soup.find('table')

    df = pd.read_html(str(table))[0]
    df.replace('\n', ' ', regex=True)

    cur_time = str(datetime.datetime.today().replace(microsecond=0))
    df['Bedrooms'] = df['Bedrooms'].str.extract('(\d+)').astype(int)
    df.insert(0, 'Time', cur_time)
    df.insert(1, 'Building', building_name)
    df.insert(3, 'Url', url)
    df.drop(df.columns[[-1, -2, -3]], axis=1, inplace=True)
    # df = df.replace(np.nan, '')

    img_list = []
    apply_url_list = []
    for row in table.find_all('tr')[1:]:
        img_list.append(row.find_all('a', {'class': 'AvailableApartments__floorplan'})[0]['href'])
        apply_url_list.append(row.find_all('a', {'class': 'AvailableApartments__apply'})[0]['href'])

    df['img'] = img_list
    df['apply_url'] = apply_url_list
    return df


def get_buildings():
    url = "https://appliedapartments.com/properties-apartments-for-rent/"

    result = requests.get(url, headers=headers)
    # soup = BeautifulSoup(result.text, "lxml")
    soup = BeautifulSoup(result.text, "html.parser")

    wish_list = ["50 Columbus", "70 Columbus", "90 Columbus", "Gotham"]

    buildings = []

    for build_div in soup.select('div.ListingItem'):
        name = build_div.find_all('h2', {'class': 'ListingItem__name'})[0].text
        url = build_div.find_all('a')[0]['href']
        if name in wish_list:
            buildings.append({"name": name, "url": url})

    # for building in buildings:
    #     print(building['name'], building['url'])
    return buildings


def print_custom(df):
    print(df[["Time", "Building", "Bedrooms", "Bathrooms", "Price"]])


def main():
    buildings = get_buildings()
    max_times = 10000
    for i in range(max_times):

        df = pd.DataFrame()
        for building in buildings:
            name = building['name']
            url = building['url']
            # print(name + ": " + url)
            try:
                df = pd.concat([df, get_available(name, url)], ignore_index=True)
            except:
                continue

        print_custom(df)
        df.to_csv("./house.csv", mode='w')
        time.sleep(120)


if __name__ == "__main__":
    main()