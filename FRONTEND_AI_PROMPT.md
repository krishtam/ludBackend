# Frontend AI Prompt: Ludora Educational Platform (Flutter)

## 1. Project Overview

You are an AI specializing in Flutter frontend development. Your task is to generate the Flutter code for a barebones but functionally complete mobile application frontend for the Ludora educational platform. The backend is a FastAPI application providing various educational and gamified features. This document outlines the screens, functionalities, UI elements, and API interactions required.

The goal is to create a functional user interface that allows users to interact with all key features of the Ludora backend. Focus on clear, intuitive design and correct API integration.

## 2. General Frontend Requirements

*   **State Management:** Use Provider or Riverpod for state management. Clearly separate UI, business logic, and state.
*   **API Client:** Create a dedicated API client service (e.g., using `http` or `dio`) to handle all backend communication. This service should manage base URLs, headers (including Authorization for authenticated requests), and error handling for API calls.
*   **Authentication:**
    *   Implement secure storage for authentication tokens (access and refresh tokens).
    *   Include logic to refresh access tokens using the refresh token when necessary.
    *   Redirect to login screen if unauthenticated or token refresh fails.
*   **Navigation:** Use Flutter's Navigator 2.0 (e.g., using `go_router` or a similar declarative routing package) for clear and manageable navigation.
*   **Error Handling:** Implement user-friendly error display (e.g., SnackBars, Dialogs) for API errors or other issues.
*   **Loading States:** Show loading indicators (e.g., `CircularProgressIndicator`) during data fetching or processing.
*   **Responsiveness (Basic):** While not the primary focus for this barebones version, ensure layouts are reasonably adaptable to common phone screen sizes.
*   **Modularity:** Structure the code into logical modules/features (e.g., auth, profile, shop, quizzes).
*   **Styling:** Use a simple, clean Material Design theme. No complex custom styling is required for this phase. Focus on functionality.

## 3. Detailed Screen/Feature Breakdown

### 3.1. Authentication Screens

#### 3.1.1. Signup Screen
*   **Purpose/User Stories:**
    *   As a new user, I want to create an account so I can access the platform.
*   **UI Layout Sketch (Text-based):**
    ```
    [App Logo/Title]
    Username Text Field
    Email Text Field
    Password Text Field
    Confirm Password Text Field (Client-side validation)
    Signup Button
    Link: "Already have an account? Login"
    ```
*   **Data Displayed:** Input fields for user registration.
*   **User Interactions:**
    *   Enter username, email, password, confirm password.
    *   Tap "Signup" button.
    *   Tap "Login" link to navigate to Login Screen.
*   **API Calls:**
    *   **Trigger:** Tap "Signup" button.
    *   **Endpoint:** `POST /api/v1/auth/signup`
    *   **Request Payload Example:**
        ```json
        {
          "username": "newuser",
          "email": "newuser@example.com",
          "password": "password123"
        }
        ```
    *   **Response Handling:**
        *   **Success (200):** Display success message (e.g., "Account created! Please login."), navigate to Login Screen.
        *   **Error (400 - Duplicate, Validation):** Display error message from backend (e.g., "Username already registered").
*   **Local State:** Form input values, loading state, error messages.

#### 3.1.2. Login Screen
*   **Purpose/User Stories:**
    *   As an existing user, I want to log in to access my account and platform features.
*   **UI Layout Sketch (Text-based):**
    ```
    [App Logo/Title]
    Username Text Field (can be username or email)
    Password Text Field
    Login Button
    Link: "Don't have an account? Signup"
    ```
*   **Data Displayed:** Input fields for login.
*   **User Interactions:**
    *   Enter username/email and password.
    *   Tap "Login" button.
    *   Tap "Signup" link to navigate to Signup Screen.
*   **API Calls:**
    *   **Trigger:** Tap "Login" button.
    *   **Endpoint:** `POST /api/v1/auth/token`
    *   **Request Payload Example (Form Data):**
        ```
        username=testuser
        password=testpassword
        ```
    *   **Response Handling:**
        *   **Success (200):** Store access and refresh tokens securely. Navigate to Main Dashboard.
        *   **Error (401 - Incorrect credentials):** Display error message (e.g., "Incorrect username or password").
*   **Local State:** Form input values, loading state, error messages.

### 3.2. Main Dashboard Screen
*   **Purpose/User Stories:**
    *   As a logged-in user, I want to see an overview of available features and quick links.
*   **UI Layout Sketch (Text-based):**
    ```
    AppBar: "Ludora Dashboard"
    Body:
      Welcome Message (e.g., "Welcome, [Username]!")
      Grid or List of Navigation Cards/Buttons:
        - "My Profile"
        - "Shop"
        - "My Inventory"
        - "Browse Topics"
        - "Start Quiz" (generic or leads to quiz setup)
        - "Play Minigames" (leads to minigame list)
        - "Leaderboards"
        - "My Quests"
        - "AI Tools" (grouping for Paraphrase, Word Problem, Guide)
        - "Logout" Button
    ```
*   **Data Displayed:** User's username (fetched from profile or token). Quick navigation links.
*   **User Interactions:** Tap on navigation items to go to respective screens. Tap "Logout" to clear tokens and navigate to Login.
*   **API Calls:** None directly from this screen, but it's the entry point after login. Profile data might be pre-fetched.
*   **Local State:** Minimal, mainly for displaying username.

### 3.3. User Profile Screen
*   **Purpose/User Stories:**
    *   As a user, I want to view my profile information.
    *   As a user, I want to update my profile information.
*   **UI Layout Sketch (Text-based):**
    ```
    AppBar: "My Profile"
    Body:
      Avatar Display (placeholder if URL is null)
      Username: [Username_Display]
      Email: [Email_Display]
      First Name: [Text Field for First Name]
      Last Name: [Text Field for Last Name]
      Bio: [Text Area for Bio]
      Current Streak: [Streak_Value]
      Max Streak: [Max_Streak_Value]
      In-App Currency: [Currency_Value]
      Update Profile Button
    ```
*   **Data Displayed:** User's profile data (username, email, first/last name, bio, avatar, streak, currency).
*   **User Interactions:**
    *   Edit first name, last name, bio fields.
    *   Tap "Update Profile" button.
*   **API Calls:**
    *   **On Load:**
        *   **Endpoint:** `GET /api/v1/users/me/profile`
        *   **Response Handling:** Populate UI with fetched data.
    *   **On Update:**
        *   **Trigger:** Tap "Update Profile" button.
        *   **Endpoint:** `PUT /api/v1/users/me/profile`
        *   **Request Payload Example:**
            ```json
            {
              "first_name": "John",
              "last_name": "Doe",
              "bio": "Loves learning!",
              "avatar_url": "http://example.com/avatar.png" // Optional
            }
            ```
        *   **Response Handling:** Display success/error message. Refresh profile data.
*   **Local State:** Profile data, form input values for editing, loading/error states.

### 3.4. Shop Screens

#### 3.4.1. Shop - Item Listing Screen
*   **Purpose/User Stories:**
    *   As a user, I want to browse available items in the shop.
*   **UI Layout Sketch (Text-based):**
    ```
    AppBar: "Shop"
    Body:
      Scrollable List/Grid of Shop Items:
        Each Item Card:
          Item Name
          Item Description (brief)
          Item Price (in-app currency)
          Item Type
          (Optional: Item Image/Icon)
      Pagination Controls (Next/Previous Page, Page Number)
    ```
*   **Data Displayed:** List of shop items with name, description, price, type.
*   **User Interactions:**
    *   Scroll through items.
    *   Tap on an item to view details (Not explicitly requested for this barebones version, but good to note. For now, purchase can be directly from list or a simplified detail view).
    *   Interact with pagination controls.
*   **API Calls:**
    *   **On Load/Pagination:**
        *   **Endpoint:** `GET /api/v1/shop/items`
        *   **Query Parameters:** `skip`, `limit`
        *   **Response Handling:** Display items. Update pagination state (`total`, `page`, `size`).
*   **Local State:** List of items, loading/error states, current page, total items.

#### 3.4.2. Shop - Item Purchase (Simplified - could be a dialog or part of item display)
*   **Purpose/User Stories:**
    *   As a user, I want to purchase an item using my in-app currency.
*   **UI Layout Sketch (Text-based - e.g., shown in a Dialog when an item is tapped):**
    ```
    Dialog Title: "Purchase Item: [Item Name]"
    Item Description: [Full Description]
    Price: [Item Price]
    Quantity: [Number Input Field (default 1)]
    Total Cost: [Calculated Total]
    Confirm Purchase Button
    Cancel Button
    ```
*   **Data Displayed:** Selected item's details, quantity input, total cost.
*   **User Interactions:**
    *   Adjust quantity.
    *   Tap "Confirm Purchase".
    *   Tap "Cancel".
*   **API Calls:**
    *   **Trigger:** Tap "Confirm Purchase".
    *   **Endpoint:** `POST /api/v1/shop/items/{item_id}/purchase`
    *   **Request Payload Example:**
        ```json
        {
          "quantity": 1
        }
        ```
    *   **Response Handling:**
        *   **Success (200):** Display success message (e.g., "Purchase successful!"). Update user's currency display (ideally by re-fetching profile or via state management).
        *   **Error (400 - Not enough currency, 404 - Item not found):** Display error message.
*   **Local State:** Selected item, quantity, loading/error states.

### 3.5. Inventory Screen
*   **Purpose/User Stories:**
    *   As a user, I want to view items I own.
*   **UI Layout Sketch (Text-based):**
    ```
    AppBar: "My Inventory"
    Body:
      Scrollable List of Inventory Items:
        Each Item Card:
          Item Name
          Quantity Owned
          Item Type
          (Optional: Brief Description or "Use" button for consumables/tickets - "Use" functionality is out of scope for now)
    ```
*   **Data Displayed:** List of user's inventory items with name, quantity, type.
*   **User Interactions:** Scroll through items.
*   **API Calls:**
    *   **On Load:**
        *   **Endpoint:** `GET /api/v1/inventory/me`
        *   **Response Handling:** Display inventory items.
*   **Local State:** List of inventory items, loading/error states.

### 3.6. Topic Browser Screen
*   **Purpose/User Stories:**
    *   As a user, I want to browse available learning topics.
*   **UI Layout Sketch (Text-based):**
    ```
    AppBar: "Browse Topics"
    Body:
      Scrollable List of Topics (grouped by Subject):
        Subject Header (e.g., "Elementary Math")
          Topic Card:
            Topic Name (Unit Name)
            Topic Description
            (Button: "Start Quiz on this Topic" or "View Questions")
    ```
*   **Data Displayed:** List of topics, potentially grouped by subject.
*   **User Interactions:**
    *   Select a topic to (conceptually) start a quiz or view related questions/minigames.
*   **API Calls:**
    *   **On Load:**
        *   **Endpoint:** `GET /api/v1/q/topics`
        *   **Response Handling:** Display topics.
*   **Local State:** List of topics, loading/error states.

### 3.7. Question Display Screen (Generic - used by Quizzes/Minigames)
*   **Purpose/User Stories:**
    *   As a user, I want to view a question and submit my answer.
*   **UI Layout Sketch (Text-based):**
    ```
    Question Text Area: [Question Text]
    Answer Input Area:
      (Could be multiple choice options, text field, etc. For barebones, assume a single text field for answer)
      Text Field: "Your Answer"
    Submit Answer Button (or "Next Question" in a quiz)
    (Optional: "Get a Hint" button - interacts with "The Guide")
    ```
*   **Data Displayed:** Question text, answer input field.
*   **User Interactions:** Enter answer, submit.
*   **API Calls:** Depends on context (Quiz or Minigame). Quiz submission is batched. Minigames might submit answer by answer or at the end.
*   **Local State:** Current question, user's current answer.

### 3.8. Quiz Interface Screens

#### 3.8.1. Quiz Generation/Setup Screen (Conceptual - can be simplified)
*   **Purpose:** User selects parameters to generate a quiz.
*   **UI Sketch:**
    ```
    AppBar: "Start a New Quiz"
    Topic Selection (Dropdown/List from GET /api/v1/q/topics)
    Number of Questions (Slider or Text Input, e.g., 5, 10, 20)
    Difficulty (Optional Dropdown: Easy, Medium, Hard - map to 1-5)
    Generate Quiz Button
    ```
*   **API Calls:**
    *   **Trigger:** Tap "Generate Quiz".
    *   **Endpoint:** `POST /api/v1/quizzes/generate`
    *   **Request Payload Example:**
        ```json
        {
          "name": "My Algebra Quiz", // Optional, can be auto-generated
          "num_questions": 10,
          "topic_ids": [1], // From topic selection
          "difficulties": [2] // Optional
        }
        ```
    *   **Response Handling:** On success, receive `QuizRead` data (including questions) and navigate to Quiz Taking Screen.
*   **Local State:** Selected topic, num_questions, difficulty, loading state.

#### 3.8.2. Quiz Taking Screen (Question by Question)
*   **Purpose:** User answers questions in the generated quiz.
*   **UI Sketch:**
    ```
    AppBar: "[Quiz Name] - Question [Current #]/[Total #]"
    Progress Bar
    [Question Display Area (see 3.7)]
      Question Text: ...
      Answer Input Field: ...
    "Next Question" / "Submit Quiz" Button
    (Optional: "Hint" button -> calls Guide API)
    ```
*   **Data Displayed:** Current question from the quiz, progress.
*   **User Interactions:** Enter answer, navigate to next question. Final question leads to submission.
*   **API Calls:** No API call per question. Answers are collected locally.
*   **Local State:** Current quiz data (`QuizRead` object), current question index, list of user's answers.

#### 3.8.3. Quiz Submission & Results Screen
*   **Purpose:** User submits their answers; views results.
*   **UI Sketch:**
    ```
    AppBar: "Quiz Results: [Quiz Name]"
    Body:
      Your Score: [Score]%
      Summary: [Correct Answers] / [Total Questions]
      (Optional: List of questions with user's answer, correct answer, and if they were correct)
      Button: "Back to Dashboard" or "Try Another Quiz"
    ```
*   **Data Displayed:** Score, summary.
*   **User Interactions:** View results, navigate away.
*   **API Calls:**
    *   **Trigger:** Tap "Submit Quiz" on the last question of Quiz Taking Screen.
    *   **Endpoint:** `POST /api/v1/quizzes/{quiz_id}/submit`
    *   **Request Payload Example:**
        ```json
        {
          "answers": [
            {"question_id": 101, "answer": "Paris"},
            {"question_id": 102, "answer": "4"}
          ]
        }
        ```
    *   **Response Handling:** On success, receive updated `QuizRead` data (with score, completion status) and display it.
*   **Local State:** Quiz results data.

### 3.9. Minigame Interface Screen (Generic Placeholder)
*   **Purpose:** User plays a minigame.
*   **UI Sketch:**
    ```
    AppBar: "[Minigame Name]"
    Body:
      Placeholder for Minigame UI.
      (This screen would dynamically load/present the specific minigame.
       For this barebones version, it can be a simple screen that:
       1. Fetches questions using GET /api/v1/minigames/{minigame_id}/questions
       2. Presents them one by one (using Question Display Screen logic).
       3. After X questions, shows a "Submit Score" button.)
      Score Display (if relevant during gameplay)
      Submit Score Button (after session)
    ```
*   **Data Displayed:** Minigame content (e.g., questions), score.
*   **User Interactions:** Play the game, submit final score.
*   **API Calls:**
    *   **On Start (Conceptual):** `GET /api/v1/minigames/{minigame_id}/questions` (if minigame uses questions).
    *   **On End:**
        *   **Endpoint:** `POST /api/v1/minigames/{minigame_id}/progress`
        *   **Request Payload Example:**
            ```json
            {
              "minigame_id": 1, // Should match path param
              "score": 1500,
              "currency_earned": 15,
              "session_duration_seconds": 180
            }
            ```
        *   **Response Handling:** Display success/error. Update user currency.
*   **Local State:** Current minigame state, score, questions (if applicable).

### 3.10. Leaderboards Screen
*   **Purpose:** User views leaderboards.
*   **UI Sketch:**
    ```
    AppBar: "Leaderboards"
    Body:
      Dropdown/Tabs to select Leaderboard (e.g., from GET /api/v1/leaderboards)
      Dropdown/Tabs for Timeframe (Daily, Weekly, All Time)
      Scrollable List of Leaderboard Entries:
        Rank | Username | Score
    ```
*   **Data Displayed:** Selected leaderboard's entries.
*   **User Interactions:** Select leaderboard, select timeframe.
*   **API Calls:**
    *   **On Load (for list of leaderboards):** `GET /api/v1/leaderboards` (can filter by `score_type`, `timeframe`).
    *   **On Select Leaderboard/Timeframe:** `GET /api/v1/leaderboards/{leaderboard_id}/entries`
    *   **Response Handling:** Display entries.
*   **Local State:** List of available leaderboards, selected leaderboard, selected timeframe, entries, loading/error states.

### 3.11. Quest Log & Generation Screen
*   **Purpose:** User views their active quests and can trigger generation of new quests.
*   **UI Sketch:**
    ```
    AppBar: "My Quests"
    Body:
      Button: "Generate New Quests" (if appropriate)
      Scrollable List of Active Quests:
        Quest Card:
          Quest Name
          Quest Description
          Quest Status
          Reward: [Currency Amount]
          Objectives:
            - Objective 1 Description (Progress: X/Y)
            - Objective 2 Description (Progress: A/B)
    ```
*   **Data Displayed:** List of user's quests with details and objectives.
*   **User Interactions:** View quests. Tap "Generate New Quests".
*   **API Calls:**
    *   **On Load:**
        *   **Endpoint:** `GET /api/v1/users/me/quests`
        *   **Response Handling:** Display quests.
    *   **On Button Tap:**
        *   **Trigger:** Tap "Generate New Quests".
        *   **Endpoint:** `POST /api/v1/users/me/quests/generate`
        *   **Response Handling:** Display newly generated quests (or message if none). Refresh quest list.
*   **Local State:** List of quests, loading/error states.

### 3.12. AI Feature Interfaces

#### 3.12.1. Weakness Display Screen (Conceptual - part of Profile or Dashboard)
*   **Purpose:** User views their predicted weaknesses.
*   **UI Sketch (Could be a section in Profile or a dedicated page):**
    ```
    Section Title: "Areas to Improve"
    List of Predicted Weaknesses:
      Topic: [Topic Name]
      (Optional: Probability: [Value]%, Suggested Action: [Text based on level])
      Button: "Practice this Topic" (links to relevant content/quiz)
    ```
*   **Data Displayed:** List of topics the AI predicts as weaknesses.
*   **API Calls (Data Source):**
    *   **Endpoint:** `POST /api/v1/ai/predict-weakness` (This endpoint expects features; frontend needs to prepare these based on user data available locally or fetched from other profile/progress endpoints. For barebones, this might be simplified or triggered by a button).
    *   **Request Payload Example (Frontend would construct this):**
        ```json
        {
          "average_score_per_topic": {"topic_A_id": 0.55, "topic_B_id": 0.60},
          "recent_quiz_scores": [0.5, 0.55, 0.4],
          "time_spent_per_topic_minutes": {"topic_A_id": 120, "topic_B_id": 90}
        }
        ```
    *   **Response Handling:** Display predicted weaknesses.
*   **Local State:** Predicted weakness data.

#### 3.12.2. AI Word Problem Request Screen (Could be part of a "Creative Corner" or similar)
*   **Purpose:** User requests an AI-generated word problem.
*   **UI Sketch:**
    ```
    AppBar: "AI Word Problem Generator"
    Topic Input Field (e.g., "Algebra Fractions")
    Keywords Input Field (comma-separated, e.g., "apples, shared, remaining")
    Max Length Slider/Input
    Generate Problem Button
    Display Area for Generated Problem:
      [Generated Problem Text]
    ```
*   **Data Displayed:** Input fields, generated problem.
*   **User Interactions:** Enter topic, keywords, max length. Tap "Generate".
*   **API Calls:**
    *   **Trigger:** Tap "Generate Problem".
    *   **Endpoint:** `GET /api/v1/q/questions/generate?question_type=ai_word_problem`
    *   **Query Parameters:** `topic_id` (needs mapping from topic name to ID, or endpoint accepts name), `keywords`.
    *   **Response Handling:** Display `QuestionRead.question_text`. (Note: The current `generate_ai_word_problem` service saves the question. The endpoint returns `QuestionRead`. The frontend would display `question_text` from this.)
*   **Local State:** Form inputs, generated problem text, loading/error state.

#### 3.12.3. AI Paraphrasing Tool Screen
*   **Purpose:** User uses AI to paraphrase text.
*   **UI Sketch:**
    ```
    AppBar: "AI Paraphraser"
    Text Area: "Enter text to paraphrase"
    Simplification Level Slider/Dropdown (1-3)
    Max Length Slider/Input
    Paraphrase Button
    Display Area for Paraphrased Text:
      Original: [Original Text]
      Paraphrased: [Paraphrased Text]
    ```
*   **Data Displayed:** Input fields, original text, paraphrased text.
*   **User Interactions:** Enter text, adjust parameters, tap "Paraphrase".
*   **API Calls:**
    *   **Trigger:** Tap "Paraphrase".
    *   **Endpoint:** `POST /api/v1/ai/paraphrase`
    *   **Request Payload Example:**
        ```json
        {
          "text_to_paraphrase": "The convoluted manuscript was arduous to comprehend.",
          "simplification_level": 2,
          "max_length": 100
        }
        ```
    *   **Response Handling:** Display original and paraphrased text.
*   **Local State:** Form inputs, original text, paraphrased text, loading/error state.

#### 3.12.4. "The Guide" AI Tutor Interaction Screen
*   **Purpose:** User interacts with "The Guide" for help on a specific problem.
*   **UI Sketch (This would typically be integrated into a Question Display Screen):**
    ```
    (Within a Question Display Screen)
    Problem Statement: [Text of the current problem]
    User Attempt Input Field: "Your current step/answer"
    Submit Attempt Button
    Feedback Area from Guide:
      Correctness: [e.g., "Partially Correct"]
      Message: [e.g., "Good try! You've got the first part right."]
      Hints:
        - Hint 1: [Text] (Type: [Type])
        - Hint 2: [Text] (Type: [Type])
    ```
*   **Data Displayed:** Problem, user's attempt input, guide's feedback and hints.
*   **User Interactions:** Type attempt, submit to guide.
*   **API Calls:**
    *   **Trigger:** Tap "Submit Attempt" (or a dedicated "Ask The Guide" button).
    *   **Endpoint:** `POST /api/v1/ai/guide/submit-attempt`
    *   **Request Payload Example:**
        ```json
        {
          "problem_state": {
            "question_id": "q_current_123",
            "current_problem_statement": "What is 5 * (3+2)?"
          },
          "user_attempt": "5 * 5 = 25"
        }
        ```
    *   **Response Handling:** Display feedback message and hints from `GuideOutput`. Update problem state if guide indicates progress/completion.
*   **Local State:** Current `ProblemState`, user's current attempt text, list of `GuideHint`s, feedback messages.

## 4. Data Models (Frontend Representation)

The frontend should have corresponding data models (simple classes or integrated with state management) for the Pydantic schemas received from the backend. Examples:
*   `User` (for profile data)
*   `Token` (for auth tokens)
*   `ShopItem`
*   `InventoryItem`
*   `Topic`, `Subject` (for curriculum browsing)
*   `Question` (generic structure)
*   `Quiz` (including its questions and user answers)
*   `Minigame`
*   `MinigameProgress`
*   `Leaderboard`, `LeaderboardEntry`
*   `Quest`, `QuestObjective`
*   AI Model related schemas: `WeaknessPredictionInput/Output`, `WordProblemInput/Output`, `ParaphraseInput/Output`, `GuideInput/Output`.

These models will be populated from API responses.

## 5. Final Output Expectation for AI Frontend Developer

*   A well-structured Flutter project.
*   Separate files for each screen/widget where appropriate.
*   A clear state management approach (Provider or Riverpod).
*   A dedicated API client service.
*   Implementation of all screens and functionalities described above, interacting correctly with the specified backend API endpoints.
*   Basic loading and error states handled.
*   Navigation implemented using a declarative routing package.
*   Code should be clean, readable, and include comments where necessary.
*   Focus on functionality over pixel-perfect UI for this barebones version. Standard Material widgets are expected.

This prompt provides a comprehensive starting point. You may need to make reasonable assumptions for minor UI details or state transitions not explicitly covered. If a backend feature is a placeholder (like some AI model outputs), the frontend should gracefully handle the placeholder data or potential "service unavailable" states.
```
