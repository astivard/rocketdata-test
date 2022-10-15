import json

import requests
from bs4 import BeautifulSoup


def get_html_by_url(url: str) -> str:
    response = requests.get(url, headers={'User-Agent': 'Custom'})
    return response.text


def make_bs4_soup(html_text: str) -> BeautifulSoup:
    soup = BeautifulSoup(html_text, 'lxml')
    return soup


def generate_city_url(city_id: str) -> str:
    prefix_url = 'https://oriencoop.cl/sucursales/'
    postfix_url = city_id
    return f'{prefix_url}{postfix_url}'


def get_cities_ids(regions: list) -> list:
    cities_ids = []

    for region in regions:
        cities = region.find_all('li')
        for city in cities:
            city_id = city.a.get('href').split('/')[2]
            cities_ids.append(city_id)

    return cities_ids


def get_all_regions(soup: BeautifulSoup) -> list:
    regions_block = soup.find(class_='c-list c-accordion')
    regions = regions_block.find_all(name='li', recursive=False)
    return regions


def get_working_hours(all_p_of_department_data_block: list) -> list:
    working_daily_intervals = all_p_of_department_data_block[3].find_all(name='span')
    working_hours = [daily_interval.text.strip() for daily_interval in working_daily_intervals]
    return working_hours


def get_phones(all_p_of_department_data_block: list) -> list:
    phones_block = all_p_of_department_data_block[1].find_all(name='span')
    working_hours = [phone.text.strip() for phone in phones_block]
    return working_hours


def get_latlon(city_soup: BeautifulSoup) -> list:
    google_map_url = city_soup.find(class_='s-mapa').iframe.get('src')
    splitted_google_map_url = google_map_url.split('!')

    lat = float(splitted_google_map_url[5][2:])
    lon = float(splitted_google_map_url[6][2:])
    latlon = [lat, lon]

    return latlon


def generate_department_data_dict(department_data_block: BeautifulSoup,
                                  city_soup: BeautifulSoup) -> dict:
    all_p_of_department_data_block = department_data_block.find_all(name='p')

    address = all_p_of_department_data_block[0].span.text
    phones = get_phones(all_p_of_department_data_block)
    name = 'Oriencoop'
    working_hours = get_working_hours(all_p_of_department_data_block)
    latlon = get_latlon(city_soup=city_soup)

    department_data_dict = dict(address=address,
                                latlon=latlon,
                                name=name,
                                phones=phones,
                                working_hours=working_hours)

    return department_data_dict


def parse_html(soup: BeautifulSoup) -> list[dict, ...]:
    regions = get_all_regions(soup=soup)
    cities_ids = get_cities_ids(regions)

    all_cities_data = []

    for city_id in cities_ids:
        city_url = generate_city_url(city_id=city_id)
        city_html = get_html_by_url(city_url)
        city_soup = make_bs4_soup(city_html)

        department_data_block = city_soup.find(class_='s-dato')
        department_data_dict = generate_department_data_dict(department_data_block=department_data_block,
                                                             city_soup=city_soup)
        all_cities_data.append(department_data_dict)
    return all_cities_data


def load_data_to_json(data: list[dict, ...]) -> None:
    with open("script_1_data.json", mode='w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def main() -> None:
    url = 'https://oriencoop.cl/sucursales.htm'
    print(f'Start parsing {url}. Please wait...')

    html = get_html_by_url(url)
    soup = make_bs4_soup(html)
    all_cities_data = parse_html(soup)
    load_data_to_json(all_cities_data)

    print(f'Successfully created /script_1/script_1_data.json')


if __name__ == '__main__':
    main()
