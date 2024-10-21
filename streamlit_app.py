import streamlit as st
import pandas as pd
from datetime import datetime
import random
from datetime import datetime, timedelta
import time
import threading
import cloudinary
import cloudinary.uploader
import os
# Function to save results to Excel
#st.image("Huawei.jpg", width=200)
# Use Streamlit's image function
#st.image("Huawei.jpg", width=150)

# Use Streamlit's image function to show the image on the left side
col1, col2 = st.columns([1, 3])  # Create 2 columns with ratios (left narrower than right)

with col1:  # Left column
    st.image("Huawei.jpg", width=80)

    # Cloudinary configuration (replace with your own Cloudinary credentials)
cloudinary.config(
    cloud_name="drpkmvcdb",  # Replace with your Cloudinary cloud name
    api_key="421723639371647",        # Replace with your Cloudinary API key
    api_secret="AWpJzomMBrw-5DHNqujft5scUbM"   # Replace with your Cloudinary API secret
)

def upload_to_cloudinary(file_path, public_id):
    try:
        response = cloudinary.uploader.upload(
            file_path,
            resource_type="raw",
            public_id=public_id,
            overwrite=True,  # Allow overwriting
            invalidate=True,  # Invalidate cached versions on CDN
            unique_filename=False,  # Do not generate a unique filename
            use_filename=True  # Use the file's original filename
        )
        return response['secure_url']
    except cloudinary.exceptions.Error as e:
        st.error(f"Cloudinary upload failed: {str(e)}")
        return None


# Function to save results to Excel and upload to Cloudinary
def save_results(username, total_attempted, correct_answers, wrong_answers, total_score, time_taken, details):   
    try:
        df = pd.read_excel("quiz_results_EHS.xlsx")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Username", "Date", "Total Attempted", "Correct Answers", "Wrong Answers", "Total Score", "Time Taken", "Details"])

    new_data = pd.DataFrame([[username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), total_attempted, correct_answers, wrong_answers, total_score, time_taken, details]],
                            columns=["Username", "Date", "Total Attempted", "Correct Answers", "Wrong Answers", "Total Score", "Time Taken", "Details"])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_excel("quiz_results_EHS.xlsx", index=False)

    # Upload the file to Cloudinary
    uploaded_url = upload_to_cloudinary("quiz_results_EHS.xlsx", "quiz_results_EHS")
    if uploaded_url:
        st.success(f"Quiz results uploaded successfully!")
        # st.markdown(f"Access your file here: [quiz_results.xlsx]({uploaded_url})")


# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'answers' not in st.session_state:
    st.session_state.answers = []
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'quiz_submitted' not in st.session_state:
    st.session_state.quiz_submitted = False
if 'flattened_questions' not in st.session_state:
    st.session_state.flattened_questions = []
    ########
# List of allowed usernames
allowed_usernames = {
"HIC_ISB_TrainingTeam_01.",
"HIC_ISB_TrainingTeam_02.",
"HIC_ISB_TrainingTeam_03.",
"HIC_ISB_TrainingTeam_04.",
"HIC_ISB_TrainingTeam_05."
}

# Define your questions
EHS = {
    "true_false": [
        {"question": "Persons working on electrical equipment must be authorized and competent.", "answer": "True"},
        {"question": "It can be allowed to access Rooftops during bad weather, Roof is 'WET', Exists Thunder or Lightening.", "answer": "False"},
        {"question": "In First Aid Kit, Mandatory Items are 10.", "answer": "False"},
        {"question": "Hazards identification in advance is a must even if you are certified on EHS.", "answer": "True"},
        {"question": "No live electrical work, which has the potential to cause electrical injury.", "answer": "False"},
        {"question": "If a driver drives the car very slowly, there is no need to fasten the seatbelt.", "answer": "False"},
        {"question": "No live-line working, which has the potential risk to cause electrical injury.", "answer": "True"},
        {"question": "The purpose of deploying project EHS management is to ensure work safely, successful delivery of the project, and improve customer satisfaction.", "answer": "True"},
        {"question": "Staff are responsible for complying with established procedures and instructions - including what to do in case of an emergency. They should only undertake tasks for which they are competent and authorized, and report any deviations from stated safe systems of work.", "answer": "True"},
        {"question": "Only qualified first aiders are allowed to use first aid to rescue casualties. This is to prevent further complication to the injured.", "answer": "True"},
        {"question": "If the firefighting system is not available on-site, we can still carry out our activities.", "answer": "False"},
        {"question": "Better EHS management with a higher total cost reduces the project profit.", "answer": "False"},
        {"question": "When workers find any damaged equipment or PPE, there is no need to report it to their site supervisor or line manager.", "answer": "False"},
        {"question": "If no internet is working on-site, there is no need to get approval from a supervisor; the field team can carry out operations.", "answer": "False"},
        {"question": "There is no need to fasten the safety belt when sitting in the backseat.", "answer": "False"},
        {"question": "If you drive or operate machinery or work at heights, there is no need to tell your supervisor if you take medication that makes you drowsy or impairs your ability. Just have a rest and restart your work when you feel better.", "answer": "False"},
        {"question": "The project team can request not to follow project EHS absolute rules when local resources are limited.", "answer": "False"},
        {"question": "Individuals are responsible only for their own safety, with no need to take care of others.", "answer": "False"},
        {"question": "Drivers should practice enough to use a hand-held phone while driving.", "answer": "False"},
        {"question": "Office equipment, such as faxes, Dictaphones, notebooks, etc., must never be used by drivers whilst the vehicle is in motion.", "answer": "True"},
        {"question": "The ladder used for safety work shall have no width limitation.", "answer": "True"},
        {"question": "Site Engineers are responsible for engineering quality, with no need to audit EHS.", "answer": "False"},
        {"question": "Only workers who have been trained and are competent can carry out safety work.", "answer": "True"},
        {"question": "There is no width requirement for ladders used safely.", "answer": "False"},
        {"question": "Casual shoes, sandals, or slippers are NOT allowed in the worksite.", "answer": "True"}
    ],
    "choose_correct": [
        {
            "question": "The key tasks for Site Supervisor are:",
            "options": [
                "A) Carry out an onsite risk assessment",
                "B) Ensure the rescue kit is on site and is suitable",
                "C) All PPE and equipment is fit for purpose and used",
                "D) Any exclusion zones (drop zones) are suitable"
                ],
            "answer": ["A", "B", "C", "D"]  # Correct answers
        },
        {
            "question": "All work at height requires planning. A risk assessment must be carried out to identify:",
            "options": [
                "A) The significant rated hazards",
                "B) The medium rated hazards",
                "C) The low rated hazards",
                "D) No hazards"
            ],
            "answer": ["A", "B", "C"]  # Correct answers
        },
        {
            "question": "RF safety needs to be minded following:",
            "options": [
                "A) All RF related working need competent and certified person",
                "B) Ensure to understand the safety area of antenna before approaching to antenna",
                "C) Need to shut down power if must work in unsafe area of RF",
                "D) Must not remove RF cable and connectors when they are running in order to avoid RF burst"
            ],
            "answer": ["A", "B", "C", "D"]  # Correct answers
        },
        {
            "question": "The project EHS management requirement comes from:",
            "options": [
                "A) Local EHS-related laws and regulations, international standards",
                "B) EHS-related clauses in the contract with the customer, customer’s requirements and expectations for EHS management",
                "C) Huawei minimum safety standards and EHS management absolute rules",
                "D) None of the above"
            ],
            "answer": ["A", "B", "C"]  # Correct answers
        },
        {
            "question": "EHS 3P Self-Management includes:",
            "options": [
                "A) Prepare to work safely",
                "B) Pre-Task Check",
                "C) Performing Check",
                "D) PPE Check"
            ],
            "answer": ["A", "B", "C"]  # Correct answers
        },
        {
            "question": "Working at height, PPE shall include:",
            "options": [
                "A) Head protection",
                "B) Foot protection",
                "C) Full body harness",
                "D) Eye protection"
            ],
            "answer": ["A", "B", "C", "D"]  # Correct answers
        },
        {
            "question": "Working at the tower safely:",
            "options": [
                "A) Not allow one rigger to work on tower, a watchman must standby",
                "B) Must check PPE and wear PPE per requirements",
                "C) Ensure lanyard is fixed at 2 different points",
                "D) Carried tools shall be kept in a bag to avoid being dropped down"
            ],
            "answer": ["A", "B", "C", "D"]  # Correct answers
        },
        {
            "question": "Field working:",
            "options": [
                "A) Need to prepare enough food as it is not convenient for food outside",
                "B) Normally need 2 or more workers to go to avoid being robbed or hurt by wild animals, take protection facility when needed, and avoid working late",
                "C) Need to wear anti-skidding shoes and clothes fit to the body",
                "D) None of the above"
            ],
            "answer": ["A", "B", "C"]  # Correct answers
        },
        {
            "question": "Working safety needs consideration of local weather patterns, such as:",
            "options": [
                "A) Wind speeds",
                "B) Temperature and temperature changes",
                "C) Humidity levels",
                "D) Snow/ice formation and type/frequency of rainfall"
            ],
            "answer": ["A", "B", "C", "D"]  # Correct answers
        },
        {
            "question": "Before work, need to analyze the risk source and take necessary actions for prevention with PPE for:",
            "options": [
                "A) Getting an electric shock",
                "B) Dropping from height",
                "C) Being hit by dropping product",
                "D) Traffic accidents"
            ],
            "answer": ["A", "B", "C", "D"]  # Correct answers
        },
        {
            "question": "Unsafe acts that cause accidents and incidents include:",
            "options": [
                "A) Working without authority",
                "B) Failure to warn others of danger",
                "C) Using dangerous or wrong equipment",
                "D) Horseplay"
            ],
            "answer": ["A", "B", "C", "D"]  # Correct answers
        },
        {
            "question": "EHS objectives are:",
            "options": [
                "A) Zero Fatalities",
                "B) Zero Injuries",
                "C) Zero Accidents",
                "D) Zero defects in the product"
            ],
            "answer": ["A", "B", "C"]  # Correct answers
        },
        {
            "question": "Safety areas of engineering construction must have:",
            "options": [
                "A) Alert signs and fence facilities",
                "B) Workers in unsafe areas need related protection (e.g., helmet, gloves, vest, eye protection glasses, and safety shoes) and necessary safety facilities and tools",
                "C) Dangerous operations must be equipped with emergency response and safety protection approaches for worker safety",
                "D) None of the above"
            ],
            "answer": ["A", "B", "C"]  # Correct answers
        },
        {
            "question": "Risks to health and safety that may arise from radio frequency (RF) fields include:",
            "options": [
                "A) Interaction of RF fields with the human body",
                "B) Interference with medical equipment",
                "C) Interference with safety-related electronics",
                "D) Fuel and flammable atmospheres"
            ],
            "answer": ["A", "B", "C", "D"]  # Correct answers
        },
        {
            "question": "Managing EHS Risk includes:",
            "options": [
                "A) EHS Risk recognition",
                "B) EHS Risk evaluation",
                "C) EHS Risk control",
                "D) EHS Risk monitoring"
            ],
            "answer": ["A", "B", "C", "D"]  # Correct answers
        },
        {
            "question": "Safety Signs should include but not be limited to the following:",
            "options": [
                "A) No access to unauthorized persons",
                "B) Safety Helmets must be worn",
                "C) Working at height",
                "D) None of the above"
            ],
            "answer": ["A", "B", "C"]  # Correct answers
        },
        {
            "question": "EHS Check in project delivery includes:",
            "options": [
                "A) Subcontractor Self-check",
                "B) Random Spot-check",
                "C) No check",
                "D) Leadership Safety Tour"
            ],
            "answer": ["A", "B", "D"]  # Correct answers
        },
        {
            "question": "For electrical safety:",
            "options": [
                "A) Power cables are not allowed to be put on the ground",
                "B) Overload for power cable is not allowed",
                "C) Damaged components of power must be replaced in time",
                "D) None of the above"
            ],
            "answer": ["A", "B", "C"]  # Correct answers
        },
        {
            "question": "For vehicle seat belts, the correct answers are:",
            "options": [
                "A) All company vehicles fitted with seat belts",
                "B) Seat belts checked as part of routine maintenance",
                "C) Driver training includes the use of seat belts",
                "D) None of the above"
            ],
            "answer": ["A", "B", "C"]  # Correct answers
        },
        {
            "question": "Fitness to drive can be affected by a number of issues:",
            "options": [
                "A) Illness",
                "B) Drug use",
                "C) Alcohol consumption",
                "D) Age"
            ],
            "answer": ["A", "B", "C", "D"]  # Correct answers
        }
    ],
    "multiple_choice": [
        {
            "question": "“E”, “H” & “S” inside of EHS represents the meanings of:",
            "options": [
                "A) E - Ear; H - Head; S - Safety",
                "B) E - Earthquake; H - Height; S - Safety",
                "C) E – Environment; H – Health; S - Safety",
                "D) None of the above"
            ],
            "answer": "C) E – Environment; H – Health; S - Safety"  # Correct answer
        },
        {
            "question": "What is the maximum temperature for working at height?",
            "options": [
                "A) 34°C",
                "B) 40°C",
                "C) 44°C",
                "D) 45°C"
            ],
            "answer": "D) 45°C"  # Correct answer
        },
        {
            "question": "The purpose of keeping the work site clear and tidy is:",
            "options": [
                "A) Comfortable for work",
                "B) Any protruding nails can wound workers or bend them over",
                "C) Meeting the requirements of EHS laws",
                "D) None of the above"
            ],
            "answer": "B) Any protruding nails can wound workers or bend them over"  # Correct answer
        },
        {
            "question": "Job Hazard Analysis been completed on First Aid Kit and Tower Rescue Kit includes:",
            "options": [
                "A) Emergency services phone numbers, location, and map",
                "B) Home address",
                "C) Office location",
                "D) None of the above"
            ],
            "answer": "A) Emergency services phone numbers, location, and map"  # Correct answer
        },
        {
            "question": "Project EHS Management is implemented in delivery project:",
            "options": [
                "A) Plan phase",
                "B) Establish phase",
                "C) Realize phase",
                "D) Whole life cycle"
            ],
            "answer": "D) Whole life cycle"  # Correct answer
        },
        {
            "question": "For working at height (unsafe zone):",
            "options": [
                "A) Allow worker to walk underneath",
                "B) Allow worker to walk underneath if another watchman reminds of danger",
                "C) Never allow worker to walk underneath",
                "D) All of the above are wrong"
            ],
            "answer": "C) Never allow worker to walk underneath"  # Correct answer
        },
        {
            "question": "The radius of the load drop zone equals ( ) the height of the load:",
            "options": [
                "A) 0.1",
                "B) 0.3",
                "C) 0.5",
                "D) 0.8"
            ],
            "answer": "C) 0.5"  # Correct answer
        },
        {
            "question": "In most countries, working at height is defined as:",
            "options": [
                "A) 1m or above",
                "B) 3m or above",
                "C) 5m or above",
                "D) 2m or above"
            ],
            "answer": "C) 5m or above"  # Correct answer
        },
        {
            "question": "Manual lifting: Pulling strength shall be:",
            "options": [
                "A) Not allow sudden pull, sudden stop",
                "B) Allow sudden pull, sudden stop",
                "C) If pulling strength is enough, allow sudden pull, sudden stop",
                "D) None of the above"
            ],
            "answer": "A) Not allow sudden pull, sudden stop"  # Correct answer
        },
        {
            "question": "The most important activity for EHS management is:",
            "options": [
                "A) Prevention",
                "B) Corrective actions",
                "C) Quick reactions",
                "D) No response to accidents or incidents"
            ],
            "answer": "A) Prevention"  # Correct answer
        },
        {
            "question": "If drivers choose to make or receive calls while driving, we strongly recommend that they use:",
            "options": [
                "A) A hand-held phone",
                "B) A hands-free facility",
                "C) No need to attend the call",
                "D) None of the above"
            ],
            "answer": "B) A hands-free facility"  # Correct answer
        },
        {
            "question": "Working at height needs to consider environmental conditions such as:",
            "options": [
                "A) 5S",
                "B) Wind, Heat, Cold, and Lightness",
                "C) Dirty or clean",
                "D) Noise"
            ],
            "answer": "B) Wind, Heat, Cold, and Lightness"  # Correct answer
        },
        {
            "question": "( ) are needed for special work (like working at height, manual soldering, etc.):",
            "options": [
                "A) Qualified by defined technical training and get related certificate",
                "B) Only safety training is enough",
                "C) If the worker has enough experience, no need to take a certificate",
                "D) All of the above are wrong"
            ],
            "answer": "A) Qualified by defined technical training and get related certificate"  # Correct answer
        },
        {
            "question": "Anyone who could be affected by the work they are carrying out safely will ensure:",
            "options": [
                "A) Inspect their safety equipment and PPE before they use it",
                "B) Inspect their safety equipment and PPE after they use it",
                "C) Inspect their safety equipment and PPE during their use",
                "D) No need to inspect their safety equipment and PPE"
            ],
            "answer": "A) Inspect their safety equipment and PPE before they use it"  # Correct answer
        },
        {
            "question": "Lifting a product to height, the product shall be:",
            "options": [
                "A) Tied tightly and locked with a safety facility",
                "B) Tied loosely for easy unjointing",
                "C) Tied and don’t unlock",
                "D) All of the above are wrong"
            ],
            "answer": "A) Tied tightly and locked with a safety facility"  # Correct answer
        },
        {
            "question": "For working at height, you need an Ended Lanyard:",
            "options": [
                "A) One",
                "B) Two",
                "C) Zero",
                "D) More than Two"
            ],
            "answer": "B) Two"  # Correct answer
        },
        {
            "question": "When carrying heavy objects by hand, you need to keep your head:",
            "options": [
                "A) Looking down on the ground",
                "B) Looking straight",
                "C) Looking at the heavy objects",
                "D) None of the above"
            ],
            "answer": "B) Looking straight"  # Correct answer
        },
        {
            "question": "Working in the tower requires a minimum of qualified persons:",
            "options": [
                "A) One",
                "B) Two",
                "C) Three",
                "D) Four"
            ],
            "answer": "B) Two"  # Correct answer
        },
        {
            "question": "The right answers for working on towers are:",
            "options": [
                "A) You can climb a tower alone; there must always be a watchman with you",
                "B) You check your harness prior to use and wear your safety harness while climbing",
                "C) Secure yourself with only one lanyard at one point",
                "D) Can climb a tower when it’s rainy or too windy, if you are a certified person"
            ],
            "answer": "B) You check your harness prior to use and wear your safety harness while climbing"  # Correct answer
        },
        {
            "question": "After how long a time of driving must the driver stop the vehicle?",
            "options": [
                "A) 2.5 hours",
                "B) 4 hours",
                "C) 3 hours",
                "D) 3.5 hours"
            ],
            "answer": "C) 3 hours"  # Correct answer
        },
        {
            "question": "EHS Accident investigations begin:",
            "options": [
                "A) The moment an accident occurred",
                "B) Within 1 day when an accident occurred",
                "C) Within 3 days when an accident occurred",
                "D) Within 7 days when an accident occurred"
            ],
            "answer": "A) The moment an accident occurred"  # Correct answer
        },
        {
            "question": "After submitting pictures from field engineers, how much time must the approver take to approve the task?",
            "options": [
                "A) 20 minutes",
                "B) 1.5 hours",
                "C) 30 minutes",
                "D) 10 minutes"
            ],
            "answer": "C) 30 minutes"  # Correct answer
        },
        {
            "question": "All PPE must be fit for ( ) and inspections carried out as per the manufacturer’s instructions and compliant with the local applicable standards. If these are not known, then European EN standards should be used:",
            "options": [
                "A) Purpose and maintenance",
                "B) Checking",
                "C) Working comfortably",
                "D) None of the above"
            ],
            "answer": "A) Purpose and maintenance"  # Correct answer
        }
    ]
}
# Flatten questions for navigation
if not st.session_state.flattened_questions:
    flattened_questions = []

    for category, qs in EHS.items():
        for q in qs:
            q['type'] = category  # Set the type for each question
            flattened_questions.append(q)

    # Shuffle questions within each type
    random.shuffle(flattened_questions)

    true_false_questions = [q for q in flattened_questions if q['type'] == 'true_false']
    choose_correct_questions = [q for q in flattened_questions if q['type'] == 'choose_correct']
    mcq_questions = [q for q in flattened_questions if q['type'] == 'multiple_choice']

    # Combine the questions in the desired order
    all_questions = (
    true_false_questions[:15] + 
    choose_correct_questions[:10] + 
    mcq_questions[:15]
)

    # Limit to the first 40 questions
    st.session_state.flattened_questions = all_questions[:40]

# Initialize answers
if len(st.session_state.answers) != len(st.session_state.flattened_questions):
    st.session_state.answers = [None] * len(st.session_state.flattened_questions)


# Login form
if not st.session_state.logged_in:
    st.header("Welcome to Huawei Quiz Portal")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")  # You might want to handle password validation separately

    if st.button("Login"):
        if username in allowed_usernames and password:  # Add password validation as needed
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.start_time = datetime.now()  # Track start time on login
            st.success("Logged in successfully!")
            st.session_state.logged_in = True
            st.experimental_set_query_params()  # Ensures the state is saved and reloaded without rerunning the entire script
        else:
            st.error("Please enter a valid username and password.")
else:
    st.sidebar.markdown(f"## Welcome **{st.session_state.username}** For The Quiz Of EHS Assurance ")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.current_question = 0  # Reset current question
        st.session_state.answers = [None] * len(st.session_state.flattened_questions)  # Reset answers
        st.session_state.username = ""
        st.session_state.quiz_submitted = False  # Reset quiz submission status
        st.session_state.flattened_questions = []  # Reset questions
        st.success("You have been logged out.")
        # st.experimental_rerun()  # Refresh the page to reflect the new state
        

    # Quiz Page
    st.header(f"Welcome {st.session_state.username} For The Quiz Of EHS Assurance")

    # Navigation buttons
    col1, col2 = st.columns(2)

    # Only show navigation buttons if the quiz hasn't been submitted
    if not st.session_state.quiz_submitted:
        if st.session_state.current_question > 0:
            with col1:
                if st.button("Previous", key="prev"):
                    st.session_state.current_question -= 1

        if st.session_state.current_question < len(st.session_state.flattened_questions) - 1:
            with col2:
                if st.button("Next", key="next"):
                    st.session_state.current_question += 1

    if st.session_state.current_question == len(st.session_state.flattened_questions) - 1 and not st.session_state.quiz_submitted:
        if st.button("Submit", key="submit"):
            if not st.session_state.quiz_submitted:  # Only process if not already submitted
                total_score = 0
                questions_attempted = 0
                correct_answers = 0
                wrong_answers = 0
                result_details = []

                for idx, question_detail in enumerate(st.session_state.flattened_questions):
                    user_answer = st.session_state.answers[idx]
                    if user_answer is not None:
                        questions_attempted += 1
                        
                        if question_detail["type"] == "true_false":
                            
                            score = 2
                            if user_answer == question_detail["answer"]:
                                correct_answers += 1
                                total_score += score
                                result_details.append((question_detail["question"], user_answer, question_detail["answer"], "Correct"))
                            else:
                                wrong_answers += 1
                                result_details.append((question_detail["question"], user_answer, question_detail["answer"], "Wrong"))
                        elif question_detail["type"] == "choose_correct":
                            score = 4
                            if sorted(user_answer) == sorted(question_detail["answer"]):
                                correct_answers += 1
                                total_score += score
                                result_details.append((question_detail["question"], user_answer, question_detail["answer"], "Correct"))
                            else:
                                wrong_answers += 1
                                result_details.append((question_detail["question"], user_answer, question_detail["answer"], "Wrong"))
                        elif question_detail["type"] == "multiple_choice":
                            score = 2
                            if user_answer == question_detail["answer"]:
                                correct_answers += 1
                                total_score += score
                                result_details.append((question_detail["question"], user_answer, question_detail["answer"], "Correct"))
                            else:
                                wrong_answers += 1
                                result_details.append((question_detail["question"], user_answer, question_detail["answer"], "Wrong"))

                end_time = datetime.now()
                time_taken = end_time - st.session_state.start_time
                
                save_results(st.session_state.username, questions_attempted, correct_answers, wrong_answers, total_score, str(time_taken), str(result_details))
                st.success("Quiz submitted successfully!")
                st.session_state.quiz_submitted = True

                total_marks = 100  # Total marks for the quiz
                percentage = (total_score / total_marks) * 100
                result_message = "<h1 style='color: green;'>Congratulations! You passed the Test!</h1>" if percentage >= 70 else "<h1 style='color: red;'>Sorry You Have Failed The Test!.</h1>"

                # Display results in a card
                st.markdown("<div class='card'><h3>Quiz Results</h3>", unsafe_allow_html=True)
                st.markdown(result_message, unsafe_allow_html=True)
                st.write(f"**Total Questions Attempted:** {questions_attempted}")
                st.write(f"**Correct Answers:** {correct_answers}")
                st.write(f"**Wrong Answers:** {wrong_answers}")
                st.write(f"**Total Score:** {total_score}")
                st.write(f"**Percentage:** {percentage:.2f}%")
                st.markdown("</div>", unsafe_allow_html=True)

    # CSS for enhanced design
    st.markdown("""<style>
        .card {
            background-color: #ffcccc; /* Light background */
            border: 1px solid #ddd; /* Subtle border */
            border-radius: 8px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .question-card {
            background-color: #ffcccc; /* Light red color for questions */
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
    </style>""", unsafe_allow_html=True)

    # Display current question if quiz is not submitted
    if not st.session_state.quiz_submitted and st.session_state.current_question < len(st.session_state.flattened_questions):
        current_question = st.session_state.flattened_questions[st.session_state.current_question]
        total_questions = 40  # Total number of questions

        question_number = st.session_state.current_question + 1 
        progress_percentage = question_number / total_questions
        st.write(f"**Question {question_number} of {total_questions}**")  # Question count
        st.progress(progress_percentage)
        
        st.markdown(f"<div class='question-card'><h4>Question {question_number}: {current_question['question']}</h4></div>", unsafe_allow_html=True)

        # Display options based on question type
        if current_question["type"] == "multiple_choice":
            st.header('Multiple Choice Questions')
            st.session_state.answers[st.session_state.current_question] =  st.radio("Choose an option:", current_question["options"], key=f"mc_{st.session_state.current_question}")
        elif current_question["type"] == "true_false":
            st.header('True False')
         
            st.session_state.answers[st.session_state.current_question] =st.radio("Choose an option:", ["True", "False"], key=f"tf_{st.session_state.current_question}")
        elif current_question["type"] == "choose_correct":
            st.header('Choose The Correct')
           
            st.session_state.answers[st.session_state.current_question] =st.multiselect("Choose correct options:", current_question["options"], key=f"cc_{st.session_state.current_question}")

# Add a footer
st.markdown("<footer style='text-align: center; margin-top: 20px;'>© 2024 Huawei Training Portal. All Rights Reserved.</footer>", unsafe_allow_html=True)
