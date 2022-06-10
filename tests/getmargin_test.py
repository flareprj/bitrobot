from unittest import TestCase
import requests
import csv
import pathlib


def margin():
    try:
        csv_url = requests.get(
            'https://www.cmegroup.com/CmeWS/mvc/Margins/OUTRIGHT.csv?sortField=exchange&sortAsc=true&clearingCode=BTC&sector=EQUITY%20INDEX&exchange=CME',
            timeout=10,
            headers={'User-Agent': 'some cool user-agent'})
    except requests.exceptions.RequestException as e:
        path = pathlib.Path('margin.csv')
        if path.exists() and path.is_file():
            with open('margin.csv') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',')
                for c, row in enumerate(spamreader):
                    if c == 1:
                        return int(row[6])
        else:
            print(f'path.exists():{path.exists()}, path.is_file():{path.is_file()}, {e}')
            raise SystemExit(e)
    else:
        url_content = csv_url.content
        csv_file = open('margin.csv', 'wb')

        csv_file.write(url_content)
        csv_file.close()

        with open('margin.csv') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')
            for c, row in enumerate(spamreader):
                if c == 1:
                    return int(row[6])


class GetMargin(TestCase):
    def test_getmargin(self):
        margin()
