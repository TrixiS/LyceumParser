from selenium.webdriver import Chrome
from pathlib import Path
from requests import get as req_get

from yandexparser import YandexParser

from config import Config


driver = Chrome(Config.webdriver_filepath)
parser = YandexParser(driver)
parser.login(Config.username, Config.password)

url_to_search = input("Site URL for search: ")

with (Path('.') / 'search.txt').open('w', encoding='utf-8') as f:

    tasks = parser.parse_tasks(input("Lesson url: "))
    
    for task in tasks:
        if task.has_solution:
            continue

        input_state = ' '.join(task.statement.split('\n')[4:6])

        with req_get(Config.google_api_url, params={
            "key": Config.google_custom_search_api_key,
            "cx": Config.google_cx_id,
            "q": f"Python 3 {task.name} {input_state} site:{url_to_search}"
        }) as r:
            result = r.json()

            if 'error' in result:
                print(*result['error']['errors'], sep='\n')

            if 'items' in result and len(result['items']) > 0:
                f.write(str(task) + '\n')

                for item in result['items'][:5]:
                    f.write(item['link'] + '\n')

                f.write('\n\n')

driver.close()