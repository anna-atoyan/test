import pandas as pd
class HumanResources:
    employees = set()

    def __init__(self, name, surname, team, salary):
        self.name = name
        self.surname = surname
        self.team = team
        self.salary = salary
        HumanResources.employees.add(self)

    def  all(HumanResourses,employees):
        for i in employees:
            return i

    def print_all(cls):
        print(HumanResources.employees)




p1 = HumanResources("Artak", "Sargsyan", "HR", 1000)
p2 = HumanResources("Elen", "Smith", "PM", 800)
p3 = HumanResources("Garnik", "Inaplanityan", "CEO", 2000)


HumanResources.print_all(HumanResources)