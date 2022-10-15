import json
import re

import requests
from bs4 import BeautifulSoup


def get_html_by_url(url: str, city_id: str = None, post=False) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36 OPR/40.0.2308.81',
    }

    if post:
        payload = {'CITY_ID': city_id}
        response = requests.post(url, headers=headers, data=payload)
    else:
        response = requests.get(url, headers=headers)
    return response.text


def make_bs4_soup(html_text: str) -> BeautifulSoup:
    soup = BeautifulSoup(html_text, 'lxml')
    return soup


def get_all_cities_ids(soup: BeautifulSoup) -> list[str, ...]:
    data_block = soup.find(class_='col-xs-12 col-sm-6 citys-box')
    regions = data_block.find_all(name='div', recursive=False)[1:]

    cities = []
    for region in regions:
        region_cities = region.find(class_='cities-container').find_all(name='div')
        for city in region_cities:
            cities.append(city)

    cities_ids = [city.label.get('id') for city in cities]
    return cities_ids


def generate_url(city_or_shop_id: str) -> str:
    prefix_url = 'https://som1.ru/shops/'
    postfix_url = city_or_shop_id
    return f'{prefix_url}{postfix_url}/'


def get_shops_ids(soup: BeautifulSoup) -> list:
    all_cities_ids = get_all_cities_ids(soup=soup)
    all_shops_ids = []

    for city_id in all_cities_ids:
        city_html = get_html_by_url('https://som1.ru/shops/', city_id=city_id, post=True)
        city_soup = make_bs4_soup(city_html)

        shops_block = city_soup.find_all(class_='shops-col shops-button')
        for shop in shops_block:
            all_shops_ids.append(shop.a.get('href').split('/')[2])
    return all_shops_ids


def parse_shop_data(shop_soup: BeautifulSoup) -> dict:
    shop_info_table = shop_soup.find(class_='shop-info-table').find_all(name='tr')
    shop_map = shop_soup.find('script', text=re.compile('showShopsMap')).get_text().split('\'')

    address = shop_info_table[0].td.next_sibling.next_sibling.next_sibling.next_sibling.get_text().strip()
    latlon = [float(shop_map[3]), float(shop_map[5])]
    name = shop_map[9]

    phones = [shop_info_table[1].td.next_sibling.next_sibling.next_sibling.next_sibling.get_text().strip()]
    all_phones = phones[0].split(',')
    phones = [phone.strip() for phone in all_phones]

    working_hours = [shop_info_table[2].td.next_sibling.next_sibling.next_sibling.next_sibling.get_text().strip()]
    if ',' in working_hours[0]:
        all_working_hours = working_hours[0].split(',')
        working_hours = [hours.strip() for hours in all_working_hours]

    shop_data_dict = dict(address=address,
                          latlon=latlon,
                          name=name,
                          phones=phones,
                          working_hours=working_hours)
    return shop_data_dict


def get_all_shops_data(soup: BeautifulSoup) -> list[dict, ...]:
    all_shops_ids = get_shops_ids(soup=soup)

    all_shops_data = []
    for shop_id in all_shops_ids:
        shop_url = generate_url(city_or_shop_id=shop_id)
        shop_html = get_html_by_url(shop_url)
        shop_soup = make_bs4_soup(shop_html)
        shop_data = parse_shop_data(shop_soup=shop_soup)
        all_shops_data.append(shop_data)

    return all_shops_data


def load_data_to_json(data: list[dict, ...]) -> None:
    with open("script_2_data.json", mode='w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def main() -> None:
    url = 'https://som1.ru/shops/'
    print(f'Start parsing {url}. Please wait...')

    html = get_html_by_url(url)
    soup = make_bs4_soup(html)
    all_shops_data = get_all_shops_data(soup)
    load_data_to_json(data=all_shops_data)

    print(f'Successfully created /script_2/script_2_data.json')


if __name__ == '__main__':
    main()
