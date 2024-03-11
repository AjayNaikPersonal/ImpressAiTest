from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST

def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question["question_text"])
        options = next_question["options"]
        for option in options:
            bot_responses.append(option)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''
    # Check if the current question ID is valid
    if current_question_id is None or current_question_id < 0 or current_question_id >= len(PYTHON_QUESTION_LIST):
        return False, "Invalid current question ID"

    # Retrieve the current question from the question list
    current_question = PYTHON_QUESTION_LIST[current_question_id]

    # Validate the user's answer
    if answer not in current_question["options"]:
        return False, "Invalid answer"

    # Store the user's answer in the session
    session["answers"] = session.get("answers", {})
    session["answers"][current_question_id] = answer
    session.modified = True  # Save the session changes

    return True, ""  # Success


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    # Increment the current question ID to get the next question
    next_question_id = current_question_id + 1

    # Check if the next question ID is valid
    if next_question_id >= len(PYTHON_QUESTION_LIST):
        return None, None  # End of questions

    # Retrieve the next question from the question list
    next_question = PYTHON_QUESTION_LIST[next_question_id]

    return next_question, next_question_id


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    # Calculate score based on user's answers stored in session
    user_answers = session.get("answers", {})
    correct_answers = 0
    total_questions = len(PYTHON_QUESTION_LIST)

    for question_id, user_answer in user_answers.items():
        correct_answer = PYTHON_QUESTION_LIST[question_id]["answer"]
        if user_answer == correct_answer:
            correct_answers += 1

    # Generate final response message
    score_percentage = (correct_answers / total_questions) * 100
    final_response = f"You answered {correct_answers} out of {total_questions} questions correctly. Your score: {score_percentage}%"
    
    return final_response
