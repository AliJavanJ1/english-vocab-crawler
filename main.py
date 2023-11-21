import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from tqdm import tqdm


if __name__ == '__main__':
    db = pd.read_csv('GRE.csv').head(10)
    db['Short Meaning'] = ''
    db['Long Meaning'] = ''
    db['Web World'] = ''
    db['Found'] = True

    service = Service(executable_path="/snap/bin/geckodriver")
    driver = webdriver.Firefox(service=service)

    for i in tqdm(range(len(db)), bar_format="{l_bar}{bar} [ elapsed: {elapsed_s}, remaining: {remaining_s}]"):
        word = db.loc[i, 'Word']
        driver.get(f"https://www.vocabulary.com/dictionary/autocomplete?search={word.replace(' ', '%20')}")
        html = driver.page_source
        soup = BeautifulSoup(html)
        spans = soup.findAll("span", class_="word")
        if not spans:
            db.loc[i, 'Found'] = False
            continue
        texts = [span.text for span in spans]
        lower_texts = [text.lower() for text in texts]
        if word.lower() not in lower_texts:
            db.loc[i, 'Found'] = False
            continue
        word = texts[lower_texts.index(word.lower())]
        db.loc[i, 'Web World'] = word
        driver.get(f"https://www.vocabulary.com/dictionary/definition.ajax?search={word.replace(' ', '%20')}&lang=en")
        html = driver.page_source
        soup = BeautifulSoup(html)
        p_short = soup.find("p", class_="short")
        p_long = soup.find("p", class_="long")
        db.loc[i, 'Short Meaning'] = p_short.text
        db.loc[i, 'Long Meaning'] = p_long.text

    db.to_csv('res.csv')
