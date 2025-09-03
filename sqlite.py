import sqlite3

#Make a connection
connection=sqlite3.connect('student.db')

#Create a cursor to create a table or to insert new entries
cursor=connection.cursor()

#create a new table
table_info='''
CREATE TABLE STUDENT(NAME VARCHAR(25),CLASS VARCHAR(25),SECTION VARCHAR(25),MARKS INT)
'''
cursor.execute(table_info)

#Insert new entries
cursor.execute('''INSERT INTO STUDENT
               VALUES
               ('John', 'Data Science', 'A' ,98)''')
cursor.execute('''INSERT INTO STUDENT
               VALUES
               ('Mia', 'Robotics', 'B' ,69)''')
cursor.execute('''INSERT INTO STUDENT
               VALUES
               ('Rajesh', 'Machine Learning', 'A' ,55)''')
cursor.execute('''INSERT INTO STUDENT
               VALUES
               ('Jacob', 'Data Science', 'C' ,78)''')
cursor.execute('''INSERT INTO STUDENT
               VALUES
               ('Mukesh', 'AI', 'B' ,94)''')

#Printing the table values
print("The inserted records are:")
data=cursor.execute("SELECT * FROM STUDENT")
for row in data:
    print(row)

#Commiting the changes and closing the connections
connection.commit()
connection.close()
