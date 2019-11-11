#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  9 16:37:31 2019

@author: supritigarnaik
"""

import os
from collections import defaultdict
from prettytable import PrettyTable
import unittest


def file_reading_gen(path, numfields, expectedfields, sep='\t'):
    try:
        fp = open(path, "r", encoding="utf-8")
    except FileNotFoundError:
        print("Can't open the file:", path)
    else:
        with fp:
            for n, line in enumerate(fp, 1):
                fields = line.rstrip('\n').split(sep)
                if len(fields) == fields:
                    print("field not present")
                elif n == 1 and expectedfields:
                    continue
                else:

                    yield (fields)

class Repository:
    """ creating repository  """

    def __init__(self, wdir, ptables=True):
        self._wdir = wdir
        self._students = dict()  # instance of class student
        self._instructors = dict()  # instance of class instructor
        self._majors = dict()  # instance of class majors
        """ Read all the text files"""
        self._get_instructors(os.path.join(wdir, 'instructors.txt'))
        self._get_majors(os.path.join(wdir, 'majors.txt'))
        self._get_students(os.path.join(wdir, 'students.txt'))
        self._get_grades(os.path.join(wdir, 'grades.txt'))

        if ptables:
           
            self.major_table()
           
            self.student_table()
         
            self.instructor_table()

    def _get_students(self, path):  # get student info
        try:
            for cwid, name, major in file_reading_gen(path, 3, 'cwid;name;major', sep=';'):
                if cwid in self._students:
                    print(f"Already exits {cwid}")
                else:
                    self._students[cwid] = Student(cwid, name, major, self._majors[major])
        except ValueError as error:
            print(error)

    def _get_instructors(self, path):  # get instructor info
        try:
            for cwid, name, dept in file_reading_gen(path, 3, 'cwid|name|department', sep='|'):
                if cwid in self._instructors:
                    print(f"Already exits {cwid}")
                else:
                    self._instructors[cwid] = Instructor(cwid, name, dept)
        except ValueError as error:
            print(error)

    def _get_grades(self, path):  # get grade info
        try:
            for student_cwid, course, grade, instructor_cwid in file_reading_gen(path, 4, 'StudentCWID|Course|Grade|InstructorCWID', sep='|'):
                if student_cwid in self._students:
                    self._students[student_cwid].add_course(course, grade)
                else:
                    print(f"Warning: student cwid {student_cwid} not exist")

                if instructor_cwid in self._instructors:
                    self._instructors[instructor_cwid].add_student(course)
                else:
                    print(f"Warning: Instructor cwid {instructor_cwid} not exist")

        except ValueError as error:
            print(error)

    def _get_majors(self, path):  # get majors info
        try:
            #for major, flag, course in file_reading_gen(path, 3, 'major\tflag\tcours'):
            for major, flag, course in file_reading_gen(path, 3, 'Major\tRequired/Elective\tCourse'):
                
                if major in self._majors:
                    self._majors[major].add_course(flag, course)
                else:
                    self._majors[major] = Major(major)
                    self._majors[major].add_course(flag, course)
        except ValueError as error:
            print(error)

    def major_table(self):
        """Print pretty table for major"""
        majorpt = PrettyTable(field_names=['Dept', 'Required', 'Elective'])
        for major in self._majors.values():
            majorpt.add_row(major.pt_row())
        print("\nMajors Summary")
        print(majorpt)

    def student_table(self):  
        """Print pretty table for student"""
        stupt = PrettyTable(field_names=['CWID', 'Name', 'Major', 'Completed Courses', 'Remaining Required', 'Remaining Elective'])

        for student in self._students.values():
            stupt.add_row(student.pt_row())
        print("\nStudent Summary")
        print(stupt)

    def instructor_table(self):  
        """Print pretty table for instructor"""
        inspt = PrettyTable(field_names=['CWID', 'Name', 'Dept', 'Course', 'Students'])
        for ins in self._instructors.values():
            for row in ins.pt_row():
                inspt.add_row(row)
        print("\nInstructor summary")
        print(inspt)       

class Student:
    """Class for all the student records. CWID, Name, completed courses."""

    def __init__(self, cwid, name, major, in_major):
        self._cwid = cwid
        self._name = name
        self._major = major
        self._instr_major = in_major
        self.courses = dict()
        self.coursegrade = dict()
        self._courses = dict()

    def add_course(self, course, grade):
        Grades = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C']
        if grade in Grades:
            self._courses[course] = grade

    def add_course_grade(self, course, grade):
        self.coursegrade[course] = grade

    def student_info(self):
        return [self._cwid, self._name, sorted(self.coursegrade.keys())]

    def pt_row(self):
        complete_course, remaining_req_course, remaining_elective_course = self._instr_major.grade_check(self._courses)
        return [self._cwid, self._name, self._major, sorted(list(complete_course)),remaining_req_course,
                remaining_elective_course]


class Instructor:
    """Class for all the instructor records. """

    def __init__(self, cwid, name, dept):
        self._cwid = cwid
        self._name = name
        self._dept = dept
        self._courses = defaultdict(int)

    def add_student(self, course):
        self._courses[course] += 1

    def instr(self):
        for course, count in self._courses.items():
            return [self._cwid, self._name, self._dept, course, count]

    def pt_row(self):
        for course, students in self._courses.items():
            yield [self._cwid, self._name, self._dept, course, students]


class Major:
    """Class for all the major records. """

    def __init__(self, major, passing=None):
        self._major = major
        self._required = set()
        self._elective = set()
        if passing is None:
            self._grades = {'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C'}
        else:
            self._grades = passing

    def add_course(self, val, course):

        if val == 'R':  #'R' means Required course
            self._required.add(course)
        elif val == 'E':  # 'E' means Elective course
            self._elective.add(course)
        else:
            raise ValueError(f"Unexcepted value {val}")

    def grade_check(self, courses):
        completed_course = {course for course, grade in courses.items() if grade in self._grades}
        if len(completed_course) == 0:  # if no courses are completed then student has to take all courses
            return [completed_course, self._required, self._elective]
        else:
            remaining_req_course = self._required - completed_course  # calculating remaining required courses
            if self._elective.intersection(completed_course):
                remaining_elective_course = None
            else:
                remaining_elective_course = self._elective  # calculating remaining elective courses
            if completed_course != None:
                completed_course = sorted(completed_course)
            
            if remaining_req_course != None:
                remaining_req_course = sorted(remaining_req_course)
            
            if remaining_elective_course != None:
                remaining_elective_course = sorted(remaining_elective_course)
                
            return [completed_course, remaining_req_course, remaining_elective_course]

    def pt_row(self):
        return [self._major, self._required, self._elective]


def main():
    """ Run repo"""
    
    path = input("Please enter the path of the file: ")
    Repository(path)
   # path = "/Users/supritigarnaik/Desktop/Study/Python" #


if __name__ == '__main__':
    main()
#    unittest.main(exit=False, verbosity=2)
