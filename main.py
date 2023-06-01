from selenium import webdriver
from selenium.webdriver.common.by import By

import time


class EPLScraper:
    """
    A web scraper for retrieving links to the statistics of players from the Premier League website.
    """

    URL = "https://www.premierleague.com/players"

    def __init__(self) -> None:
        """
        Initializes the EPLScraper instance.
        """
        self.driver = webdriver.Firefox()
        self.links = []

    def run(self) -> None:
        """
        Runs the web scraping process.
        """
        self.__get_links()
        self.__close()
        assert len(self.links) != 0

    def __get_links(self) -> None:
        """
        Scrapes the links to the statistics of players from the Premier League website.
        """
        self.driver.get(self.URL)

        time.sleep(5)

        self.__scroll()

        players = self.driver.find_elements(By.CLASS_NAME, "playerName")

        for player in players:
            self.links.append(player.get_attribute("href"))

    def __scroll(self) -> None:
        """
        Scrolls down the page to load all players dynamically.
        """
        SCROLL_PAUSE_TIME = 2
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(SCROLL_PAUSE_TIME)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def __close(self) -> None:
        """
        Closes the WebDriver instance and quits the browser.
        """
        self.driver.quit()


def main():
    """
    Main function.
    """
    scraper = EPLScraper()
    scraper.run()


if __name__ == "__main__":
    start = time.time()
    main()
    delta = time.time() - start
    print(f"Elapsed time: {delta:.2f}s")
