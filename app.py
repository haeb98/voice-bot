import streamlit as st

# pip install streamlit-audiorecorder
from audiorecorder import audiorecorder
import openai_api
# pip install streamlit-chat
from streamlit_chat import message as msg

def main():
    st.set_page_config(
        page_title='🎙️Voice Chatbot🎙️',
        layout='wide'
    )
    st.header("🎙️Voice Chatbot🎙️")

    with st.expander('How to use Voice Chatbot', expanded=True):
        st.write(
            """
            1. 녹음하기 버튼을 눌러 질문을 녹음한다.
            2. 녹음이 완료되면 자동으로 Whisper 모델을 이용해 음성을 텍스트로 변환 후 LLM에 질의한다.
            3. LLM의 응답을 다시 TTS 모델을 사용해 음성으로 변환하고 이를 사용자에게 응답한다.
            4. LLM은 OpenAI사의 GPT 모델을 사용한다.
            5. 모든 질문/답변은 텍스트로도 제공된다.
            """
        )

    system_instruction = '당신은 친절한 챗봇입니다.'

    # session state 초기화
    # - messages: LLM 질의/ 웹페이지 시각화를 위한 대화내역
    # - check_reset: 초기화를 위한 flag

    if 'messages' not in st.session_state:
        st.session_state['messages'] = [
            {'role': 'system', 'content': system_instruction}
        ]

    if 'check_reset' not in st.session_state:
        st.session_state['check_reset'] = False

    with st.sidebar:
        model = st.radio(label='GPT 모델', options=['gpt-3.5-turbo', 'gpt-4-turbo', 'gpt-4o'], index=2)
        print(model)

        if st.button(label='초기화'):
            st.session_state['messages'] = [
                {'role': 'system', 'content': system_instruction}
            ]
            st.session_state['check_reset'] = True # 화면 정리

    col1, col2 = st.columns(2)
    with col1:
        st.subheader('🎙️녹음하기')

        audio = audiorecorder()

        if (audio.duration_seconds > 0) and (st.session_state['check_reset'] == False):
            st.audio(audio.export().read())
            # 사용자 음성에서 텍스트 추출
            query = openai_api.stt(audio)
            print('q:', query)
            # LLM 질의
            st.session_state['messages'].append({'role':'user',
                                                 'content':query})
            response = openai_api.ask_gpt(st.session_state['messages'], model)
            st.session_state['messages'].append({'role':'assistant',
                                                 'content':response})
            print('a:',response)
            # 음성으로 변환
            audio_tag = openai_api.tts(response)
            st.html(audio_tag) # 시각화 없이 자동으로 재생

    with col2:
        st.subheader('❔질문/답변')
        if (audio.duration_seconds > 0) and (st.session_state['check_reset'] == False):
            for i, message in enumerate(st.session_state['messages']):
                role = message['role']
                content = message['content']
                if role == 'user':
                    msg(content, is_user=True, key=str(i))
                elif role == 'assistant':
                    msg(content, is_user=False, key=str(i))
        else:
            st.session_state['check_reset'] = False


if __name__ == '__main__':
    main()