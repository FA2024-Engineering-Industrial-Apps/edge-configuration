from pydantic import BaseModel
import requests

from constants import IEM_API
from auth import get_token


class AppConfig(BaseModel):
    name: str
    id: str
    templateId: str
    templateFileName: str


class App(BaseModel):
    name: str
    description: str
    id: str
    configs: list[AppConfig]
    projectId: str


def get_app_details(app_id: str) -> App:
    """Gets information about app and its configurations based on the app id

    Args:
        app_id (str): ID of App

    Returns:
        App: data about app
    """
    response = requests.get(
        IEM_API + f"/applications/{app_id}",
        headers={"Authorization": get_token()},
    )

    if not response.ok:
        raise ConnectionError(
            f"Error when trying to get app details for app with id {app_id} \n {response.text}"
        )

    raw_app_data = response.json()
    my_app = App(
        name=raw_app_data["title"],
        description=raw_app_data["description"],
        id=raw_app_data["id"],
        configs=[],
        projectId=raw_app_data["projectId"],
    )

    response = requests.get(
        IEM_API + f"/applications/{app_id}/configs",
        headers={"Authorization": get_token()},
    )

    if not response.ok:
        raise ConnectionError(
            f"Error when trying to get app configurations for app with id {app_id} \n {response.text}"
        )

    raw_configs = response.json()["data"]

    for raw_config in raw_configs:
        my_app.configs.append(
            AppConfig(
                name=raw_config["displayName"],
                id=raw_config["appConfigId"],
                templateId=raw_config["templateVo"]["appConfigTemplateId"],
                templateFileName=raw_config["templateVo"]["filename"],
            )
        )

    return my_app

