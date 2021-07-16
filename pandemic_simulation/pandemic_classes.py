import pandas as pd
from scipy.stats import binom
from typing import List, Tuple
import random
import copy


class Student:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"Susceptible st: {self.name}"

    def __repr__(self):
        return f"Susceptible st: {self.name}"


class InfectedStudent(Student):
    default_prob_infection = None
    default_days_to_recover = None

    def __init__(self, name, probability_infection, days_to_recover):
        super().__init__(name)
        self.probability_infection: float = probability_infection
        self.days_to_recover: int = days_to_recover

    @classmethod
    def create_infected_from_student(cls,
                                     student: Student,
                                     probability_infection,
                                     days_to_recover):

        if isinstance(student, Student):
            return cls(student.name, probability_infection, days_to_recover)
        else:
            raise TypeError(f"{student} is not a Student object")

    @classmethod
    def create_infected_from_student_defaults(cls,
                                              student: Student):

        if cls.default_prob_infection is None or cls.default_days_to_recover is None:
            raise ValueError("Defaults had not been set")
        else:
            return cls.create_infected_from_student(student,
                                                    cls.default_prob_infection,
                                                    cls.default_days_to_recover)

    def _infect_with_self(self, student: Student):
        return InfectedStudent.create_infected_from_student(
            student, self.probability_infection, self.days_to_recover
        )

    def infect_students(self, susceptible_students: List[Student]) -> Tuple[List, List]:
        if self.days_to_recover > 0:
            n_infected = binom.rvs(len(susceptible_students),
                                   self.probability_infection)
            # Even if n_infected is zero, the next lines will return and empty lists
            s_students = random.sample(susceptible_students, n_infected)
            infected_students = [
                self.create_infected_from_student_defaults(x) for x in s_students
            ]
            return s_students, infected_students

        else:
            raise ValueError(f"Student {self.name} can't infect anyone as he has "
                             f"recovered")

    def sick_day(self):
        if self.days_to_recover > 0:
            self.days_to_recover -= 1
        else:
            raise ValueError(f"Student {self.name} has already recovered")

    def __str__(self):
        return f"Infected st: {self.name}"

    def __repr__(self):
        return f"Infected st: {self.name}"


class RecoveredStudent(InfectedStudent):
    def __init__(self, name):
        super().__init__(name, probability_infection=0.0, days_to_recover=0)

    @classmethod
    def create_recovered_from_infected(cls, infected: InfectedStudent):
        if isinstance(infected, InfectedStudent):
            if infected.days_to_recover == 0:
                return cls(infected.name)
            else:
                raise ValueError(f"The infected student {infected.name} has not "
                                 f"fully recovered!")
        else:
            raise TypeError(f"{infected} is not an InfectedStudent object")

    def __str__(self):
        return f"Recovered st: {self.name}"

    def __repr__(self):
        return f"Recovered st: {self.name}"


class PandemicSim:
    _day_col = "day"
    _susceptible_col = "susceptible"
    _infected_col = "infected"
    _recovered_col = "recovered"

    def __init__(self, s_students: List[Student], i_students: List[InfectedStudent]):
        self.s_students = copy.deepcopy(s_students)
        self.i_students = copy.deepcopy(i_students)
        self.r_students = []
        self.current_day = 0
        self.sim_days = None
        self._sim_log = {"day": [],
                         "susceptible": [],
                         "infected": [],
                         "recovered": []}

    @property
    def sim_log(self):
        return pd.DataFrame(self._sim_log).set_index(self._day_col)

    @sim_log.setter
    def sim_log(self, value):
        raise ValueError("You can't set this property")

    def sim_day(self, debug=False):
        # All infected students interact with all the susceptible ones
        for infected in self.i_students:
            # *********** 1 - This is what occurred during the day *****************
            # Get the susceptible students that got infected, as well as the those
            # same students in "infected" mode!!
            s_st, i_st = infected.infect_students(self.s_students)

            if debug:
                [print(f"Day {self.current_day + 1}: {x.name} was infected by "
                       f"{infected.name}!!") for x in i_st]

            infected.sick_day()
            #
            # ******* 2 - This will be the initial state in the next day ***************
            # Remove susceptible st that got infected from the susceptible list
            [self.s_students.remove(s) for s in s_st]
            # Add the infected students to the infected list
            self.i_students += i_st
            # Check if there is any recovered student
            if infected.days_to_recover == 0:
                self.r_students.append(
                    RecoveredStudent.create_recovered_from_infected(infected)
                )
                # Remove the infected student from the infected list
                self.i_students.remove(infected)

                if debug:
                    print(f"Day {self.current_day + 2}: {infected.name} has "
                          f"recovered!!")

        self.current_day += 1
        self._sim_log[self._day_col].append(self.current_day)
        self._sim_log[self._susceptible_col].append(len(self.s_students))
        self._sim_log[self._infected_col].append(len(self.i_students))
        self._sim_log[self._recovered_col].append(len(self.r_students))

        if len(self.i_students) == 0 and debug:
            print(f"Day {self.current_day}: Pandemic is over!!!")

    def run_sim(self, days=None, debug=False):
        if days is None:
            if self.sim_days is None:
                raise ValueError("You have not set the number of simulation days")
            else:
                for i in range(self.sim_days):
                    self.sim_day(debug=debug)
        else:
            self.sim_days = days
            for i in range(self.sim_days):
                self.sim_day(debug=debug)

    @classmethod
    def run_sim_with(cls,
                     days,
                     susceptible_students,
                     infected_students,
                     probability_infection,
                     days_to_recover,
                     debug=False) -> pd.DataFrame:

        # Susceptible students
        s_students = [Student("st_" + str(i + 1)) for i in range(susceptible_students)]
        # Infected students
        i_students = [
            InfectedStudent("st_" + str(susceptible_students + i + 1),
                            probability_infection,
                            days_to_recover)
            for i in range(infected_students)
        ]
        # Set default values for infected students
        InfectedStudent.default_prob_infection = probability_infection
        InfectedStudent.default_days_to_recover = days_to_recover

        sim = cls(s_students, i_students)
        sim.run_sim(days=days, debug=debug)

        return sim.sim_log.copy()

    @classmethod
    def run_sims_with(cls,
                      trials,
                      days,
                      susceptible_students,
                      infected_students,
                      probability_infection,
                      days_to_recover,
                      debug=False) -> pd.DataFrame:

        results = pd.DataFrame()
        for t in range(trials):
            temp_results = cls.run_sim_with(days,
                                            susceptible_students,
                                            infected_students,
                                            probability_infection,
                                            days_to_recover,
                                            debug=debug)

            results = results.append(temp_results)

        return results.groupby("day").mean()
