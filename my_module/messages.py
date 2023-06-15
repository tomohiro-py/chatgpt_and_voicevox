from itertools import zip_longest
from prompt_template.system_prompt import system_message
from prompt_template.messages_template import messages_template
import config

class Messages:

    def __init__(self) -> None:
        self.messages = []
        self.system_message = system_message
        self.messages_templeate = messages_template
        self.max_messages = config.openai_max_maesages


    def add_system_message(self, system_message):
        self.system_message = dict(role='system',content=system_message)


    def add_assistant_message(self, assistant_message):
        assistant_dict = dict(role='assistant',content=assistant_message)
        self.messages.append(assistant_dict)


    def add_user_message(self, user_message):
        user_dict = dict(role='user',content=user_message)
        self.messages.append(user_dict)


    def build(self) -> list:
        len_messages = len(self.messages)
        diff = len_messages - self.max_messages
        if 0 < diff:
            result = self.messages[diff:len_messages]
        else:
            result = self.messages[0:len_messages]

        result.insert(0, self.system_message)
        return result
    
    def build_from_template(self):
        pass

def main():
    system_message = "これはシステムメッセージ"
    user_message = "これはユーザーメッセージ{}"
    assistant_message = "これはアシスタントメッセージ{}"

    msg = Messages()
    msg.add_system_message(system_message)

    for i in range(20):
        msg.add_user_message(user_message.format(i))
        msg.add_assistant_message(assistant_message.format(i))

    # print(msg.messages)
    print(msg.build())
    # print(msg.build())

if __name__=='__main__':
    main()