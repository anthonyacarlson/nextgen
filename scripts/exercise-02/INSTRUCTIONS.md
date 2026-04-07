# Exercise 0x02 - Craft Context

## Objective
Experiment with various types of context to improve Juice Shop analysis results

The goal of the provided script is to query security information from the vector database previously generated from code for the open source Juice Shop project and to find out as much information about the application as possible.

## Instructions
### 1. Run Script
Open _exercise-02/building\_with\_context.py_ and view both the `system_prompt_template` and `user_question` variables. Both provide reasonable instructions to review and provide answers about the targeted application give the current vector database and provided context.

Run the script to view the current output
```sh
python scripts/exercise-02/building_with_context.py
```

Observe the output based on context provided.

### 2. Review Current Context
Open the _juice\_shop\_knowledgbase.md_ file and note the quality of the provided data set.

```text
Typically, Node.js web application libraries will be located in a `yarn` file or `package.json`

### When it comes to Node.js web applications, the following is a list of security-specific libraries:

Input Sanitization/Validation
===

- Joi
- Validator
- Express-Validator

Authentication
===

- jsonwebtoken
- passport.js
- express-jwt

Authorization
===

- casbin
- accesscontrol
```

### 3. Improve Context

Both the sparseness of recommendations and lists could cause issues especially with custom libraries, large applications, and specific patterns. We want to improve the overall quality of the results by adding additional context to either the user question or by modifying the knowledgebase.

For this exercise, provide the current knowledgebase to ChatGPT or Gemini (or run the local chatbot) and ask for improvements to the various sections. This can be done per section or utilizing the full file. Run the script repeatedly as you make changes to observe output behavior.

