class Student:

    def __init__(self, name, last_name, birth_year):
        self.name = name
        self.last_name = last_name
        self.birth_year = birth_year
        self.id = f"{list(self.name)[0]}{self.last_name}{self.birth_year}"


name = input()
last_name = input()
birth = input()
john = Student(name, last_name, birth)
print(john.id)
