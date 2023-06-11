from pytest import MonkeyPatch

import main
import my_module as st

@MonkeyPatch
def test_speech_to_text():
    st.speech_to_text()