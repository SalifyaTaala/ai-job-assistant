import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_cover_message(job_description, resume_text, tone="professional"):
    prompt = f"""You are an expert career coach. Write a tailored, compelling 
cover letter/outreach message for this job application.

CANDIDATE RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Instructions:
- Tone: {tone}
- Keep it concise (250-350 words)
- Only use experience, skills, and achievements explicitly stated in the resume above.
- Do NOT infer, assume, or add specific claims not directly stated.
- If the job asks for experience not present in the resume, focus on the closest genuinely relevant transferable experience — do not fabricate direct experience.
- Avoid generic phrases like "I am writing to express my interest"
- End with a clear, confident call to action
- Do NOT express eagerness to work with specific named tools, systems, methods, 
or program areas (e.g. specific software, methodologies, datasets) unless they 
appear in the resume — even when framed as "eager to learn" or "excited to contribute to."
- General enthusiasm for the role or field is fine. Naming specific unlearned 
tools/methods is not.
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content


# FUNCTION 2 — verification
def verify_message(message, resume_text):
    verify_prompt = f"""Review this cover letter against the original resume. 
List any claims, experiences, or skills mentioned in the letter that are NOT 
explicitly supported by the resume. Be strict — flag anything that sounds 
like an inference or embellishment, even if plausible.Review this cover letter against the original resume.

Flag ONLY claims that are specific, checkable, and NOT supported by the resume — 
for example: named tools, systems, methods, programs, certifications, job titles, 
or specific types of experience (e.g. "epidemiology," "SmartCare," "manuscript 
development") that do not appear in the resume, whether stated as past experience 
OR as future interest/eagerness to learn.

Do NOT flag normal cover-letter framing, tone, or reasonable characterization of 
real resume content — e.g. summarizing team leadership as "self-motivated," or 
describing consistent delivery as "results-driven," is acceptable synthesis, not 
fabrication. Only flag things a reader could reasonably fact-check and find false.

RESUME:
{resume_text}

COVER LETTER:
{message}

Output only a list of unsupported claims, or "None found" if everything checks out.
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": verify_prompt}]
    )
    return response.choices[0].message.content


# FUNCTION 3 — correction (NEW, goes here, after verify_message)
def correct_message(message, resume_text, flagged_claims):
    if "none found" in flagged_claims.lower():
        return message

    correction_prompt = f"""Rewrite this cover letter to remove or correct the 
following unsupported claims. Keep everything else that IS supported by the 
resume. Do not introduce any new claims not found in the resume. Keep the 
same tone and roughly the same length.

ORIGINAL RESUME:
{resume_text}

ORIGINAL COVER LETTER:
{message}

UNSUPPORTED CLAIMS TO FIX:
{flagged_claims}

Return only the corrected cover letter, nothing else.
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": correction_prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content
def generate_verified_message(job_description, resume_text, max_attempts=3):
    known_issues = []
    message = generate_cover_message(job_description, resume_text)

    for attempt in range(max_attempts):
        flagged = verify_message(message, resume_text)

        if "none found" in flagged.lower():
            return message, flagged, attempt + 1

        known_issues.append(flagged)

        # Build a cumulative, dynamic blocklist from everything flagged so far
        all_flagged_text = "\n".join(known_issues)

        regenerate_prompt = f"""You are an expert career coach. Write a tailored, 
compelling cover letter/outreach message for this job application.

CANDIDATE RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

CRITICAL CONSTRAINT: The following claims have been flagged in previous 
attempts as NOT supported by the resume. Do NOT include them, or anything 
similar to them, in this version:
{all_flagged_text}

Instructions:
- Keep it concise (250-350 words)
- Only use experience, skills, and achievements explicitly stated in the resume above.
- Do NOT infer, assume, or add specific claims not directly stated.
- If the job asks for experience not present in the resume, focus on the closest genuinely relevant transferable experience — do not fabricate direct experience.
- End with a clear, confident call to action
- Do NOT express eagerness to work with specific named tools, systems, methods, 
or program areas (e.g. specific software, methodologies, datasets) unless they 
appear in the resume — even when framed as "eager to learn" or "excited to contribute to."
- General enthusiasm for the role or field is fine. Naming specific unlearned 
tools/methods is not.
"""
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": regenerate_prompt}],
            temperature=0.3  # lower temperature helps here too
        )
        message = response.choices[0].message.content

    # If we hit max_attempts without a clean pass, return the last version with a warning
    final_check = verify_message(message, resume_text)
    return message, final_check, max_attempts

# main block — calls all three in sequence
if __name__ == "__main__":
    resume = open("my_resume.txt").read()
    job_desc = open("job_posting.txt").read()

    final_message, final_flagged, attempts_used = generate_verified_message(job_desc, resume)

    print(f"=== FINAL MESSAGE (took {attempts_used} attempt(s)) ===")
    print(final_message)
    print("\n=== FINAL VERIFICATION ===")
    print(final_flagged)

    if "none found" not in final_flagged.lower():
        print("\n⚠️  WARNING: Could not fully verify after max attempts. Review manually before sending.")

    with open("output.txt", "w") as f:
        f.write(final_message)