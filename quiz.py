#!/usr/bin/env python3
import json
import os
import hashlib
import time
import random
import select
import sys
from datetime import datetime

# File paths
QUESTIONS_FILE = "questions.json"
USERS_FILE = "users.json"

# Difficulty levels
DIFFICULTY_NEW = "new"
DIFFICULTY_STILL_LEARNING = "still learning"
DIFFICULTY_LEARNED = "learned"
DIFFICULTY_MASTERED = "mastered"


class QuizApp:
    def __init__(self):
        self.current_user = None
        self.users_data = self._load_users()
        self.questions_data = self._load_questions()

    def _load_users(self):
        """Load users from JSON file, create if doesn't exist."""
        if not os.path.exists(USERS_FILE):
            with open(USERS_FILE, "w") as f:
                json.dump({"users": []}, f)
            return {"users": []}
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading users file: {e}")
            return {"users": []}

    def _load_questions(self):
        """Load questions from JSON file."""
        try:
            with open(QUESTIONS_FILE, "r") as f:
                data = json.load(f)
                # Validate and filter questions
                valid_questions = []
                for q in data.get("questions", []):
                    if self._is_valid_question(q):
                        valid_questions.append(q)
                    else:
                        print(f"Warning: Skipping invalid question (missing required fields): {q.get('id', 'unknown id')}")
                return {"questions": valid_questions}
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading questions file: {e}")
            return {"questions": []}

    def _is_valid_question(self, question):
        """Check if a question has all required fields."""
        required_fields = ["question", "type", "answer", "id", "explanation"]
        if not all(field in question for field in required_fields):
            return False
        if question["type"] not in ["multChoice", "trueFalse", "shortAnswer", "fillInTheBlank"]:
            return False
        if question["type"] == "multChoice" and "options" not in question:
            return False
        return True

    def _save_users(self):
        """Save users data to JSON file."""
        try:
            with open(USERS_FILE, "w") as f:
                json.dump(self.users_data, f, indent=2)
        except IOError as e:
            print(f"Error saving users file: {e}")

    def _hash_password(self, password):
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def _find_user(self, username):
        """Find user by username."""
        for user in self.users_data["users"]:
            if user["username"] == username:
                return user
        return None

    def _initialize_user_progress(self):
        """Initialize question progress for a new user."""
        progress = {}
        for q in self.questions_data.get("questions", []):
            progress[str(q["id"])] = DIFFICULTY_NEW
        return progress

    def clear_screen(self):
        """Clear the console screen."""
        os.system("clear" if os.name == "posix" else "cls")

    def _timed_input(self, prompt, timeout):
        """Get input with a timeout."""
        print(prompt, end='', flush=True)
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if ready:
            return sys.stdin.readline().strip()
        else:
            return None

    def run(self):
        """Main application loop."""
        self.clear_screen()
        print("=" * 50)
        print("          WELCOME TO PYTHON QUIZ")
        print("=" * 50)
        print()
        
        while True:
            if self.current_user is None:
                self._login_menu()
            else:
                self._main_menu()

    def _login_menu(self):
        """Handle login and registration."""
        print("\n1. Login")
        print("2. Create Account")
        print("3. Quit")
        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            self._login()
        elif choice == "2":
            self._create_account()
        elif choice == "3":
            print("\nGoodbye!")
            exit()
        else:
            self.clear_screen()
            print("Invalid option. Please try again.")

    def _login(self):
        """Handle user login."""
        self.clear_screen()
        print("\n--- LOGIN ---")
        username = input("Username: ").strip()
        
        if not username:
            self.clear_screen()
            print("Username cannot be blank.")
            return
        
        user = self._find_user(username)
        if user is None:
            self.clear_screen()
            print("Wrong username.")
            return
        
        password = input("Password: ").strip()
        if not password:
            self.clear_screen()
            print("Password cannot be blank.")
            return
        
        if self._hash_password(password) != user["password_hash"]:
            self.clear_screen()
            print("Wrong password.")
            return
        
        self.current_user = user
        self.clear_screen()
        print(f"Welcome, {username}!")

    def _create_account(self):
        """Handle account creation."""
        self.clear_screen()
        print("\n--- CREATE ACCOUNT ---")
        username = input("Username: ").strip()
        
        if not username:
            self.clear_screen()
            print("Username cannot be blank.")
            return
        
        if self._find_user(username) is not None:
            self.clear_screen()
            print("Username already exists.")
            return
        
        password = input("Password: ").strip()
        if not password:
            self.clear_screen()
            print("Password cannot be blank.")
            return
        
        new_user = {
            "username": username,
            "password_hash": self._hash_password(password),
            "question_progress": self._initialize_user_progress(),
            "stats": {
                "total_answered": 0,
                "total_correct": 0,
                "total_incorrect": 0,
                "total_not_seen": len(self.questions_data.get("questions", [])),
                "total_mastered": 0,
                "total_points": 0,
                "score_history": []
            },
            "hidden_questions": []
        }
        
        self.users_data["users"].append(new_user)
        self._save_users()
        self.current_user = new_user
        self.clear_screen()
        print(f"Account created successfully, {username}!")

    def _main_menu(self):
        """Display main menu after login."""
        print("\n--- MAIN MENU ---")
        print("1. Start Quiz")
        print("2. Stats")
        print("3. Quit")
        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            self._start_quiz()
        elif choice == "2":
            self._show_stats()
        elif choice == "3":
            self.clear_screen()
            print(f"Goodbye, {self.current_user['username']}!")
            self.current_user = None
            return
        else:
            self.clear_screen()
            print("Invalid option. Please try again.")

    def _show_stats(self):
        """Display user statistics."""
        self.clear_screen()
        stats = self.current_user["stats"]
        print("\n--- YOUR STATS ---")
        print(f"Total Questions Answered: {stats['total_answered']}")
        print(f"Total Correct: {stats['total_correct']}")
        print(f"Total Incorrect: {stats['total_incorrect']}")
        print(f"Total Not Yet Seen: {stats['total_not_seen']}")
        print(f"Total Mastered: {stats['total_mastered']}")
        print(f"Total Points Earned: {stats['total_points']}")
        
        if stats["score_history"]:
            print("\n--- SCORE HISTORY ---")
            for i, session in enumerate(stats["score_history"], 1):
                print(f"Session {i} ({session['date']}): {session['questions_answered']} questions, {session['points_earned']} points")
        
        input("\nPress Enter to return to menu...")
        self.clear_screen()

    def _start_quiz(self):
        """Start a new quiz."""
        self.clear_screen()
        
        # Check if questions file is readable
        try:
            with open(QUESTIONS_FILE, "r") as f:
                json.load(f)
        except (json.JSONDecodeError, IOError):
            print("Error reading questions file. Please try again later.")
            input("Press Enter to return to menu...")
            self.clear_screen()
            return
        
        questions = self.questions_data.get("questions", [])
        available_questions = [q for q in questions if q["id"] not in self.current_user["hidden_questions"]]
        
        if len(questions) == 0:
            self.clear_screen()
            print("no questions found, please try again later.")
            input("Press Enter to return to menu...")
            self.clear_screen()
            return
        elif not available_questions:
            self.clear_screen()
            print("No questions available. All questions have been hidden.")
            input("Press Enter to return to menu...")
            self.clear_screen()
            return
        
        print("--- START QUIZ ---")
        while True:
            try:
                num_questions = int(input(f"How many questions? (1-{len(available_questions)}): ").strip())
                if num_questions <= 0 or num_questions > len(available_questions):
                    self.clear_screen()
                    max_allowed = len(available_questions)
                    print(f"Too many questions, there must be {max_allowed} or less")
                    print("--- START QUIZ ---")
                    continue
                break
            except ValueError:
                self.clear_screen()
                print("Please enter a valid number.")
                print("--- START QUIZ ---")
                continue
        
        self._run_quiz(available_questions, num_questions)

    def _get_question_difficulty(self, question_id):
        """Get the difficulty level of a question for the current user."""
        return self.current_user["question_progress"].get(str(question_id), DIFFICULTY_NEW)

    def _get_question_config(self, difficulty):
        """Get time limit and points for a question difficulty."""
        config = {
            DIFFICULTY_NEW: {"time": 60, "points": 1},
            DIFFICULTY_STILL_LEARNING: {"time": 30, "points": 1},
            DIFFICULTY_LEARNED: {"time": 30, "points": 2},
            DIFFICULTY_MASTERED: {"time": 20, "points": 3}
        }
        return config.get(difficulty, {"time": 60, "points": 1})

    def _select_next_question(self, available_questions, asked_ids):
        """Select next question based on difficulty priority."""
        remaining = [q for q in available_questions if q["id"] not in asked_ids and q["id"] not in self.current_user["hidden_questions"]]
        
        if not remaining:
            return None
        
        # Prioritize by difficulty: new > still learning > learned > mastered
        new_qs = [q for q in remaining if self._get_question_difficulty(q["id"]) == DIFFICULTY_NEW]
        if new_qs:
            return random.choice(new_qs)
        
        learning_qs = [q for q in remaining if self._get_question_difficulty(q["id"]) == DIFFICULTY_STILL_LEARNING]
        if learning_qs:
            return random.choice(learning_qs)
        
        learned_qs = [q for q in remaining if self._get_question_difficulty(q["id"]) == DIFFICULTY_LEARNED]
        if learned_qs:
            return random.choice(learned_qs)
        
        mastered_qs = [q for q in remaining if self._get_question_difficulty(q["id"]) == DIFFICULTY_MASTERED]
        if mastered_qs:
            return random.choice(mastered_qs)
        
        return None

    def _run_quiz(self, available_questions, num_questions):
        """Run the quiz session."""
        session_correct = 0
        session_incorrect = 0
        session_points = 0
        asked_ids = []
        
        for i in range(num_questions):
            question = self._select_next_question(available_questions, asked_ids)
            
            if question is None:
                # All questions asked, repeat if needed
                if asked_ids:
                    asked_ids = []  # Reset to allow repeating
                    question = self._select_next_question(available_questions, asked_ids)
                else:
                    break
            
            if question is None:
                break
            
            asked_ids.append(question["id"])
            difficulty = self._get_question_difficulty(question["id"])
            config = self._get_question_config(difficulty)
            
            self.clear_screen()
            print(f"\n--- QUESTION {i+1}/{num_questions} ---")
            print(f"Difficulty: {difficulty.upper()}")
            print(f"Time: {config['time']}s | Points: {config['points']}")
            print()
            
            is_correct, timed_out, count = self._ask_question(question, config["time"])
            
            # Update user progress
            if count:
                if is_correct:
                    session_correct += 1
                    session_points += config["points"]
                    
                    # Update difficulty
                    if difficulty == DIFFICULTY_NEW:
                        self.current_user["question_progress"][str(question["id"])] = DIFFICULTY_LEARNED
                    elif difficulty == DIFFICULTY_STILL_LEARNING:
                        self.current_user["question_progress"][str(question["id"])] = DIFFICULTY_LEARNED
                    elif difficulty == DIFFICULTY_LEARNED:
                        self.current_user["question_progress"][str(question["id"])] = DIFFICULTY_MASTERED
                else:
                    session_incorrect += 1
                    
                    # Update difficulty
                    if difficulty == DIFFICULTY_MASTERED:
                        self.current_user["question_progress"][str(question["id"])] = DIFFICULTY_STILL_LEARNING
                    elif difficulty == DIFFICULTY_LEARNED:
                        self.current_user["question_progress"][str(question["id"])] = DIFFICULTY_STILL_LEARNING
                    elif difficulty == DIFFICULTY_NEW:
                        self.current_user["question_progress"][str(question["id"])] = DIFFICULTY_STILL_LEARNING
        
        if session_correct + session_incorrect > 0:
            # Update overall stats
            self.current_user["stats"]["total_answered"] += session_correct + session_incorrect
            self.current_user["stats"]["total_correct"] += session_correct
            self.current_user["stats"]["total_incorrect"] += session_incorrect
            self.current_user["stats"]["total_points"] += session_points
            
            # Calculate not seen
            not_seen = sum(1 for q in available_questions 
                          if self._get_question_difficulty(q["id"]) == DIFFICULTY_NEW)
            self.current_user["stats"]["total_not_seen"] = not_seen
            
            # Calculate mastered
            mastered = sum(1 for q in available_questions 
                          if self._get_question_difficulty(q["id"]) == DIFFICULTY_MASTERED)
            self.current_user["stats"]["total_mastered"] = mastered
            
            # Add to score history
            self.current_user["stats"]["score_history"].append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "questions_answered": session_correct + session_incorrect,
                "points_earned": session_points
            })
            
            self._save_users()
            
            # Show results
            self._show_quiz_results(session_correct, session_incorrect, session_points, num_questions)
        else:
            self.clear_screen()
            print("No questions remaining.")
            input("Press Enter to return to menu...")
            self.clear_screen()

    def _ask_question(self, question, time_limit):
        """Ask a question and return whether it was answered correctly."""
        print(f"Q: {question['question']}")
        
        if question["type"] == "multChoice":
            self.clear_screen()
            print(f"Q: {question['question']}")
            options = question["options"]
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")
            
            start_time = time.time()
            while True:
                elapsed = time.time() - start_time
                remaining_time = max(0, time_limit - elapsed)
                answer = self._timed_input(f"\nYour answer (1-{len(options)}): ", remaining_time)
                if answer is None:
                    timed_out = True
                    is_correct = False
                    break
                try:
                    answer_idx = int(answer) - 1
                    if 0 <= answer_idx < len(options):
                        user_answer = options[answer_idx]
                        is_correct = user_answer.lower() == question["answer"].lower()
                        timed_out = False
                        break
                    else:
                        print(f"Invalid choice. Please enter a number between 1 and {len(options)}.")
                except ValueError:
                    print(f"Invalid input. Please enter a number between 1 and {len(options)}.")
        
        elif question["type"] == "trueFalse":
            self.clear_screen()
            print(f"Q: {question['question']}")
            print("1. True")
            print("2. False")
            
            start_time = time.time()
            while True:
                elapsed = time.time() - start_time
                remaining_time = max(0, time_limit - elapsed)
                answer = self._timed_input("\nYour answer (1-2): ", remaining_time)
                if answer is None:
                    timed_out = True
                    is_correct = False
                    break
                if answer == "1":
                    user_answer = "true"
                    is_correct = user_answer == question["answer"].lower()
                    timed_out = False
                    break
                elif answer == "2":
                    user_answer = "false"
                    is_correct = user_answer == question["answer"].lower()
                    timed_out = False
                    break
                else:
                    print("Invalid choice. Please enter 1 for True or 2 for False.")
        
        elif question["type"] == "shortAnswer":
            answer = self._timed_input("\nYour answer: ", time_limit)
            if answer is None:
                timed_out = True
                is_correct = False
            else:
                timed_out = False
                if not answer:
                    is_correct = False
                else:
                    is_correct = answer.lower() == question["answer"].lower()
        
        elif question["type"] == "fillInTheBlank":
            answer = self._timed_input("\nYour answer: ", time_limit)
            if answer is None:
                timed_out = True
                is_correct = False
            else:
                timed_out = False
                if not answer:
                    is_correct = False
                else:
                    is_correct = answer.lower() == question["answer"].lower()
        
        else:
            timed_out = False
            is_correct = False
        
        # Show answer screen
        action = self._show_answer_screen(question, is_correct, timed_out)
        count_this_question = action != 'flag'
        
        return is_correct, timed_out, count_this_question

    def _show_answer_screen(self, question, is_correct, timed_out=False):
        """Show the answer screen after a question."""
        self.clear_screen()
        
        if timed_out:
            print("⏰ TIME'S UP!")
        elif is_correct:
            print("✓ CORRECT!")
        else:
            print("✗ INCORRECT")
        
        print(f"\nCorrect Answer: {question['answer']}")
        print(f"Explanation: {question['explanation']}")
        
        print("\n1. Continue")
        print("2. Flag this question")
        
        choice = input("\nSelect an option: ").strip()
        
        if choice == "2":
            self._flag_question(question["id"])
            return 'flag'
        else:
            return 'continue'

    def _flag_question(self, question_id):
        """Flag/hide a question."""
        self.clear_screen()
        print("\n--- FLAG QUESTION ---")
        print("This question will be hidden from future quizzes.")
        choice = input("Are you sure? (yes/no): ").strip().lower()
        
        if choice in ["yes", "y"]:
            if question_id not in self.current_user["hidden_questions"]:
                self.current_user["hidden_questions"].append(question_id)
                self._save_users()
            self.clear_screen()
            print("Question flagged and hidden.")
        else:
            self.clear_screen()

    def _show_quiz_results(self, correct, incorrect, points, total):
        """Show quiz results."""
        self.clear_screen()
        print("\n--- QUIZ COMPLETE ---")
        print(f"Questions Answered: {correct + incorrect}")
        print(f"Correct: {correct}")
        print(f"Incorrect: {incorrect}")
        print(f"Points Earned: {points}")
        
        print("\n1. Back to Menu")
        choice = input("\nSelect an option: ").strip()
        
        self.clear_screen()


def main():
    app = QuizApp()
    app.run()


if __name__ == "__main__":
    main()
