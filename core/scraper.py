from selenium import webdriver
from selenium.webdriver.common.by import By

from newspaper import Article
from newspaper import Config

import yake
import time

from database.logger import get_logger

logger = get_logger()

config = Config()
config.request_timeout = 10


class Scraper:
    def __init__(self):
        logger.info("SCRAPER INIT")

    def scrape_url(self, url):
        logger.info(f'SCRAPE URL START | url="{url}"')

        article = Article(url)
        article.download()
        article.parse()

        title = article.title
        content = article.text

        logger.info(f'SCRAPE URL DONE | title="{title}"')

        return {
            "url": url,
            "title": title,
            "content": content
        }

    def scrape_trusted_sources(self, title):
        logger.info(f'SCRAPE TRUSTED START | title="{title}"')

        kw_extractor = yake.KeywordExtractor(
            lan="id",
            n=3,
            top=3
        )

        title_kw = kw_extractor.extract_keywords(title)
        logger.info(f'KEYWORDS YAKE | {title_kw}')

        TRUSTED_SOURCES = [
            ("republika",  "news-title",   "https://www.republika.co.id/search/v3/?q="),
            ("kompas",     "article-link", "https://search.kompas.com/search/?q="),
            ("detik",      "media__link",  "https://www.detik.com/search/searchall?query="),
            ("tempo",      "contents",     "https://www.tempo.co/search?q="),
            ("antaranews", "h5",           "https://www.antaranews.com/search/?q="),
        ]

        SPECIAL_MEDIA_LAYOUTS = ["tempo", "antaranews", "republika"]

        driver = webdriver.Chrome()

        links = []
        for source in TRUSTED_SOURCES:
            source_media = source[0]
            source_element = source[1]
            source_url = source[2]

            logger.info(f'SOURCE | {source_media}')

            for kw in title_kw:
                final_url = source_url + kw[0] + "&search_type=relevansi"
                if source_media == "detik":
                    final_url = source_url + kw[0] + "&result_type=relevansi"

                logger.info(f'OPEN URL | {final_url}')

                driver.get(final_url)

                if source_media in SPECIAL_MEDIA_LAYOUTS:
                    articles = []
                    contents = driver.find_elements(By.CLASS_NAME, source_element)
                    for content in contents:
                        articles.append(content.find_element(By.TAG_NAME, "a"))
                else:
                    articles = driver.find_elements(By.CLASS_NAME, source_element)
                
                for article in articles:
                    link = article.get_attribute("href")

                    if link:
                        links.append(link)
                        logger.info(f'LINK FOUND | {link}')

                        if len(links) > 5:
                            break

        driver.close()

        links = set(links)
        logger.info(f'TOTAL LINKS | {len(links)}')

        result = []
        for link in links:
            logger.info(f'SCRAPE DETAIL | {link}')
            result.append(self.scrape_url(link))

        logger.info(f'SCRAPE TRUSTED DONE | total_data={len(result)}')

        return result

    def scrape_checkhoax(self, title):
        logger.info(f'SCRAPE HOAX START | title="{title}"')

        kw_extractor = yake.KeywordExtractor(
            lan="id",
            n=3,
            top=3
        )

        title_kw = kw_extractor.extract_keywords(title)
        logger.info(f'KEYWORDS YAKE | {title_kw}')

        HOAXCHECK_SOURCES = [
            ("checkfakta", "content", "https://cekfakta.com/api-search?_token=LOHO3l0gWBz623sumAjWXdJ7UY40fIe3Reu5AiRC&search=")
        ]
        
        driver = webdriver.Chrome()

        links = []
        for source in HOAXCHECK_SOURCES:
            source_element = source[1]
            source_url = source[2]

            for kw in title_kw:
                final_url = source_url + kw[0]

                logger.info(f'OPEN HOAX URL | {final_url}')

                driver.get(final_url)
                time.sleep(2)

                articles = []
                contents = driver.find_elements(By.CLASS_NAME, source_element)

                logger.info(f'FOUND ELEMENTS | count={len(contents)}')

                for content in contents:
                    articles.append(content.find_element(By.TAG_NAME, "a"))

                for article in articles:
                    link = article.get_attribute("href")

                    if link:  # ⬅️ filter link kosong
                        links.append(link)
                        logger.info(f'HOAX LINK | {link}')

                    if len(links) > 5:
                        break

        driver.close()

        links = set(links)
        logger.info(f'TOTAL HOAX LINKS | {len(links)}')

        result = []
        for link in links:
            logger.info(f'SCRAPE DETAIL HOAX | {link}')
            result.append(self.scrape_url(link))

        logger.info(f'SCRAPE HOAX DONE | total_data={len(result)}')

        return result