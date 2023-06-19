# History Class
ユーザーの入力メッセージと、AIからの回答を順に記録していく
functionなど、回答生成までの経過は含まない。

## method
- add_user_message
- add_assistant_message

# Memory Class
ユーザーとAIの過去のやり取りを要約して保存しておく。
趣味嗜好、関心のある事柄などは、記録する。
historyクラスからChatGPT自身に作成させる。

### method
- dumps / dump
- loads / load

# Prompt Class
templateにたいして、Memory、History（最新の入力と過去の履歴）、pre-function、を取り込んで、最終的なpromptを生成する。

## method
- build
- exec_pre_function
テンプレ―トに記載のあるfunctionがあれば、それを実行して、結果を記載する。

# Chatgpt Class
入力されたプロンプトに対して、回答を生成する。
function_callはこのクラスのメソッド内部で処理する。
システムPromptは、このクラス内で処理する。
 - chat(prompt, system_prompt)
 - achat(prompt, system_prompt)
 - add_system_prompt
