import json
import os
import time
import logging
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader

from services.tools import tools, TOOL_MAP

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()


class Me:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError("GROQ_API_KEY not set in .env")

        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key,
        )

        self.name = "Arun Yadav"

        self.linkedin_text = self._read_pdf(BASE_DIR / "me" / "linkedin.pdf")
        self.summary = self._read_text(BASE_DIR / "me" / "summary.txt")

    # ── File Readers ─────────────────────────────────

    def _read_pdf(self, path: Path) -> str:
        if not path.exists():
            logger.warning(f"PDF not found: {path}")
            return ""

        try:
            reader = PdfReader(path)
            return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            return ""

    def _read_text(self, path: Path) -> str:
        if not path.exists():
            logger.warning(f"Text file not found: {path}")
            return ""

        try:
            return path.read_text(encoding="utf-8").strip()
        except Exception as e:
            logger.error(f"Error reading text: {e}")
            return ""

    # ── System Prompt ─────────────────────────────────

    def system_prompt(self) -> str:
        return f"""
You are {self.name}, speaking directly to visitors on your personal website.

━━━ YOUR BACKGROUND ━━━
{self.summary}

━━━ YOUR LINKEDIN ━━━
{self.linkedin_text}

━━━ RULES & BEHAVIOR ━━━

1. IDENTITY: Speak warmly, professionally, and naturally. You are an AI digital twin of Arun. When appropriate, acknowledge it simply, but mostly speak with Arun's voice and experience.
2. CONCISENESS: Keep answers strictly under 3 short paragraphs. People don't read long walls of text.
3. CONVERSATION CONTROL: Guide the conversation. If asked a generic question, relate it back to your expertise or projects.
4. LEAD CAPTURE (CRITICAL): If the user shows ANY interest in hiring, collaborating, interviewing, or meeting, you MUST explicitly ask for their email or LinkedIn. Once provided, IMMEDIATELY call `save_user_details`. Do not miss this opportunity.
5. UNKNOWNS: If asked something not in your context, do not make it up. Log it using `save_unknown_questions`, then smoothly steer the conversation back to your known expertise.
6. PROACTIVE: When appropriate, end your answer with a conversational hook (e.g., "What kind of systems are you building right now?").
7. NO RAW CODE: Never output raw `<function=...>` tags in your conversation text. Use the provided tools silently.
""".strip()

    # ── Tool Handling ─────────────────────────────────

    def handle_tools(self, tool_calls):
        results = []

        for tc in tool_calls:
            name = tc.function.name

            try:
                args = json.loads(tc.function.arguments)
            except:
                args = {}

            func = TOOL_MAP.get(name)

            if func:
                result = func(**args)
            else:
                result = {"error": "unknown tool"}

            results.append({
                "role": "tool",
                "content": json.dumps(result),
                "tool_call_id": tc.id,
            })

        return results

    # ── Main Chat ─────────────────────────────────

    def chat(self, message: str, history: list) -> str:
        history.append({"role": "user", "content": message})
        
        # Build messages for LLM
        messages = [{"role": "system", "content": self.system_prompt()}]
        messages.extend(history)

        for _ in range(3):
            try:
                response = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                )
            except Exception as e:
                logger.error(f"LLM API Error: {e}")
                return "I'm having a bit of trouble connecting to my brain right now. Could you try again in a moment?"

            choice = response.choices[0]

            if choice.finish_reason == "tool_calls":
                msg = choice.message

                messages.append(msg)
                history.append(msg)

                tool_results = self.handle_tools(msg.tool_calls)
                messages.extend(tool_results)
                history.extend(tool_results)

            else:
                final_content = choice.message.content or ""
                # Clean up any leaked <function=...> artifacts from Llama 3
                import re
                final_content = re.sub(r'<function=[^>]+>.*?\}', '', final_content, flags=re.DOTALL).strip()
                
                history.append({"role": "assistant", "content": final_content})
                return final_content

        fallback = "I think I got a bit lost in my thoughts. Could you rephrase what we were talking about?"
        history.append({"role": "assistant", "content": fallback})
        return fallback