import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
import multiprocessing
from tqdm import tqdm


def process_range(start_idx, end_idx, db_slice):
    service = Service(executable_path="/snap/bin/geckodriver")
    driver = webdriver.Firefox(service=service)

    for i in tqdm(range(start_idx, end_idx),
                  bar_format="{l_bar}{bar} [ elapsed: {elapsed_s}, remaining: {remaining_s}]"):
        word = db_slice.loc[i, 'Word']
        driver.get(f"https://www.vocabulary.com/dictionary/autocomplete?search={word.replace(' ', '%20')}")
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        spans = soup.findAll("span", class_="word")

        if not spans:
            db_slice.loc[i, 'Found'] = False
            continue

        texts = [span.text for span in spans]
        lower_texts = [text.lower() for text in texts]

        if word.lower() not in lower_texts:
            db_slice.loc[i, 'Found'] = False
            continue

        word = texts[lower_texts.index(word.lower())]
        db_slice.loc[i, 'Web World'] = word

        driver.get(f"https://www.vocabulary.com/dictionary/definition.ajax?search={word.replace(' ', '%20')}&lang=en")
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        p_short = soup.find("p", class_="short")
        p_long = soup.find("p", class_="long")

        db_slice.loc[i, 'Short Meaning'] = p_short.text if p_short else ""
        db_slice.loc[i, 'Long Meaning'] = p_long.text if p_long else ""

    db_slice.to_csv(f'res_range_{start_idx}_{end_idx}.csv', index=False)
    driver.quit()


def main():
    db = pd.read_csv('1212.csv')
    db['Short Meaning'] = ''
    db['Long Meaning'] = ''
    db['Web World'] = ''
    db['Found'] = True

    num_processes = multiprocessing.cpu_count()
    chunk_size = len(db) // num_processes

    processes = []
    for i in range(num_processes):
        start_idx = i * chunk_size
        end_idx = start_idx + chunk_size if i < num_processes - 1 else len(db)
        db_slice = db[start_idx:end_idx].copy()
        process = multiprocessing.Process(target=process_range, args=(start_idx, end_idx, db_slice))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    merged_db = pd.concat([pd.read_csv(f'res_range_{start_idx}_{end_idx}.csv') for start_idx, end_idx in
                           [(i * chunk_size, (i + 1) * chunk_size if i < num_processes - 1 else len(db)) for i in
                            range(num_processes)]],
                          ignore_index=True)

    merged_db.loc[:, ["Web World", "Short Meaning", "Long Meaning"]] = merged_db.loc[:, ["Web World", "Short Meaning",
                                                                                         "Long Meaning"]].fillna("")

    merged_db.to_csv('res.csv', index=False)


if __name__ == '__main__':
    main()
