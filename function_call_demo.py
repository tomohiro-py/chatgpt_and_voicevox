from my_module.chat_gpt import Chatgpt
from my_module.messages import Messages

# import pyttsx3

def main():
    ai = Chatgpt()
    msg = Messages()
    msg.renew_system_message("You are an excellent AI assistant. If the user indicates their intention to end the conversation, please respond with '[END]'.")
    # engine = pyttsx3.init()

    while True:
        try:
            ipt = input("USER : ")
            msg.add_user_message(ipt)
            print('AI : ', end='')
            res = ai.chat_stream(msg.build())
            msg.add_assistant_message(res)
            # engine.say(res)
            # engine.runAndWait()

            if '[END]' in res:
                break
        except KeyboardInterrupt:
            print("Stopped")
            break

if __name__=='__main__':
    main()