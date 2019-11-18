#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 17 19:02:46 2019

@author: supritigarnaik
"""

from collections import defaultdict
from prettytable import PrettyTable
import os
import sqlite3

DB_FILE = "/Users/supritigarnaik/810/assignments/810_startup.db"
class Repository:
    # stores and process students, instructors and major informations
    def __init__(self, path):
        self.path = path
        self.pStu = os.path.join(path, 'students.txt')
        self.pIns = os.path.join(path, 'instructors.txt')
        self.pGPA = os.path.join(path, 'grades.txt')
        self.pMajor = os.path.join(path, 'majors.txt')
        self.stu = dict()
        self.ins = dict()
        self.major = dict()
        self.read_Student()
        self.read_Instructor()
        self.read_Grade()
        self.read_Major()

    def file_reader(self,path,fields,sep = '\t',header = False):
        try:
            fp = open(path,'r')

        except FileNotFoundError:
            raise FileNotFoundError(f"Can't find or open {path}, please try another folder path")

        else:
            with fp:
                for n, line in enumerate(fp):
                    count = n + 1
                    fds = line.strip().split(sep)

                    if n == 0 and header:
                        continue

                    elif len(fds) == fields:
                        yield fds

                    else:
                        raise ValueError(f" {path} has {len(fds)} fields on line {count} but except {fields}")
    
    def read_Student(self):
        for CWID, Name, Dept in self.file_reader(self.pStu, 3):
            self.stu[CWID] = Student(CWID, Name, Dept)

    def read_Instructor(self):
        for CWID, Name, Dept in self.file_reader(self.pIns, 3):
            self.ins[CWID] = Instructor(CWID, Name, Dept)

    def read_Grade(self):
        for CWID, course, grade, insID in self.file_reader(self.pGPA, 4):
            if CWID in self.stu.keys() and grade != '':
                self.stu[CWID].cgrade(course, grade)

            if insID in self.ins.keys():
                self.ins[insID].cPop(course)
    
    def read_Major(self):
        for Dept, flag, course in self.file_reader(self.pMajor, 3):
            if Dept not in self.major:
                self.major[Dept] = Major(Dept)
            self.major[Dept].add_course(flag, course)

    def Major_Summary(self):
        '''Major Summary'''
        test = dict()
        # dictionary for testing purpose
        table = PrettyTable(field_names=['Dept','Required','Electives'])
        table.title = 'Major Summary'

        for majors in self.major.values():
            for Dept, Required, Electives in majors.pt():
                table.add_row([Dept, Required, Electives])
                test[Dept] = [Dept, sorted(Required), sorted(Electives)]

        print(table)
        return test
        

    def Student_Summary(self):
        '''Student Summary'''
        test = dict()
        # dictionary for testing purpose
        table = PrettyTable(field_names=['CWID','Name','Completed Courses', 'Remaining Required', 'Remaining Electives'])
        table.title = 'Student Summary'

        for stu in self.stu.values():
            for CWID, Name, course, Required_remaining, Electives_remaining in stu.pt(self.major[stu.Dept]):
                table.add_row([CWID, Name, course, Required_remaining, Electives_remaining])
                test[CWID] = [CWID, Name, sorted(course), Required_remaining, Electives_remaining]

        print(table)
        return test
        
    def Instructor_Summary(self):
        '''Instructor Summary'''
        test = set()
        # set for testing purpose due to possible repeated keys.
        table = PrettyTable(field_names=['CWID','Name','Dept','Course','Students'])
        table.title = 'Instructor Summary'
        
        for ins in self.ins.values():
            for CWID, Name, Dept, course, students in ins.pt():
                table.add_row([CWID, Name, Dept, course, students])
                test.add((CWID, Name, Dept, course, students))

        print(table)
        return test

    def instructor_table_db(self):
        '''Instructor Summary Through Database Query'''
        test = set()
        
        table = PrettyTable(field_names=['CWID','Name','Dept','Course','Students'])
        table.title = 'Instructor Summary'
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        for row1 in c.execute("""select instructors.CWID, instructors.Name,instructors.Dept, majors.Course,
                    count(grades.StudentCWID) as student_count
                    from instructors, majors ,grades
                    where instructors.Dept = majors.Major
                    and  grades.Course = majors.Course
                    AND instructors.CWID = grades.InstructorCWID
    
                    group by  instructors.CWID, instructors.Name,instructors.Dept, majors.Course"""):
            table.add_row(row1)
            test.add(row1)

        print(table)
        return test


class Student:
    # student grades stored with each person individually
    def __init__(self, CWID, Name, Dept):
        self.CWID = CWID
        self.Name = Name
        self.Dept = Dept
        self.grade = defaultdict(lambda: 'not taken/finished')

    def cgrade(self, course, grade):
        self.grade[course] = grade

    def pt(self, major):
        passed = {courses for courses, grade in self.grade.items() if grade in ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-']}
        remaining_req, remaining_ele = major.Remaining(passed)
        yield self.CWID, self.Name, sorted(list(passed)), remaining_req, remaining_ele


class Instructor:
    # instructor information
    def __init__(self, CWID, Name, Dept):
        self.CWID = CWID
        self.Name = Name
        self.Dept = Dept
        self.course_Pop = defaultdict(int)

    def cPop(self, course):
        self.course_Pop[course] += 1
        
    def pt(self):
        for course, students in self.course_Pop.items():
            yield self.CWID, self.Name, self.Dept, course, students


class Major:
    # major information: required and elective courses
    def __init__(self, Dept):
        self.Dept = Dept
        self.Required = set()
        self.Electives = set()

    def add_course(self, flag, course):
        if flag == 'R':
            self.Required.add(course)

        if flag == 'E':
            self.Electives.add(course)

    def pt(self):
        yield self.Dept, list(self.Required), list(self.Electives)

    def Remaining(self, course_set):
        remaining_req = self.Required - course_set
        if self.Electives & course_set:
            remaining_ele = None
        else:
            remaining_ele = self.Electives

        return remaining_req, remaining_ele


def main(path):
    try:
        repo = Repository(path)
        repo.Major_Summary()
        repo.Student_Summary()
        repo.instructor_table_db()
        
    except FileNotFoundError as e:
        print(e, "\n")

    except ValueError as f:
        print(f, "\n")

    except OSError as g:
        print(g, "\n")



if __name__ == "__main__":


        path = input('Please input a folder path:\n')
        main(path)  


