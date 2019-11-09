#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 15:21:14 2019

@author: supritigarnaik
"""

import os
from collections import defaultdict
from prettytable import PrettyTable
import unittest

class Repository:
    def __init__(self, dir_path):
        """Store all the information about student and instructor"""
        
        """ Read all the text files"""
        self.stu_path = os.path.join(dir_path, 'students.txt')
        self.inst_path = os.path.join(dir_path, 'instructors.txt')
        self.grade_path = os.path.join(dir_path, 'grades.txt')
        self.student = dict() #instance of class student
        self.Instructor = dict()  #instance of class instructor      
        self.feed_student()
        self.feed_instructor()

    def feed_student(self):
        """Read grade text file"""
        try:
            fp = open(self.stu_path, 'r')
        except FileNotFoundError:
            raise FileNotFoundError('Error! Cannot open the student.txt file', self.stu_path)
        else:
            with fp:         
                for line in fp:
                    line = line.strip().split('\t')
                    self.student[line[0]] = Student(line[0], line[1], line[2])
        try:
            file = open(self.grade_path, 'r')
        except FileNotFoundError:
            raise FileNotFoundError('Error! Cannot open the grades.txt file', self.grade_path)
        else:
            with file:                
                for grade_line in file:
                    grade_line = grade_line.strip().split('\t')
                    try:
                        self.student[grade_line[0]].course_grade(grade_line[1], grade_line[2])
                    except KeyError:
                        raise KeyError("Grade file has a student ID that does not exist!")
            self.student_table(self.student)

    def student_table(self, stu):
        """Print pretty table for student"""
        stu_pt = PrettyTable(field_names=Student.columns)
        for key in stu.keys():
            stu_pt.add_row([stu[key].CWID, stu[key].Name,sorted(list(stu[key].grade))])
        
        print("Student Summary")
        print(stu_pt)
             
    def feed_instructor(self):
        """Feed data to instructor class and print the pretty table"""
        try:
            fp = open(self.inst_path, 'r')
        except FileNotFoundError:
            raise FileNotFoundError('Error! Cannot open the instructor.txt file', self.inst_path)
        else:
            with fp:             
                for line in fp:
                    line = line.strip().split('\t')
                    self.Instructor[line[0]] = Instructor(line[0], line[1], line[2])
                  
        try:
            file = open(self.grade_path, 'r')
        except FileNotFoundError:
            raise FileNotFoundError('Error! Cannot open the grades.txt file', self.grade_path)
        else:
            with file:                             
                for grade_line in file:
                    grade_line = grade_line.strip().split('\t')
                    try:
                        self.Instructor[grade_line[3]].num_course(grade_line[1])
                    except KeyError:
                        raise KeyError("Grade file has an instructor ID that does not exist!")
            self.instructor_table(self.Instructor)

    def instructor_table(self, ins):
        """Print the pretty table for instructor"""
        ins_pt = PrettyTable(field_names = Instructor.columns)
        for key in ins.keys():
            for a in ins[key].generator_ins():
                ins_pt.add_row(a)
        
        print("Instructor Summary")
        print(ins_pt)

class Student:
    """Class for all the student records. CWID, Name, completed courses."""
    columns = ['CWID', 'Name', 'Completed Courses'] #Class attributes for pretty table columns

    def __init__(self, CWID, Name, Major):
        """Student will have cwid, name, major, course name and grade"""
        self.CWID = CWID
        self.Name = Name
        self.Major = Major
        self.grade = defaultdict(str) #Course name is the key with grade be the value
    def course_grade(self, course_name, letter_grade):
        self.grade[course_name] = letter_grade

class Instructor:
    """Class for all the instructor records. """
    columns = ['CWID', 'Name', 'Dept', 'Course', 'Students']    #Class attributes for pretty table columns

    def __init__(self, CWID, Name, Dept):
        """Container for instructor"""
        self.CWID = CWID
        self.Name = Name
        self.Dept = Dept
        self.Course = defaultdict(int)  #Course name is the key with number of students be the value

    def num_course(self, course_name):
        """Add course and number of students to course dict"""
        self.Course[course_name] += 1

    def generator_ins(self):
        """Generator for prettytable"""
        for course_name, num in self.Course.items():
            yield [self.CWID, self.Name, self.Dept, course_name, num]
                   
def main():
    """Run repo"""
    path = input("Please enter the path of student, instructor and grade. (All three files must exist in the same directory): ")
    Repository(path)

 
if __name__ == '__main__':
    main()


# ----------
# UNIT TESTS
# ----------
class Test(unittest.TestCase):
  
    def test_Instructor(self):
        """Test instructor course function"""
      
        inst = Instructor(98765, 'Einstein, A', 'SFEN')
        for i in range(10):
            inst.num_course("SSW 567")
        for a in range(4):
            inst.num_course("SSW 540")
        dict = inst.Course
        result = {"SSW 567":10, "SSW 540":4}
        self.assertEqual(dict, result)
        
    def test_Student(self):
        """Test student course grade function"""
        stud = Student(10172, "Forbes, I", "SFEN")
        stud.course_grade("SSW 555", "A")
        stud.course_grade("SSW 567", "A-")

        dict = stud.grade
        result = {"SSW 555":"A", "SSW 567":"A-"}
        self.assertEqual(dict, result)

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)