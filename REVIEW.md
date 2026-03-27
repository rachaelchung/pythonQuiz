I'll review the project's code against the specification. Let me start by reading both the spec and the implementation files.   

Read [](file:///Users/rachaelchung/Documents/GitHub/pythonQuiz/SPEC.md)

Read [](file:///Users/rachaelchung/Documents/GitHub/pythonQuiz/quiz.py#1-1), lines 1 to 300

Read [](file:///Users/rachaelchung/Documents/GitHub/pythonQuiz/test_app.py)

Read [](file:///Users/rachaelchung/Documents/GitHub/pythonQuiz/quiz.py#300-300), lines 300 to 500

Read [](file:///Users/rachaelchung/Documents/GitHub/pythonQuiz/quiz.py#500-500), lines 500 to 502

Read [](file:///Users/rachaelchung/Documents/GitHub/pythonQuiz/questions.json)

Let me also check the README to understand the project better: 

Read [](file:///Users/rachaelchung/Documents/GitHub/pythonQuiz/README.md)

Now I'll compile a comprehensive review of the code against the specification. Here are my findings:

## Code Review: Python Quiz App

### 1. [FAIL] Timer Not Implemented
quiz.py passes `time_limit` to `_ask_question()`, but the timer is never enforced. The method signature at quiz.py accepts the parameter but ignores it completely. The function always returns `timed_out=False` at quiz.py. Users get unlimited time regardless of difficulty level, violating the spec's time-based points table.

### 2. [FAIL] Difficulty Progression Broken for "Still Learning" State
quiz.py has incomplete difficulty update logic. When a user correctly answers a "still learning" question, there is no case to progress it to "learned"—it stays "still learning" instead. The spec defines: "learned = user done this question once and gotten it right," but "still learning + correct" produces no state change. Only "new + correct" and "learned + correct" are handled.

### 3. [FAIL] Flagged Questions Can Be Asked Again in Same Session
quiz.py calculates `available_questions` once before the quiz loop. When a user flags a question at quiz.py, `hidden_questions` is updated but the `available_questions` list is never refreshed. The next quiz iteration can re-select the same flagged question. This violates the flagging requirement.

### 4. [FAIL] No Validation for Incomplete/Malformed Questions
quiz.py accesses question fields without checking if they exist (e.g., `question["type"]`, `question["answer"]`, `question["options"]`). If a question in questions.json is missing required fields, the app crashes with `KeyError`. The spec lists required fields but there's no validation.

### 5. [FAIL] Flagging Last Question in Session Should Return to Menu
quiz.py handles flagging but doesn't detect if it was the quiz's last question. The spec states: "If the user flags the only question in the session, they return to the menu with 'no questions remaining'." Currently, the loop would continue and error trying to select another question, or repeat a flagged one.

### 6. [WARN] Users.json Not Created on Application Startup
The spec says: "The app creates a users.json if missing on launch." Currently, quiz.py only returns an empty dict if the file doesn't exist but doesn't create it. The file is only created on the first `_save_users()` call quiz.py. A more robust approach would create it during initialization.

### 7. [WARN] No User Feedback for Invalid Multiple Choice/True-False Answers
When users enter invalid input for multiple choice or true/false questions (quiz.py), the answer is silently marked wrong with no error message or guidance (e.g., "Please enter 1-4"). This creates poor UX—users won't know why they got it wrong.

### 8. [WARN] Unclear Error Message When No Questions Available
quiz.py shows: "No questions available. All questions have been hidden." This doesn't distinguish between two scenarios: (1) no questions exist in the question bank at all, or (2) all existing questions were hidden. The spec says: "If the user starts quiz but the json is empty, the app should instead say 'no questions found, please try again later.'"

### 9. [WARN] Inefficient Screen Rendering for Multiple Choice and True/False
In `_ask_question()`, multiple choice and true/false options are printed before `clear_screen()` at quiz.py, then printed again after clearing. This is wasteful and confusing to users who see the options appear twice.

### 10. [CODE QUALITY] Magic String Duplication for Difficulty Levels
Difficulty strings ("new", "still learning", "learned", "mastered") are repeated throughout the code. Consider using an Enum or constants for maintainability.

### 11. [PASS] Login Validation - Wrong Password
quiz.py correctly rejects wrong passwords with error message "Wrong password."

### 12. [PASS] Login Validation - Nonexistent Username
quiz.py correctly prioritizes username check before password, showing "Wrong username."

### 13. [PASS] Login Validation - Existing Username on Account Creation
quiz.py correctly rejects duplicate usernames with "Username already exists."

### 14. [PASS] Blank Field Validation
[quiz.py](quiz.py#L82-L84, L98-L100, L111-L113) validates blank inputs for username and password during login and account creation.

### 15. [PASS] Password Hashing
quiz.py uses SHA-256 hashing. Passwords stored as 64-character hex strings are not human-readable. Test file confirms this.

### 16. [PASS] Question Selection Priority
quiz.py correctly prioritizes: new → still learning → learned → mastered. Uses `random.choice()` for randomization within each category.

### 17. [PASS] Case-Insensitive Answers
All user-input question types convert to lowercase before comparison:
- Short answer quiz.py
- Fill in the blank quiz.py
- Multiple choice quiz.py
- True/false quiz.py

### 18. [PASS] Answer Confirmation Screen
quiz.py shows correct answer and explanation after each question, with correct/incorrect indicator.

### 19. [PASS] Blank Short Answer/Fill-in-the-Blank Handling
[quiz.py](quiz.py#L430-L431, L436-L437) marks blank answers as incorrect as specified.

### 20. [PASS] Menu Navigation and Quit
quiz.py correctly handles quit option and invalid menu choices with retry prompts.

### 21. [PASS] Stats Collection
quiz.py correctly stores all required stats: total answered, correct, incorrect, not seen, mastered, points, and score history with date/timestamp.

### 22. [PASS] Excessive Questions Error Message
quiz.py correctly shows: `"Too many questions, there must be {max_allowed} or less"` with proper count of available (non-hidden) questions.

### 23. [PASS] JSON File Error Handling
quiz.py gracefully handles unreadable questions.json with error message and returns to menu.

---

**Summary:**  
- **5 Critical Failures** (timer, difficulty progression, flagged question reuse, malformed question validation, flag-last-question handling)
- **4 Warnings** (users.json creation timing, user feedback on invalid answers, error messages, inefficient rendering)  
- **14 Items Pass** specification requirements

The app is **partially functional** but has critical flaws that violate core spec requirements, particularly around timing mechanics and question difficulty progression.