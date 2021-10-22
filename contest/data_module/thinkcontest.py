from datetime import datetime

import requests
from bs4 import BeautifulSoup
import pandas as pd

pd.set_option("display.max_colwidth", 255)

# import env
from . import env


def get_cate_list(url):
    """씽굿 공모전 카테고리 정보"""
    url = url + "/Contest/CateField.html"
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    columns = ["name", "url"]
    data = [
        [source.find("a").get_text(), url + source.find("a")["href"]]
        for source in soup.find("ul", class_="contest-cate-list").find_all("li")
    ]

    df = pd.DataFrame(data, columns=columns)
    return df


def get_main_source(url):
    """
    메인 페이지 html 소스
    카테고리별 공모전 정보 수집
    """
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    source = soup.find_all("tr")

    return source


def parse_main_source(source):
    """공모전 메인 페이지 정보 파싱"""
    contest_name = source.find("a").get_text()  # 공모전명
    contest_url = env.thinkcontest + source.find("a")["href"]  # detail url
    categories = "|".join(
        [info.get_text() for info in source.find_all("span", class_="cate-name")]
    )  # 카테고리
    sponsor = source.find_all("td")[1].get_text()  # 주최자
    # progressing = source.find("span", class_="labeling").get_text()  # 진행사항

    dates = source.find_all("td")[3].get_text().split("~")
    date_format = "%Y.%m.%d"
    start_date = datetime.strptime(dates[0], date_format)
    end_date = datetime.strptime(dates[1], date_format)

    columns = [
        "contest_name",
        "contest_url",
        "categories",
        "sponsor",
        # "progressing",
        "start_date",
        "end_date",
    ]
    data = [
        contest_name,
        contest_url,
        categories,
        sponsor,
        # progressing,
        start_date,
        end_date,
    ]

    return columns, data


def get_main_information(target):
    """
    해당 공모전 카테고리 정보 수집

    Args:
        target ([str]): 수집할 카테고리명 (ex. 마케팅, 디자인, ...)
    """
    categories = get_cate_list(env.thinkcontest)  # 카테고리 종류
    for cate_name, url in zip(categories["name"], categories["url"]):
        if target in cate_name:
            data = []
            for i in range(1, 6):  # 5페이지까지 수집
                page_url = url + f"&page={i}"
                sources = get_main_source(page_url)
                for source in sources:
                    try:
                        columns, parse_data = parse_main_source(source)
                        data.append(parse_data)
                    except Exception as e:
                        print(e)

            df = pd.DataFrame(data, columns=columns)
            return df
