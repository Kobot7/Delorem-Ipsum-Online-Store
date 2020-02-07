class Feedback:
    def __init__(self, name, agenda, comment, rating):
        self.__name = name
        self.__agenda = agenda
        self.__comment = comment
        self.__rating = rating


    def set_name(self, name):
        self.__name = name

    def set_agenda(self, agenda):
        self.__agenda = agenda

    def set_comment(self, comment):
        self.__comment = comment

    def set_rating(self, rating):
        self.__rating = rating


    def get_name(self):
        return self.__name

    def get_agenda(self):
        return self.__agenda

    def get_comment(self):
        return self.__comment

    def get_rating(self):
        return self.__rating
