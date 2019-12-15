from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from typing import List

from .entities import *


def login_required(fun):
	
	def wrap(self, *args, **kwargs):
		if not hasattr(self, "logged_in"):
			raise Exception("Parser object must have 'logged_in' attribute")
		
		if not self.logged_in:
			raise Exception("Login required")
		
		return fun(self, *args, **kwargs)

	return wrap


class YandexParser:

	def __init__(self, webdriver, *, wait_timeout: int=3):
		self.driver = webdriver
		self.wait_timeout = wait_timeout
		self.logged_in = False

		self._base_url = "https://lyceum.yandex.ru/"


	def _get_with_wait(self, url: str, lambda_to_wait):
		self.driver.get(url)
		WebDriverWait(self.driver, self.wait_timeout).until(lambda_to_wait)


	def login(self, username: str, password: str) -> None:
		self.driver.get(self._base_url)

		def submit():
			submit_btn = self.driver.find_element_by_xpath('//button[@type="submit"]')
			submit_btn.click()

		def get_and_send(element: str, send_keys: str):
			WebDriverWait(self.driver, self.wait_timeout).until(lambda x: x.find_element_by_name(element))
			self.driver.find_element_by_name(element).send_keys(send_keys)		

		get_and_send("login", username)
		submit()

		get_and_send("passwd", password)
		submit()

		WebDriverWait(self.driver, self.wait_timeout).until(lambda x: x.find_element_by_class_name("courses__list-item"))

		self.logged_in = True


	@login_required	
	def parse_tasks(self, lesson_url: str) -> List[YandexTask]:
		tasks = []

		self._get_with_wait(lesson_url, lambda x: x.find_elements_by_xpath('//header[@class="task-group-header"]'))

		unparsed_tasks_urls = tuple(map(lambda x: x.get_attribute('href'), self.driver.find_elements_by_class_name("student-task-list__task")))

		state_btn_xpath = '//a[@class="nav-tab nav-tab_view_button"]'
		task_name_xpath = '//h1[@class="heading heading_level_1 yde1c4--task-header__heading"]'

		for task_url in unparsed_tasks_urls:
			try:
				self._get_with_wait(task_url, lambda x: x.find_element_by_xpath(task_name_xpath) and x.find_element_by_xpath(state_btn_xpath))
				self.driver.find_element_by_xpath(state_btn_xpath).click()
			except (TimeoutException, NoSuchElementException):
				pass
			
			task_name = self.driver.find_element_by_xpath(task_name_xpath)
			task_statement = self.driver.find_element_by_class_name("problem-statement")

			tasks.append(YandexTask(statement=task_statement.text, name=task_name.text, url=task_url))

		return tasks


	@login_required
	def parse_lessons(self, course_url: str) -> List[YandexLesson]:
		lessons = []

		lesson_xpath = "link-list__link"

		self._get_with_wait(course_url, lambda x: x.find_element_by_class_name(lesson_xpath))

		unparsed_lessons = self.driver.find_elements_by_class_name(lesson_xpath)

		for lesson in unparsed_lessons:
			lesson_name = lesson.text.split('\n')[0]
			lesson_url = lesson.get_attribute('href')

			if 'task' not in lesson_url:
				lessons.append(YandexLesson(name=lesson_name, url=lesson_url))

		return lessons


	@login_required
	def parse_courses(self) -> List[YandexCourse]:
		courses_xpath = '//a[@class="course-card course-card_type_link"]'

		self._get_with_wait(self._base_url + "courses", lambda x: x.find_element_by_xpath(courses_xpath))

		courses = []

		unparsed_courses = self.driver.find_elements_by_xpath(courses_xpath)

		for course in unparsed_courses:
			course_name = course.text
			course_url = course.get_attribute("href")

			courses.append(YandexCourse(name=course_name, url=course_url))

		for course in courses:
			self.driver.get(course.url)

			course_description = None
			
			details_btn = self.driver.find_elements_by_class_name("details__summary")

			if details_btn:
				details_btn[0].click()
				course_description = self.driver.find_element_by_xpath('//details[@class="details course-details__description"]').text

			course.description = course_description

		return courses


	@login_required
	def get_courses(self) -> List[YandexCourse]:
		courses = self.parse_courses()

		for course in courses:
			course.lessons = self.parse_lessons(course.url)

			for lesson in course.lessons:
				lesson.tasks = self.parse_tasks(lesson.url)

		return courses