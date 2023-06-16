from my_module.chat_gpt import Chatgpt
from my_module.messages import Messages

# import pyttsx3

def main():
    ai = Chatgpt()
    msg = Messages()
    msg.renew_system_message("あなたは優秀なAIアシスタントです。ユーザーから会話終了の意向を告げられた場合には、'[END]'を回答してください。")
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