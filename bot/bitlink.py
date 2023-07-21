from urllib.parse import urlparse
import requests

API_URL = 'https://api-ssl.bitly.com/v4/'


def is_bitlink(token, url):
    parsed_url = urlparse(url)
    url = f"{parsed_url.netloc}{parsed_url.path}"
    api_method_url = f'{API_URL}/bitlinks/{url}'
    headers = {
        'Authorization': f'Bearer {token}'
    }

    response = requests.get(api_method_url, headers=headers)
    return response.ok


def shorten_link(token, url):
    api_method_url = f"{API_URL}bitlinks"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    payload = {
        'long_url': url
    }

    response = requests.post(bitly_url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()['id']
    # id:   bit.ly/3nqqxey
    # link: https://bit.ly/3nqqxey


def count_clicks(token, bitlink, period='month'):
    parsed_bitlink = urlparse(bitlink)
    bitlink = f'{parsed_bitlink.netloc}{parsed_bitlink.path}'
    api_method_url = f"{API_URL}bitlinks/{bitlink}/clicks/summary"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    payload = {
        'unit': period
    }

    response = requests.get(api_method_url, headers=headers, params=payload)
    response.raise_for_status()
    return response.json()['total_clicks']
