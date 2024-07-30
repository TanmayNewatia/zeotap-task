### Rule Engine Project Documentation

---

#### Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Backend API Design](#backend-api-design)
4. [Frontend Implementation](#frontend-implementation)
5. [Setup and Deployment](#setup-and-deployment)
6. [Example Use Cases](#example-use-cases)

---

### Project Overview

The Rule Engine project is a system designed to dynamically create and evaluate rules against user data. The system comprises a backend API built with Flask and a frontend implemented in HTML and JavaScript. Users can create and evaluate rules based on user attributes like age, department, income, and experience.

### System Architecture

The system consists of two main components:
1. **Backend API**: Handles rule creation, user data management, rule combination, and rule evaluation.
2. **Frontend Interface**: Allows users to interact with the backend API to create users, rules, combine rules, and evaluate rules.

---

### Backend API Design

#### Overview

The backend API provides endpoints to:
- Create users
- Create rules
- Combine rules into a single Abstract Syntax Tree (AST)
- Evaluate rules against user data
- Evaluate combined rules against a dataset

#### Endpoints

1. **Create User**
   - **Endpoint**: `/users`
   - **Method**: `POST`
   - **Description**: Creates a new user with specified attributes.
   - **Request Body**:
     ```json
     {
       "data": {
         "name": "John Doe",
         "age": 30,
         "department": "Sales",
         "income": 50000,
         "experience": 5
       }
     }
     ```
   - **Response**:
     ```json
     {
       "user_id": 1,
       "message": "User created successfully"
     }
     ```

2. **Create Rule**
   - **Endpoint**: `/rules`
   - **Method**: `POST`
   - **Description**: Creates a new rule.
   - **Request Body**:
     ```json
     {
       "data": {
         "name": "Rule1",
         "condition": "age > 25 and income > 30000"
       }
     }
     ```
   - **Response**:
     ```json
     {
       "rule_id": 1,
       "message": "Rule created successfully"
     }
     ```

3. **Combine Rules**
   - **Endpoint**: `/combine_rules`
   - **Method**: `POST`
   - **Description**: Combines multiple rules into a single AST.
   - **Request Body**:
     ```json
     {
       "rules": ["age > 25", "income > 30000"]
     }
     ```
   - **Response**:
     ```json
     {
       "combined_rule_ast": "<AST representation>",
       "message": "Rules combined successfully"
     }
     ```

4. **Evaluate User**
   - **Endpoint**: `/evaluate/<user_id>`
   - **Method**: `GET`
   - **Description**: Evaluates a user against all created rules.
   - **Response**:
     ```json
     {
       "evaluation_result": true,
       "message": "User evaluation result"
     }
     ```

5. **Evaluate Rule with User Data**
   - **Endpoint**: `/evaluate_rule`
   - **Method**: `POST`
   - **Description**: Evaluates a rule against user data.
   - **Request Body**:
     ```json
     {
       "rule_ast": "<AST representation>",
       "data": {
         "age": 35,
         "department": "Sales",
         "income": 60000,
         "experience": 3
       }
     }
     ```
   - **Response**:
     ```json
     {
       "evaluation_result": true,
       "message": "Rule evaluation result"
     }
     ```

---

### Frontend Implementation

The frontend is a simple HTML interface with forms to interact with the backend API.

#### HTML Structure

1. **Create User Form**: 
   - Collects user details and submits them to the backend.
   
2. **Create Rule Form**:
   - Collects rule details and submits them to the backend.

3. **Combine Rules Form**:
   - Collects rule names to combine and submits them to the backend.

4. **Evaluate User Form**:
   - Collects a user ID and submits it for evaluation against existing rules.

5. **Evaluate Rule Form**:
   - Collects rule AST and user data to evaluate the rule.

#### JavaScript Functions

- **Submit Form Data**: Functions to handle form submissions, send data to the backend, and display responses.

```javascript
document.getElementById('user-form').addEventListener('submit', function (event) {
    event.preventDefault();
    const data = {
        data: {
            name: document.getElementById('name').value,
            age: document.getElementById('age').value,
            department: document.getElementById('department').value,
            income: document.getElementById('income').value,
            experience: document.getElementById('experience').value,
        }
    };
    fetch('http://127.0.0.1:5000/users', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }).then(response => response.json())
      .then(data => {
          console.log('Success:', data);
          alert('User created successfully: ' + JSON.stringify(data));
      })
      .catch(error => {
          console.error('Error:', error);
          alert('Failed to create user: ' + error);
      });
});

// Similar functions for other forms...
```
---

### Setup and Deployment

1. **Clone the Repository**:
   ```bash
   git clone <repository_url>
   cd rule-engine
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Backend Server**:
   ```bash
   python app.py
   ```

4. **Open the Frontend**:
   - Open `index.html` in a web browser.

---

### Example Use Cases

1. **Creating a User**:
   - Fill out the user form with details and submit.
   - Verify that the user is created successfully through the backend response.

2. **Creating a Rule**:
   - Define a rule condition and submit.
   - Verify the rule is created and stored in the backend.

3. **Combining Rules**:
   - Input multiple rules to be combined.
   - Verify the combined rule AST.

4. **Evaluating a User**:
   - Provide a user ID for evaluation.
   - Check the result of the evaluation against existing rules.

5. **Evaluating Rule with User Data**:
   - Provide rule AST and user data for evaluation.
   - Check the result of the evaluation.