
import streamlit as st
import pandas as pd
import joblib
from pathlib import Path

from database import (
    create_tables,
    save_student,
    update_student,
    get_all_students,
    get_latest_student,
    save_task,
    get_all_tasks,
    update_task_status,
    update_task_details,
    delete_task
)

# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="SmartStudy AI",
    page_icon="📚",
    layout="wide"
)



# Make sure database tables exist
create_tables()


# ==================================================
# 2. LOAD MACHINE LEARNING MODEL
# ==================================================

@st.cache_resource
def load_student_model():

    model_path = (
        Path(__file__).resolve().parent
        / "ml_model"
        / "student_model.pkl"
    )

    if not model_path.exists():
        return None, None

    try:
        saved_model = joblib.load(model_path)

        if not isinstance(saved_model, dict):
            raise ValueError("Invalid model file format.")

        if "model" not in saved_model or "features" not in saved_model:
            raise ValueError("Model or features are missing.")

        model = saved_model["model"]
        features = saved_model["features"]

        if not features:
            raise ValueError("Model features are empty.")

        return model, features

    except Exception as error:
        raise RuntimeError(
            f"Unable to load the ML model: {error}"
        ) from error

    model_path = (
        Path(__file__).resolve().parent
        / "ml_model"
        / "student_model.pkl"
    )

    if not model_path.exists():
        return None, None

    saved_model = joblib.load(model_path)

    return saved_model["model"], saved_model["features"]


def predict_score(study_hours, attendance, previous_marks, sleep_hours):

    model, features = load_student_model()

    if model is None:
        raise FileNotFoundError("ML model file not found.")

    input_values = {
        "Hours_Studied": study_hours,
        "Attendance": attendance,
        "Previous_Scores": previous_marks,
        "Sleep_Hours": sleep_hours
    }

    input_data = pd.DataFrame(
        [[input_values[feature] for feature in features]],
        columns=features
    )

    prediction = model.predict(input_data)[0]

    return max(0, min(100, float(prediction)))


# ==================================================
# 3. SIDEBAR NAVIGATION
# ==================================================

st.sidebar.title("📚 SmartStudy AI")
st.sidebar.write("Your Personal Study Assistant")

st.sidebar.divider()

menu = st.sidebar.selectbox(
    "Navigate",
    [
        "Dashboard",
        "Student Profile",
        "Performance Predictor",
        "Study Planner",
        "Analytics",
        "AI Recommendations",
        "What-If Simulator",
        "Student Records"
    ]
)


# ==================================================
# 4. FETCH DATABASE INFORMATION
# ==================================================

student = get_latest_student()
students = get_all_students()
tasks = get_all_tasks()

total_students = len(students)
total_tasks = len(tasks)

completed_tasks = sum(
    1 for task in tasks if bool(task[4])
)

pending_tasks = total_tasks - completed_tasks

completion_rate = (
    completed_tasks / total_tasks * 100
    if total_tasks > 0 else 0
)


# ==================================================
# 5. DASHBOARD
# ==================================================

if menu == "Dashboard":

    st.title("Welcome to SmartStudy AI 👋")

    st.write(
        "Your personal space to plan, track, "
        "and improve your studies."
    )

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Students", total_students)

    with col2:
        st.metric("Total Tasks", total_tasks)

    with col3:
        st.metric("Completed Tasks", completed_tasks)

    with col4:
        st.metric("Task Completion", f"{completion_rate:.1f}%")

    st.divider()

    st.subheader("📌 Student Overview")

    if student:

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Study Hours", f"{student[3]} hrs")

        with col2:
            st.metric("Attendance", f"{student[4]}%")

        with col3:
            st.metric("Previous Marks", f"{student[5]}%")

        st.write(f"**Student:** {student[1]}")
        st.write(f"**Course:** {student[2]}")
        st.write(f"**Sleep Hours:** {student[6]} hrs")

    else:

        st.info("Create your Student Profile to get started.")

    st.divider()

    st.subheader("📚 Recent Study Tasks")

    if tasks:

        for task in tasks[:5]:

            status = (
                "✅ Completed"
                if bool(task[4])
                else "⏳ Pending"
            )

            st.write(
                f"**{task[1]}** — {task[2]} | "
                f"Priority: {task[3]} | {status}"
            )

    else:

        st.info("No study tasks added yet.")


# ==================================================
# 6. STUDENT PROFILE
# ==================================================

elif menu == "Student Profile":

    st.title("👩‍🎓 Student Profile")
    st.write("Create or update your academic profile.")

    # Get existing student profile
    student = get_latest_student()

    # Load saved information
    if student:
        student_id = student[0]
        name_value = student[1]
        course_value = student[2]
        study_value = float(student[3])
        attendance_value = float(student[4])
        marks_value = float(student[5])
        sleep_value = float(student[6])
    else:
        student_id = None
        name_value = ""
        course_value = "B.Tech CSE"
        study_value = 4.0
        attendance_value = 75.0
        marks_value = 60.0
        sleep_value = 7.0

    courses = ["B.Tech CSE", "B.Tech IT", "BCA", "B.Sc", "Other"]

    with st.form("student_profile_form"):

        name = st.text_input("Full Name", value=name_value)

        course = st.selectbox(
            "Select Course",
            courses,
            index=courses.index(course_value)
            if course_value in courses else 0
        )

        study_hours = st.number_input(
            "Daily Study Hours",
            min_value=0.0,
            max_value=24.0,
            value=study_value,
            step=0.5
        )

        attendance = st.number_input(
            "Attendance Percentage",
            min_value=0.0,
            max_value=100.0,
            value=attendance_value
        )

        previous_marks = st.number_input(
            "Previous Exam Marks (%)",
            min_value=0.0,
            max_value=100.0,
            value=marks_value
        )

        sleep_hours = st.number_input(
            "Daily Sleep Hours",
            min_value=0.0,
            max_value=24.0,
            value=sleep_value,
            step=0.5
        )

        submitted = st.form_submit_button(
            "Update Profile" if student else "Save My Profile"
        )

    # Save or update profile
    if submitted:

        if not name.strip():
            st.error("Please enter your name.")

        elif student:
            update_student(
                student_id,
                name.strip(),
                course,
                study_hours,
                attendance,
                previous_marks,
                sleep_hours
            )

            st.success("Profile updated successfully!")
            st.rerun()

        else:
            save_student(
                name.strip(),
                course,
                study_hours,
                attendance,
                previous_marks,
                sleep_hours
            )

            st.success("Profile saved successfully!")
            st.rerun()

    # Display saved profile
    student = get_latest_student()

    if student:
        st.divider()
        st.subheader("Your Saved Profile")

        st.write("**Name:**", student[1])
        st.write("**Course:**", student[2])

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Study Hours", f"{student[3]} hrs")
            st.metric("Attendance", f"{student[4]}%")

        with col2:
            st.metric("Previous Marks", f"{student[5]}%")
            st.metric("Sleep Hours", f"{student[6]} hrs")


# ==================================================
# 7. PERFORMANCE PREDICTOR
# ==================================================

elif menu == "Performance Predictor":

    st.title("🤖 Performance Predictor")

    st.write(
        "Predict your examination performance "
        "using your trained Machine Learning model."
    )

    if not student:

        st.warning("Please create your Student Profile first.")

    else:

        col1, col2 = st.columns(2)

        with col1:

            study_hours = st.number_input(
                "Daily Study Hours",
                0.0, 24.0,
                float(student[3]),
                step=0.5,
                key="predict_hours"
            )

            attendance = st.number_input(
                "Attendance (%)",
                0, 100,
                int(student[4]),
                key="predict_attendance"
            )

        with col2:

            previous_marks = st.number_input(
                "Previous Marks (%)",
                0, 100,
                int(student[5]),
                key="predict_marks"
            )

            sleep_hours = st.number_input(
                "Sleep Hours",
                0.0, 24.0,
                float(student[6]),
                step=0.5,
                key="predict_sleep"
            )

        if st.button("Predict My Performance", type="primary"):

            try:

                score = predict_score(
                    study_hours,
                    attendance,
                    previous_marks,
                    sleep_hours
                )

                st.divider()

                st.subheader("Your Predicted Performance")

                st.metric(
                    "Estimated Exam Score",
                    f"{score:.2f}%"
                )

                st.progress(int(score))

                if score >= 80:
                    st.success("Excellent! Keep up your performance.")

                elif score >= 60:
                    st.info("Good progress! Keep improving.")

                else:
                    st.warning(
                        "Focus on consistent study and revision."
                    )

                st.caption(
                    "This is a model-based estimate, "
                    "not a guaranteed examination result."
                )

            except Exception as error:

                st.error(f"Prediction failed: {error}")


# ==================================================
# 8. STUDY PLANNER
# ==================================================

elif menu == "Study Planner":

    st.title("📚 Study Planner")
    st.write("Manage your daily study tasks.")

    # Add new task
    st.subheader("➕ Add New Study Task")

    with st.form("add_task_form"):

        subject = st.selectbox(
            "Select Subject",
            ["Java", "Python", "DBMS", "Mathematics", "Other"]
        )

        task = st.text_input("Enter Study Task")

        priority = st.selectbox(
            "Select Priority",
            ["High", "Medium", "Low"]
        )

        add_task_button = st.form_submit_button("Add Task")

        if add_task_button:

            if task.strip():

                save_task(subject, task.strip(), priority)

                st.success("Task added successfully!")
                st.rerun()

            else:
                st.warning("Please enter a task.")

    st.divider()

    # Display existing tasks
    st.subheader("📋 Your Study Tasks")

    tasks = get_all_tasks()

    if tasks:

        for task_data in tasks:

            task_id = task_data[0]
            subject = task_data[1]
            task_name = task_data[2]
            priority = task_data[3]
            completed = bool(task_data[4])

            with st.container(border=True):

                col1, col2 = st.columns([4, 1])

                with col1:

                    st.markdown(f"**{task_name}**")
                    st.caption(f"Subject: {subject}")

                    st.caption(f"Priority: {priority}")

                    if completed:
                        st.success("Completed")
                    else:
                        st.warning("Pending")

                with col2:

                    status = st.checkbox(
                        "Completed",
                        value=completed,
                        key=f"status_{task_id}"
                    )

                    if status != completed:
                        update_task_status(task_id, status)
                        st.rerun()

                # Edit task
                with st.expander("✏️ Edit Task"):

                    with st.form(f"edit_form_{task_id}"):

                        new_subject = st.selectbox(
                            "Subject",
                            ["Java", "Python", "DBMS", "Mathematics", "Other"],
                            index=(
                                ["Java", "Python", "DBMS", "Mathematics", "Other"]
                                .index(subject)
                                if subject in ["Java", "Python", "DBMS", "Mathematics", "Other"]
                                else 0
                            ),
                            key=f"subject_{task_id}"
                        )

                        new_task = st.text_input(
                            "Task",
                            value=task_name,
                            key=f"task_{task_id}"
                        )

                        new_priority = st.selectbox(
                            "Priority",
                            ["High", "Medium", "Low"],
                            index=["High", "Medium", "Low"].index(priority),
                            key=f"priority_{task_id}"
                        )

                        save_changes = st.form_submit_button(
                            "Save Changes"
                        )

                        if save_changes:

                            if new_task.strip():

                                update_task_details(
                                    task_id,
                                    new_subject,
                                    new_task.strip(),
                                    new_priority
                                )

                                st.success("Task updated successfully!")
                                st.rerun()

                            else:
                                st.warning("Task cannot be empty.")
        # Delete Task
        with st.expander("🗑️ Delete Task"):
            confirm_delete = st.checkbox(
                f"Confirm deletion of: {task_name}",
                key=f"confirm_delete_{task_id}"
            )

            if st.button(
                                "Delete Task",
                                key=f"delete_{task_id}",
                                disabled=not confirm_delete
                            ):
                                delete_task(task_id)
                                st.success("Task deleted successfully!")
                                st.rerun()


# ==================================================
# 9. ANALYTICS
# ==================================================

elif menu == "Analytics":

    st.title("📊 Study Analytics")

    st.write("Analyze your academic and study progress.")

    if not student:

        st.info("Create a Student Profile to view analytics.")

    else:

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Study Hours", f"{student[3]} hrs")

        with col2:
            st.metric("Attendance", f"{student[4]}%")

        with col3:
            st.metric("Previous Marks", f"{student[5]}%")

        st.divider()

        st.subheader("Academic Performance")

        performance_data = pd.DataFrame({
            "Category": ["Attendance", "Previous Marks"],
            "Percentage": [student[4], student[5]]
        })

        st.bar_chart(
            performance_data.set_index("Category")
        )

        st.divider()

        st.subheader("Study Task Progress")

        task_data = pd.DataFrame({
            "Status": ["Completed", "Pending"],
            "Tasks": [completed_tasks, pending_tasks]
        })

        st.bar_chart(
            task_data.set_index("Status")
        )

        st.write(
            f"**Task Completion Rate:** {completion_rate:.1f}%"
        )

        st.progress(int(completion_rate))


# ==================================================
# 10. AI RECOMMENDATIONS
# ==================================================

elif menu == "AI Recommendations":

    st.title("💡 AI Study Recommendations")

    st.write(
        "Study suggestions based on your academic information."
    )

    if not student:

        st.warning("Please create your Student Profile first.")

    else:

        recommendations = []

        if student[3] < 3:

            recommendations.append(
                "📚 Increase your daily study time gradually."
            )

        else:

            recommendations.append(
                "✅ Your study hours are good. Maintain consistency."
            )

        if student[4] < 75:

            recommendations.append(
                "📅 Improve your attendance to strengthen "
                "your academic performance."
            )

        else:

            recommendations.append(
                "✅ Your attendance is good. Keep it consistent."
            )

        if student[5] < 60:

            recommendations.append(
                "📝 Revise fundamentals and practice "
                "previous examination questions."
            )

        else:

            recommendations.append(
                "🎯 Continue practicing mock tests."
            )

        if student[6] < 7:

            recommendations.append(
                "😴 Try to maintain 7–9 hours of sleep."
            )

        else:

            recommendations.append(
                "✅ Maintain your healthy sleep routine."
            )

        if pending_tasks > 0:

            recommendations.append(
                f"⏳ You have {pending_tasks} pending tasks. "
                "Complete high-priority tasks first."
            )

        else:

            recommendations.append(
                "🎉 All your study tasks are completed!"
            )

        for recommendation in recommendations:

            st.info(recommendation)


# ==================================================
# 11. WHAT-IF SIMULATOR
# ==================================================

elif menu == "What-If Simulator":

    st.title("🔮 What-If Simulator")

    st.write(
        "Explore how changes in your study habits "
        "may affect your predicted examination score."
    )

    if not student:

        st.warning("Please create your Student Profile first.")

    else:

        col1, col2 = st.columns(2)

        with col1:

            simulated_hours = st.slider(
                "Daily Study Hours",
                0.0,
                12.0,
                min(float(student[3]), 12.0),
                step=0.5
            )

            simulated_attendance = st.slider(
                "Attendance (%)",
                0,
                100,
                int(student[4])
            )

        with col2:

            simulated_marks = st.slider(
                "Previous Marks (%)",
                0,
                100,
                int(student[5])
            )

            simulated_sleep = st.slider(
                "Sleep Hours",
                0.0,
                12.0,
                min(float(student[6]), 12.0),
                step=0.5
            )

        if st.button("Simulate My Performance", type="primary"):

            try:

                current_score = predict_score(
                    student[3],
                    student[4],
                    student[5],
                    student[6]
                )

                simulated_score = predict_score(
                    simulated_hours,
                    simulated_attendance,
                    simulated_marks,
                    simulated_sleep
                )

                difference = simulated_score - current_score

                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "Current Predicted Score",
                        f"{current_score:.2f}%"
                    )

                with col2:

                    st.metric(
                        "Simulated Predicted Score",
                        f"{simulated_score:.2f}%",
                        f"{difference:+.2f}%"
                    )

                st.progress(int(simulated_score))

                st.info(
                    "Both scores are generated using your trained "
                    "Machine Learning model."
                )

            except Exception as error:

                st.error(f"Simulation failed: {error}")


# ==================================================
# 12. STUDENT RECORDS
# ==================================================

elif menu == "Student Records":

    st.title("📋 Student Records")

    st.write("View all saved student profiles.")

    if not students:

        st.info("No student records found.")

    else:

        records = pd.DataFrame(
            students,
            columns=[
                "ID",
                "Name",
                "Course",
                "Study Hours",
                "Attendance",
                "Previous Marks",
                "Sleep Hours"
            ]
        )

        st.dataframe(
            records,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Total Student Records",
                len(records)
            )

        with col2:

            st.metric(
                "Average Previous Marks",
                f"{records['Previous Marks'].mean():.2f}%"
            )


# ==================================================
# 13. SIDEBAR FOOTER
# ==================================================

st.sidebar.divider()

st.sidebar.caption(
    "📚 SmartStudy AI | Your Personal Study Assistant"
)
