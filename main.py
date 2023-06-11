import openai
import config
from itertools import zip_longest
import my_module as st
import asyncio

openai.api_key = config.openai_api_key

# st.voicevox_text_to_speech('ハロー！')
def main():
    with open('system.prompt', 'r', encoding='utf-8') as f:
        system_content = f.read()

    system_message = dict(role='system', content=system_content)
    user_messages = []
    ai_messages = []

    while True:
        # user_content = input('YOU : ')
        user_content = st.speech_to_text()
        print(f'YOU : {user_content}')

        if user_content.lower() == "bye now":
            st.play_wavfile('wav/ending.wav')
            break
        elif user_content == "おしまい":
            st.play_wavfile('wav/ending.wav')
            break
        else:
            user_dict = dict(role='user',content=user_content)
            user_messages.append(user_dict)

        messages = []
        messages.append(system_message)

        if len(ai_messages) == 0:
            messages.extend(user_messages)
        else:
            for (user_message, ai_message) in zip_longest(user_messages, ai_messages):
                messages.append(user_message)
                if ai_message is not None:
                    messages.append(ai_message)
        
        ai_content = asyncio.run(st.async_chatgpt_to_voicevox(messages))
        ai_dict = dict(role='assistant',content=ai_content)
        ai_messages.append(ai_dict)

        if config.openai_prompt_threshold < len(user_messages):
            del user_messages[0]
            del ai_messages[0]


if __name__ == '__main__':
    main()
