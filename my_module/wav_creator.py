import my_module as st
import random



def main():
    text = 'ありがとうございました。またのご利用をお待ちしております。'
    path = 'ending.wav'

    audio_query = st.voicevox_post_audio_query(text)
    audio = st.voicevox_post_synthesis(audio_query)

    with open(path, 'wb') as f:
        f.write(audio)

    st.play_wavfile(path)

if __name__ == '__main__':
    main()