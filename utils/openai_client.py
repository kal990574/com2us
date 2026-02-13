import streamlit as st
from openai import OpenAI


@st.cache_resource
def get_openai_client():
    return OpenAI(api_key=st.secrets["API_KEY"])


def generate_chat(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    client = get_openai_client()
    kwargs = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.9,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content


def generate_chat_with_image(system_prompt: str, user_text: str, base64_image: str, json_mode: bool = False) -> str:
    client = get_openai_client()
    kwargs = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                ],
            },
        ],
        "max_tokens": 2000,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content


def generate_chat_stream(system_prompt: str, user_prompt: str):
    """스트리밍 응답 제너레이터 - st.write_stream()과 함께 사용"""
    client = get_openai_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.9,
        stream=True,
    )
    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def generate_image(prompt: str, size: str = "1024x1024") -> str | None:
    client = get_openai_client()
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        n=1,
        quality="standard",
    )
    return response.data[0].url
