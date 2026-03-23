from services.me_agent import Me
import logging

logging.basicConfig(level=logging.DEBUG)

try:
    print("Initializing agent...")
    me = Me()
    print("Testing chat...")
    resp = me.chat("Hello, I am looking to hire you for a project. My email is test@test.com and phone is 555-0100.", history=[])
    print("EXPECTED RESP:", resp)
except Exception as e:
    print("DIAGNOSTIC CRASHED:", str(e))
