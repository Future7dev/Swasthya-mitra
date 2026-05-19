# Swasthya Mitra

Swasthya Mitra is an intelligent health-tech web application designed to assist users with symptom-based disease prediction, preliminary precautionary measures, and reliable medical guidance. With an integrated machine learning engine, a robust Java-based backend, a highly interactive React frontend, and a sophisticated FastAPI-based HealthBot microservice, Swasthya Mitra aims to provide an accessible and comprehensive health advisory platform.

## 🚀 Project Features & Implementation Details

This project is built using a modern microservices approach. Below is a detailed technical breakdown of each core feature, especially focusing on our intelligent HealthBot.

### 1. Interactive HealthBot Assistant (FastAPI Microservice)
The HealthBot is the brain of Swasthya Mitra's conversational interface. Built in Python using FastAPI, it handles multi-turn conversations, extracts medical context, and combines rule-based safety with LLM-powered empathy. 

**Implementation Details:**
- **NLP & Context Extraction (`nlp.py` & `context.py`):** User input is normalized and tokenized. The system uses a combination of Regex, custom token matching, and optional SpaCy integration to extract `symptoms`, `duration` (e.g., "for 3 days"), `severity` (e.g., "severe", "mild"), and user `intent` (e.g., emergency, medical advice). It actively detects negation (e.g., "no fever") to prevent false positives.
- **Rule-Based Safety & Confidence Engine (`confidence.py`, `clarify.py`, `response.py`):** Before making any predictions, the system assesses its "confidence" based on the extracted context. If the extracted symptoms are ambiguous, the `clarify.py` module takes over to ask targeted follow-up questions. If confident, it pulls verified medical advice and precautions from strict local JSON rule files (`symptoms.json`, `emergencies.json`).
- **LLM Enhancement Pipeline (`llm.py`):** To make the bot sound empathetic and human, the strict rule-based response, conversation history, and current medical context are injected as a system prompt into a Large Language Model. The system dynamically supports Ollama (local), OpenAI (GPT), and Google Gemini via API keys configured in a `.env` file. 
- **Session Management (`session.py` & `database.py`):** A local SQLite database (`healthbot.db`) maintains chat history and user context across API calls. A background thread runs continuously to clean up expired sessions (default timeout is 30 minutes).

### 2. Intelligent Disease Prediction (Machine Learning)
Swasthya Mitra doesn't just guess; it predicts possible conditions based on statistical models.

**Implementation Details:**
- **Data Pipeline:** The model is trained on a massive dataset of symptoms-to-disease mappings (`Training.csv`). The data cleaning and training pipeline is documented in `Final_Disease.ipynb`.
- **Model Architecture:** The system uses Scikit-Learn to encode symptoms (`label_encoder.pkl` and `symptoms.pkl`) and infer diseases using a trained classifier (`model.pkl`). 
- **Serving:** The `.pkl` files are loaded into memory by the Python backend to provide sub-second inference times when the HealthBot accumulates enough symptoms.

### 3. Voice-Enabled Input (Frontend)
To make the application accessible to users who may be unable to type, Swasthya Mitra supports continuous voice dictation.

**Implementation Details:**
- **Web Speech API:** Leverages the native browser Web Speech API.
- **React Integration:** Uses the `react-speech-recognition` hook to continuously listen to the user's microphone, transcribe speech to text in real-time, and automatically pipe the text into the HealthBot's chat input field.

### 4. Geographic Medical Assistance (Frontend)
Users can find nearby medical facilities if the HealthBot detects an emergency or recommends an in-person visit.

**Implementation Details:**
- **Map Rendering:** Built using `react-leaflet` to render a fully interactive Leaflet map layer within the React application.
- **Geolocation:** It requests the user's browser location to center the map and plot hospital or clinic coordinates using custom map markers.

### 5. Secure User Authentication & Core Backend
The central nervous system of the app relies on a rock-solid Spring Boot architecture.

**Implementation Details:**
- **Java Spring Boot:** Provides the main REST API for user management and saving long-term health profiles.
- **Security:** Spring Security filters intercept HTTP requests, verifying JSON Web Tokens (JWT) to ensure endpoints are protected.
- **Persistence:** Spring Data JPA automatically translates Java entity objects into SQL queries, storing user credentials securely (using bcrypt password hashing) in a MySQL database.

---

## 🛠️ Tech Stack

### Frontend
- **Framework:** React.js (v19) with Vite
- **Styling:** Bootstrap, CSS3
- **Mapping:** Leaflet & React-Leaflet
- **Voice Recognition:** React Speech Recognition
- **Routing & API:** React Router v7, Axios

### Backend (Core)
- **Framework:** Spring Boot (Java 17)
- **Security:** Spring Security
- **Database:** MySQL (via Spring Data JPA)
- **Build Tool:** Maven

### Microservices & ML Engine
- **HealthBot Service:** FastAPI (Python) with CORS, session management, and LLM enhancement capabilities.
- **Machine Learning:** Scikit-Learn (models saved as `.pkl`), Pandas & Jupyter Notebooks for training (`Final_Disease.ipynb`).
- **Local DB (Bot):** SQLite (`healthbot.db`)

---

## 📁 Repository Structure

```
swasthya-mitra/
├── Backend/
│   ├── src/                # Spring Boot application source code
│   ├── pom.xml             # Maven dependencies configuration
│   └── services/
│       └── healthbot/      # FastAPI Microservice for Chat & ML predictions
│           ├── app.py      # FastAPI entry point
│           ├── rules/      # Symptom and emergency rules JSON files
│           ├── utils/      # NLP, LLM, session, and context management
│           └── healthbot.db# SQLite Database for session state
├── frontend/
│   ├── src/                # React Vite frontend source code
│   ├── public/             # Static assets
│   ├── package.json        # Node.js dependencies
│   └── vite.config.js      # Vite build configuration
├── ML_Model/
│   ├── Final_Disease.ipynb # Model training notebook
│   ├── Training.csv        # Training dataset
│   ├── Testing.csv         # Testing dataset
│   └── *.pkl               # Serialized ML models & Encoders
└── README.md
```

## 💻 Getting Started

Follow these steps to set up the project locally.

### 1. Clone the Repository
```bash
git clone https://github.com/rohankharche34/swasthya-mitra.git
cd swasthya-mitra
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The frontend will run on the default Vite port (usually `http://localhost:5173`).

### 3. Core Backend (Spring Boot) Setup
Ensure you have Java 17 and Maven installed. Update your MySQL database credentials in the `application.properties` or `application.yml` file within `Backend/src/main/resources/`.
```bash
cd Backend
./mvnw spring-boot:run
```

### 4. HealthBot Microservice Setup
The HealthBot microservice powers the conversational AI and symptom analysis. Ensure Python 3.8+ is installed.
```bash
cd Backend/services/healthbot
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload
```
The FastAPI microservice will be available at `http://localhost:8000`.

## 🤝 Contributing Guidelines

Contributions are welcome! Please follow these steps:
1. **Fork the repository** on GitHub.
2. **Create a new branch:** `git checkout -b feature/your-feature-name`
3. **Make your changes** and commit them: `git commit -m "Add your message"`
4. **Push to the branch:** `git push origin feature/your-feature-name`
5. **Open a Pull Request** describing your changes.

Ensure your code follows the project's existing linting and formatting rules. For the frontend, you can run `npm run lint`.

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
