# Python Quiz Game

This game is a command line quiz app for Python. The app should greet the user and ask them to login or create an account with a basic username and password. Passwords should NOT be easily discoverable.

It should take them to a menu, with start quiz, stats, or quit.

It should ask how many questions they want. The quiz will then ask them questions, showing them new questions first, mastered ones less, and cycling through the others. The users performance should be stored, such as questions asked, questions right, questions wrong, questions haven't seen yet, points, questions mastered etc. These stats should be available to the user in the menu. When they are finished with the quiz they are shown their score, questions wrong, right, and then an option to be sent back to the menu.


### QUESTIONS
The questions include:
- The question
- the type (multiple choice, true/false, short answer, fill-in-the-blank)
- the answer
- id, created just in some incrementing order
any question requiring user input should not be case-sensitive, and thus should lowercase answers before checkiing their correctness.

However, stored with user info is diffculty that match with each question id. Any question not in a users "question progress" is inherently new.
- difficulty, including:
    - new: the user hasn't seen this question before
    - still learning: the user done this question once and gotten it wrong or has gotten it wrong after getting it right before
    - learned: the user done this question once and gotten it right
    - mastered: the user has gotten it correct twice in a row

Each question after answering should stay in a screen that either shows them the correct answer or confirms their correct answer with an explanation. If the user doesn't like the question, they have an option to say "this is wrong" and hide it from their questions.

There should be a timer and points. 
| question | time | points |
| -------- | ---- | ------ |
| new | 60 seconds | 1 point |
| learned | 30 seconds | 2 points |
| still learning | 30 seconds | 1 point |
| mastered | 20 seconds | 3 points |

Score history should be stored alongside the username and passwords in a file that is not human-readable.


For now add these five questions as a JSON:
```bash
{
  "questions": [
    {
      "question": "What keyword is used to define a function in Python?",
      "type": "multChoice",
      "options": ["func", "define", "def", "function"],
      "answer": "def",
      "explanation": "def is used at the beginning of functions right before naming them."
      "id": 1
    },
    {
      "question": "A list in Python is immutable.",
      "type": "trueFalse",
      "answer": "false",
      "explanation": "lists are able to be changed"
      "id": 2
    },
    {
      "question": "What built-in function returns the number of items in a list?",
      "type": "shortAnswer",
      "answer": "len",
      "explanation": "len is short for length, and returns the length of the list or the number of items"
      "id": 3
    },
    {
      "question": "A number shown as a decimal in python is called a ___",
      "type": "fillInTheBlank",
      "answer": "float",
      "explanation": "float is short for 'floating point number'"
      "id": 4
    },
    {
      "question": "x = [1, 2, 3]; print(x[-1])",
      "type": "multChoice",
      "answer": ["1", "2", "3", "None of the above"],
      "explanation": "[-1] will index a list to the last item"
      "id": 5
    }
  ]
}
```

### FILES
There should be:
- questions.json: a file for the questions
- users.json: a file for usernames, passwords, a question map to diffculty, and other stats
- quiz.py: a file for the actual quiz

### ERROR HANDLING
If the user starts quiz but the json is empty, the app should instead say "no questions found, please try again later"

If the user requests more questions than are in the bank, the app should send back saying "too many questions, there must be {number of questions - hidden questions} or less" 

If the user puts in the wrong password, it should say wrong password. If the user puts in a username that doesn't exist however, it should say wrong username, which takes priority over saying if the password is correct or not. When creating an account, if they enter in a username that already exists, it should show them "username already exists".

If a user deletes a question, it should try to pull another one from the question bank. If there are no more to pull, it can repeat a couple questions, prioritizing still learning, new, learned, and then mastered.

If a blank answer is submitted for a short answer or fill in the blank, it should just be marked wrong.

If a user has hidden all the questions and doesn't have any more questions to start a quiz with, the app sends an friendly error as well.

### ACCEPTANCE CRITERIA

**Login**
- User can't log in with wrong password and receives error
- User can't create an account with existing username and recieves error
- User can't log in with a nonexistent username and recieves error
- User can't leave fields blank and recieves an answer
- Passwords are hashed an non-readable by a human
- Given a new account or successful login, user is taken to a menu

**Menu**
- When choosing the option to quit, the app successfully quits.
- If the user chooses an option that doesn't exist they will be prompted to try again

**Quiz**
- When starting a quiz, they are prompted with how many questions
- If they choose an amount greater or less than they can, they recieve an error and are prompted to try again
- If users or questions is unreadable, the app gives them the error, and puts them back on the menu screen
- If there is an incomplete question, it is skipped

**Order and Difficulty**
- New questions are shown before others
- If no new questions remain, they will be given still learning or learned
- If no learning or still learned remain, they will be given mastered.
- Questions are random, and not simply given in the same order as their ids.
- Given the parameters listed above, questions correctly change difficulty for the user
- If the timer runs out, the question is marked incorrect
- An answer screen is shown after every question whether correct, incorrect, or timed out. But it should inform the user if they got it correct or not.

**Flagging Questions**
- Flagged questions can be hidden from the user for the future
- Flagging a questions prompts an "are you sure?" screen that informs what is about to happen.
- If the user flags the only question in the session, they return to the menu with "no questions remaining"

**Stats**
- a users stats include:
Total questions answered
Total correct answers
Total incorrect answers
Total questions not yet seen
Total questions mastered
Total points earned
Score history per session (date, questions answered, points earned)

**Storage**
- The app creates a users.json if missing on launch