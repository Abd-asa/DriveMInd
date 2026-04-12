# 🚗 DriveMind: Agentic VLM Dashcam Analyst

DriveMind is a stateful, multimodal AI application designed to analyze dashcam footage and provide real-time, structured safety assessments. Powered by Google's Gemini Vision Language Models and LangChain, it acts as a virtual co-pilot, identifying road hazards and answering user queries with professional accuracy.

## ✨ Features
* **Multimodal Chat Interface:** Upload dashcam frames directly in the chat bar and ask specific questions about the scene.
* **Agentic Structured Output:** The backend LLM is constrained via Pydantic to output strict JSON blueprints, dynamically triggering UI color-coded hazard alerts (Red for High, Yellow for Medium, Green for Low).
* **Stateful Memory:** A persistent, threaded chat history. Switch between multiple chat sessions without losing your context or having to re-upload images.
* **Modern Streamlit UI:** Features a sleek sidebar navigation, invisible native layout hacks, and a centralized modal dialog for renaming and deleting chat threads.

## 🛠️ Tech Stack
* **Frontend:** [Streamlit](https://streamlit.io/) (v1.43.0+)
* **Backend:** Python 3.10
* **AI Orchestration:** [LangChain](https://www.langchain.com/) (`langchain-google-genai`)
* **Vision Model:** Google Gemini 2.5 Flash
* **Data Validation:** Pydantic

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone git@github.com:YOUR-USERNAME/DriveMind.git
cd DriveMind
```

### 2. Set Up the Environment
It is recommended to use Conda or venv to manage dependencies.

```bash
conda create -n drivemind-env python=3.10
conda activate drivemind-env

pip install streamlit langchain-google-genai google-generativeai pydantic python-dotenv pillow
```

### 3. Configure API Keys
Create a `.env` file in the root directory of the project:

```bash
touch .env
```

Add your Google AI Studio API key to the `.env` file:

```text
GOOGLE_API_KEY=your_api_key_here
```
*(Note: Ensure .env is added to your .gitignore file to prevent leaking credentials!)*

### 4. Run the Application
Launch the Streamlit server from your terminal:

```bash
streamlit run app.py
```
The application will automatically open in your browser at `http://localhost:8501`.

## 📁 Project Structure
```text
DriveMind/
├── app.py                  # Main Streamlit frontend and UI logic
├── .env                    # Environment variables (API Keys)
├── .gitignore              # Git ignore rules
├── sample_images/          # Test dashcam frames
│   └── test.jpg            
└── src/                    # Backend modular code
    ├── api_client.py       # LangChain/Gemini integration and Pydantic schemas
    └── prompts.py          # System prompts and AI persona definitions
```

## 🤝 Contributing
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request