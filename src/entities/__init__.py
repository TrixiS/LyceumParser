class YandexEntity:

    def __init__(self, **kwargs):
        self.name = kwargs.pop("name")
        self.url = kwargs.pop("url")

    def __str__(self):
        return f"{self.name} - {self.entity_type.name.title()}({self.url})"


class YandexCourse(YandexEntity):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.description = kwargs.pop("description", None)
        self.lessons = kwargs.pop("lessons", None)


class YandexLesson(YandexEntity):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.tasks = kwargs.pop("tasks", None)


class YandexTask(YandexEntity):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.statement = kwargs.pop("statement")
        
        if self.name.endswith("РУЧ"):
            self.name = self.name[:-3]
            self.is_manual = True
        else:
            self.is_manual = False