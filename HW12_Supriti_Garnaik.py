from flask import Flask, render_template, request
import sqlite3


app = Flask(__name__)

@app.route('/')
def hello():
    display =  """
            <h1>Site map:</h1>
            <br>
            <a href="http://127.0.0.1:5000/instructor">Instructor student count</a>
        """
    return display


@app.route('/instructor')
def instructor_template():
    database_path = "/Users/supritigarnaik/810/assignments/810_startup.db"
    try:
        db = sqlite3.connect(database_path)
    except sqlite3.OperationalError:
        return (f"Error: Unable to open database at {database_path}")    
    else:
        query = """select i.CWID, i.Name, i.Dept, g.Course, count(*) as Students 
                        from instructors i left outer join grades g 
                        on g.InstructorCWID=i.CWID 
                        group by  i.CWID, i.Name, i.Dept, g.Course"""
        data = db.execute(query)
        instructor = [{'cwid': cwid, 'name': name, 'dept': dept, 'course': course,
                    'students': students} for cwid, name, dept, course, students in data]

        return render_template('instructor.html',
                            title="Stevens Repository",
                            page_header="Stevens Repository",
                            table_title="Courses and student counts",
                            instructors=instructor)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')