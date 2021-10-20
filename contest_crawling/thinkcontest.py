from datetime import datetime
from collections import namedtuple

import requests
from bs4 import BeautifulSoup

# from . import env
import env


def get_cate_list(url):
    url = url + "/Contest/CateField.html"
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    categories = namedtuple("categories", ["name", "url"])
    return [
        categories(name=source.find("a").get_text(), url=source.find("a")["href"])
        for source in soup.find("ul", class_="contest-cate-list").find_all("li")
    ]


def get_main_source(url):
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    source = soup.find_all("tr")

    return source


def parse_main_source(source):
    contest_name = source.find("a").get_text()  # 공모전명
    contest_url = source.find("a")["href"]  # detail url
    categories = [
        info.get_text() for info in source.find_all("span", class_="cate-name")
    ]  # 카테고리
    sponsor = source.find_all("td")[1].get_text()  # 주최자
    progressing = source.find("span", class_="labeling").get_text()  # 진행사항

    dates = source.find_all("td")[3].get_text().split("~")
    date_format = "%Y.%m.%d"
    start_date = datetime.strptime(dates[0], date_format)
    end_date = datetime.strptime(dates[1], date_format)

    return [
        contest_name,
        contest_url,
        categories,
        sponsor,
        progressing,
        start_date,
        end_date,
    ]



if __name__ == "__main__":
    categories = get_cate_list(env.thinkcontest)
    target_cates = set(["마케팅", "디자인", "콘텐츠", "컨텐츠"])
    for name, url in categories:
        if target_cates & set(name.split("/")):
            print(name, url)
            sources = get_main_source(env.thinkcontest + url)
            for source in sources:
                try:
                    print(parse_main_source(source))
                except Exception as e:
                    print(e)

            print(" ")
