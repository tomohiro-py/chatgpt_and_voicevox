from my_module.chat_gpt import Chatgpt
from my_module.messages import Messages


def main():
    ai = Chatgpt()
    msg = Messages()
    msg.renew_system_message("""You are my good friend.
                                If you need, You can access real internet.
                                If the user indicates their intention to end the conversation, 
                                please respond with '[END]'.""")

    while True:
        try:
            ipt = input("USER : ")
            msg.add_user_message(ipt)
            print('AI : ', end='')
            res = ai.chat_stream(msg.build())
            msg.add_assistant_message(res)

            if '[END]' in res:
                break
        except KeyboardInterrupt:
            print("Stopped")
            break

if __name__=='__main__':
    main()