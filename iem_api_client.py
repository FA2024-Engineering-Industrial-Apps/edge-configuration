import requests  # type: ignore
import dotenv  # type: ignore
import pydantic
import os
from pydantic import BaseModel
import streamlit as st
from model import DeviceModel

HOST = "https://ferienakademie-udeliyih.iem.eu1.edge.siemens.cloud"
LOGIN_ROUTE = HOST + "/portal/api/v1/login/direct"
DEVICE_ROUTE = HOST + "/portal/api/v1/devices"


class AuthToken(BaseModel):
    access_token: str
    expires_in: int


def ensure_login():
    if "iem_token" not in st.session_state:
        login()


def login():
    response = requests.post(
        LOGIN_ROUTE,
        json={
            "username": st.session_state["iem_user"],
            "password": st.session_state["iem_pass"],
        },
    )
    token = AuthToken.model_validate(response.json()["data"])
    st.session_state["iem_token"] = token.access_token


def create_device(device: DeviceModel):
    ensure_login()
    response = requests.post(
        DEVICE_ROUTE,
        headers={"Authorization": f"Bearer {st.session_state['iem_token']}"},
        json=device.dict(),
    )
    return response.json()
