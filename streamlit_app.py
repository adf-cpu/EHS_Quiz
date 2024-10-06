import streamlit as st
import pandas as pd
from datetime import datetime
import random
import cloudinary
import cloudinary.uploader
import cloudinary.api
import os


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
def save_results_to_cloudinary(username, total_attempted, correct_answers, wrong_answers, total_score, time_taken, details):   
    try:
        df = pd.read_excel("quiz_results_1.xlsx")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Username", "Date", "Total Attempted", "Correct Answers", "Wrong Answers", "Total Score", "Time Taken", "Details"])

    new_data = pd.DataFrame([[username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), total_attempted, correct_answers, wrong_answers, total_score, time_taken, details]],
                            columns=["Username", "Date", "Total Attempted", "Correct Answers", "Wrong Answers", "Total Score", "Time Taken", "Details"])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_excel("quiz_results_1.xlsx", index=False)

    # Upload the file to Cloudinary
    uploaded_url = upload_to_cloudinary("quiz_results_1.xlsx", "fixed_quiz_results_1")
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

# Define your questions
questions = {
    "true_false": [
        {"question": "When the outdoor feeders enter the indoor system, they need to be connected to the surge protector to protect the BTS equipment against damages from lightning.", "answer": "False"},
        {"question": "According to radiation direction, the antenna can be classified into omni directional antenna and directional antenna.", "answer": "True"},
        {"question": "The level-2 VSWR alarm will cause a serious consequence, therefore, it is better to set the level-2 VSWR threshold lower than 2.0.", "answer": "True"},
        {"question": "Jumper is quite soft, its common specification is 1/2” and can be used for long distance connection.", "answer": "False"},
        {"question": "When installed on a tower, only one RRU can be installed in standard mode or reverse mode, and two RRUs can be installed on a pole in back-to-back mode. RRUs cannot be installed on the side, and the brackets for more than two RRUs cannot be combined.", "answer": "False"},
        {"question": "The labels of communication cables, feeder cables and jumper should be stuck and tied according to specifications. The labels should be arranged in an orderly way with same direction.", "answer": "True"},
        {"question": "The jumper of the antenna should be tied along the rail of the support to the steel frame of the power.", "answer": "True"},
        {"question": "The black cable tie used for outdoor cable colligation and fixation normally.", "answer": "True"},
        {"question": "The feeder cable's bending radius should be more than ten times of the cable's diameter.", "answer": "True"},
        {"question": "Electrical tilt antenna has remote control function, can control the downtilt angle, azimuth angle remotely.", "answer": "False"},
        {"question": "3～5mm should left When cut off the surplus binding strap to resist expansion and contraction.", "answer": "True"},
        {"question": "BBU3900 can be installed in the 19-Inch’s cabinet.", "answer": "True"},
        {"question": "It’s necessary to make a drip-loop before the cable entering the feeder window, and the entrance of the feeder-window must be waterproofed.", "answer": "True"},
        {"question": "It’s forbidden to look at the laser directly, also the laser shouldn’t be directed at eyes.", "answer": "True"},
        {"question": "The Electronic Serial Number (ESN) is not a unique identifier of a Network Element(NE). Record the ESN for later commissioning of the base station before installation.", "answer": "False"},
        {"question": "When you connect RFUs to ISM6 boards, it is recommended that you connect RFUs in the same polarization direction to ISM6 board ports of the same ID. For example, connect RFUs in the vertical polarization direction to ISM6 board ports whose IDs are 1, and connect RFUs in the horizontal polarization direction to ISM6 board ports whose IDs are 2.", "answer": "True"},
        {"question": "Exposed live parts such as diesel generator, transformer and distribution cabinet shall be insulated or isolated, and the electric shock hazard sign shall be posted.", "answer": "True"},
        {"question": "As shown in the following photo, the clearance after site construction is complete meets the quality requirements.", "answer": "False"},
        {"question": "The power cable and grounding cable must be made of copper core materials, and there can be connectors in the middle.", "answer": "True"},
        {"question": "Huawei microwave IDIJ supports two power supply voltages: -48 V DC and -60 V DC. The allowed voltage ranges from -38.4 V DC to -72 V DC.", "answer": "True"},
        {"question": "Two ground cables can be connected to the same grounding hole on grounding busbar.", "answer": "False"},
        {"question": "The bolt installed in the following photo are correct.", "answer": "False"},
        {"question": "The vertical deviation of cabinets and the clearance between combined cabinets should be less than 3 mm. The cabinets in each row along the main aisle should be in a straight line with the deviation less than 5 mm.", "answer": "True"},
        {"question": "Keep at least 10 mm spacing between storage batteries to facilitate heat dissipation during storage battery operation.", "answer": "True"},
        {"question": "Adding a Female Fast Connector (Screw-free Type) to the RRU Power Cable on the RRU Side, the stripped length of the power cable must be greater than or equal to 18 mm, each core wire must be exposed outside the female fast connector (screw-free type) (ensure that the exposed part is not excessively long), and the connector must not press the outer insulation layer of the power cable.", "answer": "True"},
        {"question": "Route the RRU power cable from the RRU side to the power equipment side through the feeder window. Install a ground clip near the feeder window outside the equipment room, Wrap three layers of waterproof tape and three layers of insulation tape around the ground clip. And connect the PGND cable on the ground clip to the external ground bar.", "answer": "True"},
        {"question": "After the ODIJ is unpacked, it must be powered on within 24 hours to avoid moisture accumulation in it.", "answer": "True"},
    ],
    "choose_correct": [
        {
            "question": "What are the impacts of level-1 VSWR alarm?",
            "options": ["A) Service interrupt", "B) The RF emissive power reduces", "C) The amplifier of RF unit is shut down", "D) Shrink the cell coverage"],
            "answer": ["B) The RF emissive power reduces", "D) Shrink the cell coverage"]  # Correct answers
        },
        {
            "question": "Which type of the transmission can be supported by WMPT board?",
            "options": ["A) E1/T1", "B) Electronic IP", "C) Optical IP", "D) Microwave"],
            "answer": ["A) E1/T1", "B) Electronic IP", "C) Optical IP"]  # Correct answers
        },
        {
            "question": "BBU3900’s functions include:",
            "options": [
                "A) Interactive communication between BTS and BSC", 
                "B) Provide the system clock", 
                "C) BTS Centralized Management", 
                "D) Provide the maintenance channel with LMT (or M2000)"
            ],
            "answer": ["A) Interactive communication between BTS and BSC", "B) Provide the system clock", "C) BTS Centralized Management", "D) Provide the maintenance channel with LMT (or M2000)"]  # All options are correct
        },
        {
            "question": "Option board of BBU3900 include:",
            "options": [
                "A) Power module UPEU", 
                "B) E1 surge protector UELP", 
                "C) Universal clock unit USCU", 
                "D) Environment monitor interface board UEIU"
            ],
            "answer": ["B) E1 surge protector UELP", "C) Universal clock unit USCU", "D) Environment monitor interface board UEIU"]  # Correct answers
        },
        {
            "question": "The typical installation of BTS3900 include:",
            "options": ["A) Concrete floor", "B) Stub fixed", "C) ESD floor", "D) Sand ground installation"],
            "answer": ["A) Concrete floor", "C) ESD floor"]  # Correct answers
        },
        {
            "question": "Which of the following statements of grounding is correct?",
            "options": [
                "A) First connect grounding cables when installation; unmount grounding cables at the end when Un-deployment", 
                "B) Destroy grounding conductor is prohibit", 
                "C) Operate device before installing grounding conductor is prohibit", 
                "D) Device should ground with reliability"
            ],
            "answer": ["A) First connect grounding cables when installation; unmount grounding cables at the end when Un-deployment", "C) Operate device before installing grounding conductor is prohibit", "D) Device should ground with reliability"]  # Correct answers
        },
        {
            "question": "Which of following statements of GPS installation is correct?",
            "options": [
                "A) GPS antenna should install at the protect area of lighting rod (45 degree below the lighting rod top)", 
                "B) Keep metal base horizon, use washer when need", 
                "C) Fixing the GPS firmly, nothing block the vertical 90 degree area of the antenna", 
                "D) Waterproof is needed at the connector between GPS antenna and feeder"
            ],
            "answer": ["A) GPS antenna should install at the protect area of lighting rod (45 degree below the lighting rod top)", "B) Keep metal base horizon, use washer when need", "C) Fixing the GPS firmly, nothing block the vertical 90 degree area of the antenna", "D) Waterproof is needed at the connector between GPS antenna and feeder"]  # All options are correct
        }
    ],
    "multiple_choice": [
        {
            "question": "The height of DCDU is:",
            "options": ["A) 1 U", "B) 2 U", "C) 3 U", "D) 4 U"],
            "answer": "A) 1 U"  # Correct answer
        },
        {
            "question": "What is the distance between each feeder cable clip?",
            "options": ["A) 1.5~2M", "B) 2~2.5M", "C) 2.5~3M", "D) 2~2.5M"],
            "answer": "A) 1.5~2M"  # Correct answer
        },
        {
            "question": "After the installation of BTS3900 cabinet, the vertical error should be less than:",
            "options": ["A) 2mm", "B) 3mm", "C) 4mm", "D) 5mm"],
            "answer": "B) 3mm"  # Correct answer
        },
        {
            "question": "Which cabinet is always used indoor?",
            "options": ["A) BTS3900", "B) BTS3900A", "C) APM30", "D) BTS3902E"],
            "answer": "A) BTS3900"  # Correct answer
        },
        {
            "question": "Which description is wrong as below?",
            "options": [
                "A) The jumper connectors must be protected before hoisting.",
                "B) The antenna and jumper cable can’t be hoisted together.",
                "C) Before hoisting the antenna, the hoisting rope bind on the upper antenna bracket, the steering rope bind on the lower antenna bracket.",
                "D) When hoisting the antenna, one group of people pulls the hoisting rope down, while another group pulls the steering rope away from the tower, preventing the antenna from hitting the tower."
            ],
            "answer": "B) The antenna and jumper cable can’t be hoisted together."  # Correct answer
        },
        {
            "question": "When pasting the indoor labels, keep ___ between the label and the end of the cable, and all directions must be consistent.",
            "options": ["A) 1-5mm", "B) 20-30mm", "C) 30-40mm", "D) 40-50mm"],
            "answer": "B) 20-30mm"  # Correct answer
        },
        {
            "question": "The jumper cable’s size of RRU commonly is:",
            "options": ["A) 1/4 inch", "B) 1/2 inch", "C) 5/4 inch", "D) 7/8 inch"],
            "answer": "B) 1/2 inch"  # Correct answer
        },
        {
            "question": "Usually, 2G antenna uses ___ RCU.",
            "options": ["A) 0", "B) 1", "C) 2", "D) 3"],
            "answer": "A) 0"  # Correct answer
        },
        {
            "question": "Making the OT terminal of the 16mm² grounding cable, the terminal’s type is:",
            "options": ["A) 12", "B) 14", "C) 15", "D) 16"],
            "answer": "B) 14"  # Correct answer
        },
        {
            "question": "The fiber work-temperature is ___, exceeding scope needs protection.",
            "options": ["A) -40°~60°", "B) -30°~60°", "C) -40°~50°", "D) -45°~70°"],
            "answer": "A) -40°~60°"  # Correct answer
        },
        {
            "question": "In Swap sites the transmission equipment will get power from:",
            "options": ["A) DCDU_BLVD", "B) DCDU_LLVD", "C) DC PDB", "D) AC PDB"],
            "answer": "A) DCDU_BLVD"  # Correct answer
        },
        {
            "question": "What is the function of RCU module in the antenna system?",
            "options": [
                "A) It receives and runs the control commands from the base station and drives the stepper motor.",
                "B) It is the passive component that couples RF signals or OK signals with feeder signals.",
                "C) It provides DC power supply and control commands through the feeder.",
                "D) It amplifies the weak signals received from the antenna to increase the receiver sensitivity of the base station system."
            ],
            "answer": "A) It receives and runs the control commands from the base station and drives the stepper motor."  # Correct answer
        },
        {
            "question": "Which of the following RF components can be used to remotely control the tilt of the antenna?",
            "options": ["A) Combiner", "B) BT", "C) RCU", "D) Divider"],
            "answer": "C) RCU"  # Correct answer
        }
    ]
}

# Flatten questions for navigation
if not st.session_state.flattened_questions:
    flattened_questions = []

    # Process each category and set type
    for category, qs in questions.items():
    

        for q in qs:
            q['type'] = category  # Set the type for each question
            

            flattened_questions.append(q)

    # Shuffle questions within each type
    random.shuffle(flattened_questions)

    # Split back into categories
   

    true_false_questions = [q for q in flattened_questions if q['type'] == 'true_false']
    choose_correct_questions = [q for q in flattened_questions if q['type'] == 'choose_correct']
    mcq_questions = [q for q in flattened_questions if q['type'] == 'multiple_choice']
    

    # Shuffle each category
    
    
    random.shuffle(true_false_questions)
    random.shuffle(choose_correct_questions)
    random.shuffle(mcq_questions)

    # Combine the questions in the desired order
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
    # Display headings for question sections
    



# Login form
if not st.session_state.logged_in:
    st.header("Welcome to Huawei Quiz Portal")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username and password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.start_time = datetime.now()  # Track start time on login
            st.success("Logged in successfully!")
            st.experimental_rerun()  # Refresh the page to reflect the new state
        else:
            st.error("Please enter a valid username and password.")
else:
    st.sidebar.markdown(f"## Welcome **{st.session_state.username}**")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.current_question = 0  # Reset current question
        st.session_state.answers = [None] * len(st.session_state.flattened_questions)  # Reset answers
        st.session_state.username = ""
        st.session_state.quiz_submitted = False  # Reset quiz submission status
        st.session_state.flattened_questions = []  # Reset questions
        st.success("You have been logged out.")
        st.experimental_rerun()  # Refresh the page to reflect the new state

    # Quiz Page
    st.header(f"Welcome {st.session_state.username} to the quiz!")


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
                
                # Save the results to Cloudinary
                save_results_to_cloudinary(st.session_state.username, questions_attempted, correct_answers, wrong_answers, total_score, str(time_taken), str(result_details))
                st.success("Quiz submitted successfully!")
                st.session_state.quiz_submitted = True

                total_marks = 100  # Total marks for the quiz
                percentage = (total_score / total_marks) * 100
                result_message = "<h1 style='color: green;'>Congratulations! You passed the test!</h1>" if percentage >= 70 else "<h1 style='color: red;'>Failed. Please try again later.</h1>"

                # Display results in a card
                st.markdown("<div class='card'><h3>Quiz Results</h3>", unsafe_allow_html=True)
                st.markdown(result_message, unsafe_allow_html=True)
                st.write(f"*Total Questions Attempted:* {questions_attempted}")
                st.write(f"*Correct Answers:* {correct_answers}")
                st.write(f"*Wrong Answers:* {wrong_answers}")
                st.write(f"*Total Score:* {total_score}")
                st.write(f"*Percentage:* {percentage:.2f}%")
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
        st.markdown(f"<div class='question-card'><h4>{current_question['question']}</h4></div>", unsafe_allow_html=True)

        # Display options based on question type
        if current_question["type"] == "multiple_choice":
            st.session_state.answers[st.session_state.current_question] = st.radio("Choose an option:", current_question["options"], key=f"mc_{st.session_state.current_question}")
        elif current_question["type"] == "true_false":
            st.session_state.answers[st.session_state.current_question] = st.radio("Choose an option:", ["True", "False"], key=f"tf_{st.session_state.current_question}")
        elif current_question["type"] == "choose_correct":
            st.session_state.answers[st.session_state.current_question] = st.multiselect("Choose correct options:", current_question["options"], key=f"cc_{st.session_state.current_question}")

# Add a footer
st.markdown("<footer style='text-align: center; margin-top: 20px;'>Quiz Application © 2024</footer>", unsafe_allow_html=True)
