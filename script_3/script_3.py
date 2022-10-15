import json

import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim


def get_json_data_by_url(url: str) -> str:
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    data = {'type': 'all'}
    response = requests.post(url=url, headers=headers, data=data)
    return response.json()


def make_bs4_soup(html_text: str) -> BeautifulSoup:
    soup = BeautifulSoup(html_text, 'lxml')
    return soup


def generate_shop_url(shop_postfix_url: str) -> str:
    prefix_url = 'https://naturasiberica.ru'
    return f'{prefix_url}{shop_postfix_url}'


def get_all_shops_url(soup: BeautifulSoup) -> list[str, ...]:
    shops_block = soup.find(class_='card-list')
    shops = shops_block.find_all(name='li')
    all_shops_url = [generate_shop_url(shop.a.get('href')) for shop in shops]
    return all_shops_url


def get_shop_info(shop_html: str) -> str:
    shop_soup = make_bs4_soup(shop_html)
    shop_info = shop_soup.find(class_='original-shops__info')
    return shop_info


def get_latlon_by_address(geolocator: Nominatim, loc: str) -> list[float, float]:
    loc = loc.replace('пр.', '').replace('пр-т', '').replace('пр-кт', '').replace('ул.', ''). \
        replace('д.', '').replace('им.', '').replace('им.', '')
    location = geolocator.geocode(loc)

    if not location:
        split_loc = loc.split(',')
        len_loc = len(split_loc)
        while not location:
            loc = split_loc[:len_loc]
            loc = ','.join(loc)
            len_loc -= 1
            location = geolocator.geocode(loc)

    return [location.latitude, location.longitude]


def generate_shop_info_dict(address: str,
                            latlon: list,
                            phones: list,
                            working_hours: list) -> dict:
    name = 'Natura Siberica'
    shop_info = dict(address=address,
                     latlon=latlon,
                     name=name,
                     phones=phones,
                     working_hours=working_hours
                     )

    return shop_info


def parse_json_data(json_data: json) -> list:
    all_shops_data = []
    shops = json_data['original']
    geolocator = Nominatim(user_agent="my_request")

    for shop in shops:
        city = shop['city']
        address = shop['address'].replace('&quot;', '\"')
        full_address = f"{city}, {address}"
        latlon = get_latlon_by_address(geolocator=geolocator, loc=full_address)
        phones = [shop['phone'].replace(' ', '') if shop['phone'] else shop['phone']]
        working_hours = [shop['schedule'].replace('\r\n', ' ').strip() if shop['schedule'] else shop['schedule']]

        shop_info = generate_shop_info_dict(
            address=full_address,
            latlon=latlon,
            phones=phones,
            working_hours=working_hours
        )
        all_shops_data.append(shop_info)

    return all_shops_data


def load_data_to_json(data: list[dict, ...]) -> None:
    with open("script_3_data.json", mode='w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def main() -> None:
    prefix_url = 'https://naturasiberica.ru/'
    url = f'{prefix_url}local/php_interface/ajax/getShopsData.php'
    print(f'Start parsing {prefix_url}. Please wait...')

    json_data = get_json_data_by_url(url=url)
    all_shops_data = parse_json_data(json_data=json_data)
    load_data_to_json(all_shops_data)

    print(f'Successfully created /script_3/script_3_data.json')


if __name__ == '__main__':
    main()
