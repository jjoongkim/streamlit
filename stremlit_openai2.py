from openai import OpenAI
import streamlit as st
import time

assistant_id = 'asst_AFfxBHzSo4b0C4Y4hUJ8hY6T'
# thread_id = 'thread_rtnIcfC2K1U0isdXh8ZzJuT8' # threadID를 고정할 경우 1명을 위한 것이므로 아래에서 다시 구현한다.

with st.sidebar:
    # 후원하기 링크 달기
    st.link_button("더 좋은 컨텐츠를 위해 후원하기", "https://toss.me/kimfl")
    # 배너광고 달기(예 쿠팡 파트너 배너광고)
    iframe_html = """<iframe>배너광고</iframe>"""
    st.markdown(iframe_html, unsafe_allow_html=True) # True로 하지 않을 경우 이미지없이 url링크가 표기된다.
    st.info("이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 받습니다.")

    openai_api_key = st.text_input("OpenAI API KEY", type="password")
    
    client = OpenAI(api_key=openai_api_key)

    thread_id = st.text_input("Thread ID") # thread_id는 개인화를 위해 삭제한다.

    # 버튼을 만들어 새로운 thread를 받아서 사용하는 코드
    # 스레드를 새로 생성할 경우
    # 새로운 대화가 시작된다.(즉, 앞서 물어본(대화)것은 무시됨)
    thread_make_btn = st.button("Create a new thread")
    if thread_make_btn:
        # 스레드 생성
        thread = client.beta.threads.create()
        thread_id = thread.id
        st.subheader(f"{thread_id}", divider="rainbow")
        st.info("새로운 스레드가 생성되었습니다.")

st.title("My OpenAI ChatBots")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "안녕하세요. 선생님에게 뭐든 물어보세요?"}] # 메세지 뿌려지는 곳에 공백에 ~~~이 문장이 먼저 뿌려진다.

print(f"st.session_state\n{st.session_state}") # session_state: 현재 메시지 상태를 저장
print()

# 앞서 채팅한 메세지를 기록하여 화면에 보여준다.
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

prompt = st.chat_input()
if prompt:
    # client = OpenAI(api_key=openai_api_key) # 새로운 thread를 사용하기 위해 주석처리하고 위쪽에 다시 구현하도록 한다. 
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt) # 여기는 채팅창에 입력한 값이 화면에 보여지기까지만 하고 아직 전송전
    
    # response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.messages)
    response = client.beta.threads.messages.create(thread_id=thread_id, role="user", content=prompt)
    run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)
    run_id = run.id

    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        if run.status == "completed":
            break
        else:
            time.sleep(2)

    # assistant로 부터 받은 메세지 담아서 출력
    # assistant_content = response.choices[0].message.content
    thread_messages = client.beta.threads.messages.list(thread_id)
    assistant_content = thread_messages.data[0].content[0].text.value

    st.session_state.messages.append({"role": "assistant", "content": assistant_content})
    st.chat_message("assistant").write(assistant_content)

    print(st.session_state.messages)

