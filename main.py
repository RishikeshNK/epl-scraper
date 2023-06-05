from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup

import time
import pprint


class EPLScraper:
    """
    A web scraper for retrieving links to the statistics of players from the Premier League website.
    """

    URL = "https://www.premierleague.com/players"
    OVERVIEW_CLASSES = {
        "Name": "name t-colour",
        "Jersey Number": "number t-colour",
        "Club": "info",
        "Position": "info",
        "Nationality": "playerCountry",
        "Age": "info--light",
    }
    STATS_CLASSES = {
        "Appearances": "allStatContainer statappearances",
        "Wins": "allStatContainer statwins",
        "Losses": "allStatContainer statlosses",
        "Goals": "allStatContainer statgoals",
        "Goals per match": "allStatContainer statgoals_per_game",
        "Headed goals": "allStatContainer statatt_hd_goal",
        "Goals with right foot": "allStatContainer statatt_rf_goal",
        "Goals with left foot": "allStatContainer statatt_lf_goal",
        "Penalties scored": "allStatContainer statatt_pen_goal",
        "Freekicks scored": "allStatContainer statatt_freekick_goal",
        "Shots": "allStatContainer stattotal_scoring_att",
        "Shots on target": "allStatContainer statontarget_scoring_att",
        "Shooting accuracy %": "allStatContainer statshot_accuracy",
        "Hit woodwork": "allStatContainer stathit_woodwork",
        "Big chances missed": "allStatContainer statbig_chance_missed",
        "Clean sheets": "allStatContainer statclean_sheet",
        "Goals conceded": "allStatContainer statgoals_conceded",
        "Tackles": "allStatContainer stattotal_tackle",
        "Tackle success %": "allStatContainer stattackle_success",
        "Last man tackles": "allStatContainer statlast_man_tackle",
        "Blocked shots": "allStatContainer statblocked_scoring_att",
        "Interceptions": "allStatContainer statinterception",
        "Clearances": "allStatContainer stattotal_clearance",
        "Headed Clearance": "allStatContainer stateffective_head_clearance",
        "Clearances off line": "allStatContainer statclearance_off_line",
        "Recoveries": "allStatContainer statball_recovery",
        "Duels won": "allStatContainer statduel_won",
        "Duels lost": "allStatContainer statduel_lost",
        "Successful 50/50s": "allStatContainer statwon_contest",
        "Aerial battles won": "allStatContainer stataerial_won",
        "Aerial battles lost": "allStatContainer stataerial_lost",
        "Own goals": "allStatContainer statown_goals",
        "Errors leading to goal": "allStatContainer staterror_lead_to_goal",
        "Assists": "allStatContainer statgoal_assist",
        "Passes": "allStatContainer stattotal_pass",
        "Passes per match": "allStatContainer stattotal_pass_per_game",
        "Big chances created": "allStatContainer statbig_chance_created",
        "Crosses": "allStatContainer stattotal_cross",
        "Cross accuracy %": "allStatContainer statcross_accuracy",
        "Through balls": "allStatContainer stattotal_through_ball",
        "Accurate long balls": "allStatContainer stataccurate_long_balls",
        "Saves": "allStatContainer statsaves",
        "Penalties saved": "allStatContainer statpenalty_save",
        "Punches": "allStatContainer statpunches",
        "High Claims": "allStatContainer statgood_high_claim",
        "Catches": "allStatContainer statcatches",
        "Sweeper clearances": "allStatContainer stattotal_keeper_sweeper",
        "Throw outs": "allStatContainer statkeeper_throws",
        "Goal Kicks": "allStatContainer statgoal_kicks",
        "Yellow cards": "allStatContainer statyellow_card",
        "Red cards": "allStatContainer statred_card",
        "Fouls": "allStatContainer statfouls",
        "Offsides": "allStatContainer stattotal_offside",
    }
    POSITIONS = ["Goalkeeper", "Defender", "Midfielder", "Forward"]

    def __init__(self) -> None:
        """
        Initializes the EPLScraper instance.
        """
        self.driver = webdriver.Firefox()
        self.links = []
        self.stats = []

    def run(self) -> None:
        """
        Runs the web scraping process.
        """
        # self.__get_links()
        # assert len(self.links) != 0

        stats = self.__get_player_stats(
            "https://www.premierleague.com/players/13565/Marcus-Rashford/"
        )

        pprint.pprint(stats, sort_dicts=False)

    def __get_links(self) -> None:
        """
        Scrapes the links to the statistics of players from the Premier League website.
        """
        self.driver.get(self.URL)

        time.sleep(5)

        self.__scroll()

        players = self.driver.find_elements(By.CLASS_NAME, "playerName")

        for player in players:
            self.links.append(player.get_attribute("href").replace("overview", ""))

        self.__close()

    def __get_player_stats(self, link: str) -> dict[str, str]:
        """
        Scrapes player statistics for the player from the passed-in URL.
        """
        stats = {}

        # Scraping from the overview page
        response = requests.get(link + "overview")
        soup = BeautifulSoup(response.text, "html.parser")

        name = soup.find("div", class_=self.OVERVIEW_CLASSES["Name"])
        stats["Name"] = name.get_text().strip() if name is not None else ""

        jersey_number = soup.find("div", class_=self.OVERVIEW_CLASSES["Jersey Number"])
        stats["Jersey Number"] = (
            jersey_number.get_text().strip() if jersey_number is not None else ""
        )

        infos = soup.find_all("div", class_="info")

        if len(infos) > 1:
            if infos[0].get_text().strip() in self.POSITIONS:
                stats["Club"] = ""
                stats["Position"] = infos[0].get_text().strip()
            else:
                stats["Club"] = infos[0].get_text().strip()
                stats["Position"] = infos[1].get_text().strip()
        else:
            stats["Club"] = ""
            stats["Position"] = ""

        nationality = soup.find("span", class_=self.OVERVIEW_CLASSES["Nationality"])
        stats["Nationality"] = (
            nationality.get_text().strip() if nationality is not None else ""
        )

        age = soup.find("span", class_=self.OVERVIEW_CLASSES["Age"])
        stats["Age"] = (
            age.get_text().strip().replace("(", "").replace(")", "")
            if age is not None
            else ""
        )

        # Scraping from the statistics page
        response = requests.get(link + "stats")
        soup = BeautifulSoup(response.text, "html.parser")

        for class_ in self.STATS_CLASSES.items():
            stat = soup.find("span", class_=class_[1])
            if stat is not None:
                stats[class_[0]] = stat.get_text().strip()
            else:
                stats[class_[0]] = ""

        return stats

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
