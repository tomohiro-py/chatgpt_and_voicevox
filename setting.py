import os
from dotenv import load_dotenv

load_dotenv()

def main():
    if os.getenv('openai_api_key') is not None:
        print('Success')
    else:
        print('Oops')

if __name__ == '__main__':
    main()
