from selenium import webdriver
from src import YandexParser

driver = webdriver.Chrome()
parser = YandexParser(driver, wait_timeout=5)

user = "morozov2281337@yandex.ru"
pwd = "rfrdsnfrvj;tnt123"

parser.login(user, pwd)

courses = parser.get_courses()

#cache
#tests
#interface
#paclets
#self.is_logged_in @dec

for course in courses:
    
    for lesson in course.lessons:
        
        for task in lesson.tasks:
            print(task.name, task.url)