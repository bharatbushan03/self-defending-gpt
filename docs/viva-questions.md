# Viva Questions and Answers

## 1. What is the main objective of this project?
**Answer:** The main objective is to build a "Self-Defending GPT" system that actively monitors, detects, and mitigates adversarial attacks on Large Language Models, such as prompt injections and jailbreaks. It acts as a secure middleware, ensuring that only safe prompts are processed while providing detailed analytics on attempted attacks.

## 2. How does the system detect malicious prompts?
**Answer:** The system uses an interceptor pattern. Before sending the user's prompt to the main generative model, it is first sent to a specialized security model (LlamaGuard via NVIDIA API). This model acts as an evaluator, classifying the prompt as either safe, suspicious, or malicious based on predefined policies.

## 3. What happens if a user repeatedly sends malicious prompts?
**Answer:** The system implements a "trust score" mechanism. Each time a malicious prompt is detected, the user's trust score decays. If the score falls below certain thresholds, the system escalates its mitigation actions, moving from simple warnings to outright blocking the user's requests, even if subsequent prompts are only marginally suspicious.

## 4. Can you explain the tech stack used and why it was chosen?
**Answer:**
- **Frontend (Next.js):** Chosen for its performance, ease of building React applications, and routing capabilities.
- **Backend (FastAPI):** Chosen for its high performance, native async support, and excellent integration with Python AI libraries.
- **Database (MongoDB):** A NoSQL database was chosen for its flexibility in logging JSON-like documents, which is ideal for storing varied metadata associated with security logs.

## 5. What is the difference between Prompt Injection and Jailbreaking?
**Answer:**
- **Prompt Injection:** An attacker attempts to override the original instructions given to the LLM by the developer, often to make the model perform unintended actions or extract sensitive data.
- **Jailbreaking:** A specific form of prompt injection where the attacker tries to bypass the safety and ethical guardrails placed on the LLM by its creators (e.g., making it generate harmful or illegal content).

## 6. How is the dashboard data generated?
**Answer:** Every time a prompt is evaluated, regardless of whether it's safe or malicious, the backend creates a log entry containing the user ID, the prompt, the assigned risk score, the classification label, and the action taken. This log is stored in MongoDB. The frontend dashboard then fetches these logs via a `/logs` API endpoint and visualizes the data using Recharts.

## 7. How would you improve this system in the future?
**Answer:** Future improvements could include implementing more advanced behavioral analytics to detect distributed or slow-burn attacks over time. We could also add automated IP banning at the network level, allow administrators to customize security policies directly from the dashboard, and use an ensemble of different security models to improve detection accuracy.
