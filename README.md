# AI Job Application Assistant

An AI agent that generates tailored job application cover letters — and checks its own work before handing it back to you.

Built while job-hunting, out of a simple problem: generic cover letters take forever to write by hand, but AI-generated ones will confidently invent experience you don't have if you let them. This project is my attempt at solving both problems at once.

## What it does

1. Takes a resume and a job description as input
2. Generates a tailored cover letter using an LLM (Groq / Llama 3.3)
3. **Verifies** the letter against the original resume, flagging any claim that isn't actually supported
4. If issues are found, **regenerates** with the flagged claims fed back in as explicit constraints — repeating up to a set number of attempts
5. Returns the final letter along with its verification status

The interface is a simple chat-style thread (React + Tailwind, served through Flask) — every letter you generate stays visible in the thread, tagged with a "verified" badge showing whether it came back clean or needed correction.

## Why the verification loop exists

The first version of this project generated a cover letter that confidently described me analyzing electronic health records and evaluating national HIV treatment programs — using systems and methods I have never worked with. It read completely plausibly. That's the core risk with using AI for anything factual about yourself: the model optimizes for sounding complete and convincing, not for being true.

The generate → verify → correct loop exists specifically to catch that before it reaches a real employer.

### A real failure mode I found along the way

Even with explicit instructions not to fabricate experience, the same false claims kept surviving multiple correction attempts. The pattern: every fabrication was phrased as *future interest* ("I'm excited to bring my skills to X") rather than a claim of past experience — technically not a false statement about the past, but still naming tools and programs with no real connection to me. The fix was an explicit rule blocking that framing specifically, not just blocking claims of direct experience.

This also surfaced a real precision/recall tradeoff: a stricter verifier caught more fabrication but also flagged completely normal cover-letter phrasing ("self-motivated," "results-driven") as unsupported. A looser verifier stopped over-flagging but let a real fabrication slip through, mixed into an otherwise-true sentence. There's no setting that fully solves both at once — which is why this system is built as a strong first-pass filter, not a replacement for reading the final output yourself.

## Tech stack

- **Backend:** Python, Flask
- **LLM:** Groq API (Llama 3.3 70B)
- **Frontend:** React (CDN, no build step), Tailwind CSS
- **Environment:** python-dotenv for API key management

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/ai-job-assistant.git
cd ai-job-assistant
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:
```
GROQ_API_KEY=your_key_here
```

Get a free API key at [console.groq.com](https://console.groq.com).

Run it:
```bash
python app.py
```
Visit `http://127.0.0.1:5000`

## Project structure

```
ai-job-assistant/
├── app.py                  # Flask routes
├── generate_message.py     # generate / verify / correct logic
├── templates/
│   └── index.html          # React + Tailwind chat UI
├── .env                    # API key (not committed)
├── .gitignore
└── requirements.txt
```

## Status

Working end-to-end: generation, verification, and the correction loop are functional and have been tested against real job postings. Verifier tuning (the precision/recall tradeoff above) is an ongoing refinement, not a solved problem — noted here deliberately rather than overstated.

## What's next

- Tighter verifier tuning to reduce both false flags and missed fabrications
- Deployment (Render/Railway) for a live, shareable demo
- Support for multiple resume/job description pairs in one session

---

Built by [Your Name] — [LinkedIn] · [Blog/Medium]
