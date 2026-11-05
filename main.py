print("========================")
print("WELCOME TO SMARTSTUDY AI")
print("========================")
student_name = input("Enter your name :")

print("Welcome" , student_name)

study_hours =float (input("How many hours do you study daily?"))
attendance_percentage =float(input("What is your attendance percentage?"))
previous_marks = float(input("What were your previous exam marks?"))
sleep_hours = float(input("How many hours do you sleep?"))

print("\n=========STUDENT REPORT=========")
print("Student Name:", student_name)

print("Study Hours:", study_hours)

print("Attendance:", attendance)

print("Previous Marks:", previous_marks)

print("Sleep Hours:", sleep_hours)

print("======= STUDENT ANALYSIS======")

#ATTENDENCE ANALYSIS

if attendance >= 85:
    print("Attendance : Excellent")
    
elif attendance >= 75:
    print("Attendance : Good")
    
elif attendance >=50:
    print("Attendance: Needs improvement")
    
else :
    print("Attendance : very low")  
    
if study_hours >= 4:
    print("Study Habit: Good")

elif study_hours >= 2:
    print("Study Habit: Average")

else:
    print("Study Habit: Needs More Practice")


# Previous marks analysis

if previous_marks >= 75:
    print("Academic Performance: Excellent")

elif previous_marks >= 50:
    print("Academic Performance: Average")

else:
    print("Academic Performance: Needs Improvement")


# Sleep analysis

if sleep_hours >= 7:
    print("Sleep: Good")

else:
    print("Sleep: Try to maintain a healthier sleep schedule")      
