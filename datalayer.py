from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from chainlit.data.storage_clients.s3 import S3StorageClient
import os
import json
from datetime import datetime
from chainlit.element import ElementDict
import chainlit
from chainlit.types import Feedback

from models import Messages
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
import logfire
from chainlit.logger import logger


class DataLayer:
    datalayer = None

    def __init__(self):
        conninfo = os.environ.get("DATABASE_URL")

        kwargs = {
            'aws_access_key_id': os.environ['APP_AWS_ACCESS_KEY'],
            'aws_secret_access_key': os.environ['APP_AWS_SECRET_KEY']
        }

        storage = S3StorageClient('52713ed5-d0d2-4eaf-8701-dcb26067a9f3', **kwargs)

        DataLayer.datalayer = SQLAlchemyDataLayer(conninfo=conninfo, ssl_require=True, show_logger=False,
                                                  storage_provider=storage)

    @staticmethod
    def get_data_layer():
        return DataLayer.datalayer

    @staticmethod
    async def create_cache(thread_id: str, step_id: str, args: dict, response: dict):
        columns = ['type', 'document', 'direction', 'objet', 'montant', 'montant_sup', 'comp']
        inputs = {p: args[p] for p in columns}
        inputs['forId'] = step_id
        inputs['threadId'] = thread_id
        inputs['response'] = json.dumps(response)
        inputs['direction'] = inputs['direction'][0] if isinstance(inputs['direction'], list) else inputs['direction']
        inputs['created_date'] = datetime.now()

        columns = ", ".join(f'"{key}"' for key in inputs.keys() if inputs[key] is not None)
        values = ", ".join(f":{key}" for key in inputs.keys() if inputs[key] is not None)
        query = f"""
                INSERT INTO cache_qui_signe ({columns},"feedback")
                VALUES ({values},1)
            """

        await DataLayer.get_data_layer().execute_sql(query=query, parameters=inputs)

    @staticmethod
    async def get_direction(args: dict):
        # query = """SELECT * FROM cache_qui_signe WHERE "document" = :document AND "objet" = :objet AND created_date >= NOW() - INTERVAL '30' DAY"""
        # parameters = {"document": args['document'], "objet": args['objet']}
        query = """SELECT * FROM cache_qui_signe WHERE "objet" = :objet AND (created_date >= NOW() - INTERVAL '30' DAY OR feedback=2)"""
        parameters = {"objet": args['objet']}
        element = await DataLayer.get_data_layer().execute_sql(
            query=query, parameters=parameters
        )
        try:
            if isinstance(element, list) and element:
                return element[0]
        except:
            return None

    @staticmethod
    async def get_explication(args: dict):
        # query = """SELECT * FROM cache_qui_signe WHERE "document" = :document AND "objet" = :objet AND created_date >= NOW() - INTERVAL '30' DAY"""
        # parameters = {"document": args['document'], "objet": args['objet']}
        query = """SELECT * FROM cache_qui_signe WHERE "direction" = :direction AND (created_date >= NOW() - INTERVAL '30' DAY OR feedback=2)"""
        parameters = {"direction": args['direction']}
        element = await DataLayer.get_data_layer().execute_sql(
            query=query, parameters=parameters
        )
        try:
            if isinstance(element, list) and element:
                return element[0]
        except:
            return None

    @staticmethod
    async def get_response(args: dict):
        columns = ['document', 'direction', 'objet', 'montant', 'montant_sup', 'comp']
        values = " AND ".join(f'"{key}" = :{key}' for key in columns)
        query = f"""SELECT * FROM cache_qui_signe WHERE {values} AND created_date >= NOW() - INTERVAL '30' DAY"""
        parameters = {k: args[k] for k in columns}
        direction = parameters['direction']
        parameters['direction'] = direction[0] if isinstance(direction, list) else direction
        element = await DataLayer.get_data_layer().execute_sql(
            query=query, parameters=parameters
        )
        try:
            if isinstance(element, list) and element:
                return element[0]['response']
        except Exception as e:
            return None

    @staticmethod
    async def count_response(args: dict):
        columns = ['document', 'direction', 'objet', 'montant', 'montant_sup', 'comp']
        values = " AND ".join(f'"{key}" = :{key}' for key in columns)

        query = f"""
            SELECT f."value", count(*) FROM cache_qui_signe c
    --         LEFT JOIN elements e on  e."id" = c."forId"
            LEFT JOIN steps s ON s."parentId" = c."forId"
            LEFT JOIN feedbacks f ON s."parentId" = f."forId"
            WHERE {values} AND created_date >= NOW() - INTERVAL '30' DAY
            GROUP BY f."value"
            """
        statistic = await DataLayer.datalayer.execute_sql(
            query=query, parameters=args
        )
        print(statistic)

        try:
            if isinstance(statistic, list) and statistic:
                feedback = {'1': 0, '2': 0, '0': 0}
                if statistic is not None:
                    for stat in statistic:
                        if stat['value'] == 0:
                            feedback['0'] = stat['count']
                        elif stat['value'] == 1:
                            feedback['1'] = stat['count']
                        else:
                            feedback['2'] += stat['count']
                return feedback
        except Exception as e:
            return None

    @staticmethod
    async def delete_response(thread_id: str, step_id: str) -> bool:
        query = """DELETE FROM cache_qui_signe WHERE "threadId" = :threadId AND "stepId" = :stepId"""
        parameters = {"threadId": thread_id, "stepId": step_id}
        await DataLayer.get_data_layer().execute_sql(query=query, parameters=parameters)
        return True

    @staticmethod
    async def update_element(element, user_id):
        import aiofiles
        import aiohttp

        if element.path:
            async with aiofiles.open(element.path, "rb") as f:
                content = await f.read()
        elif element.url:
            async with aiohttp.ClientSession() as session:
                async with session.get(element.url) as response:
                    if response.status == 200:
                        content = await response.read()
                    else:
                        content = None
        elif element.content:
            content = element.content
        else:
            raise ValueError("Element url, path or content must be provided")
        if content is None:
            raise ValueError("Content is None, cannot upload file")

        element_dict = element.to_dict()

        file_object_key = f"{user_id}/{element.id}" + (
            f"/{element.name}" if element.name else ""
        )

        element_dict["url"] = ''
        element_dict["objectKey"] = file_object_key

        element_dict_cleaned = {k: v for k, v in element_dict.items() if v is not None}
        if "props" in element_dict_cleaned:
            element_dict_cleaned["props"] = json.dumps(element_dict_cleaned["props"])

        placeholders = ", ".join(
            f'"{column}"=:{value}' for column, value in zip(element_dict_cleaned.keys(), element_dict_cleaned.keys()))

        query = f'UPDATE elements SET {placeholders} WHERE "id"=$1 AND "threadId"=$2'
        await DataLayer.get_data_layer().execute_sql(query=query, parameters=element_dict_cleaned)

    @staticmethod
    async def get_element(thread_id: str, element_id: str
                          ):

        query = """SELECT * FROM elements WHERE "threadId" = :thread_id AND "id" = :element_id"""
        parameters = {"thread_id": thread_id, "element_id": element_id}
        element = await DataLayer.get_data_layer().execute_sql(
            query=query, parameters=parameters
        )
        if isinstance(element, list) and element:
            element_dict = element[0]
            props = element_dict.get("props", "{}")
            return ElementDict(
                id=element_dict["id"],
                threadId=element_dict.get("threadId"),
                type=element_dict["type"],
                chainlitKey=element_dict.get("chainlitKey"),
                url=element_dict.get("url"),
                objectKey=element_dict.get("objectKey"),
                name=element_dict["name"],
                props=props if isinstance(props, dict) else json.loads(props),
                display=element_dict["display"],
                size=element_dict.get("size"),
                language=element_dict.get("language"),
                page=element_dict.get("page"),
                autoPlay=element_dict.get("autoPlay"),
                playerConfig=element_dict.get("playerConfig"),
                forId=element_dict.get("forId"),
                mime=element_dict.get("mime"),
            )
        else:
            return None

    @staticmethod
    async def update_messages(thread_id, msgs: Messages):
        # msgs = Messages(messages=messages)
        parameters = {"thread_id": thread_id, "messages": msgs.model_dump_json()}
        resp = await DataLayer.get_messages(thread_id)
        if resp is None:
            query = """INSERT INTO messages ("threadId", "messages") VALUES (:thread_id, :messages)"""
            await DataLayer.get_data_layer().execute_sql(query=query, parameters=parameters)
        else:
            query = '''UPDATE messages SET messages= :messages  WHERE "threadId"= :thread_id '''
            await DataLayer.get_data_layer().execute_sql(query=query, parameters=parameters)

    @staticmethod
    async def get_messages(thread_id: str):

        query = """SELECT * FROM messages WHERE "threadId" = :thread_id"""
        parameters = {"thread_id": thread_id}
        element = await DataLayer.get_data_layer().execute_sql(
            query=query, parameters=parameters
        )
        if isinstance(element, list) and element:
            messages_dict = element[0]
            messages = messages_dict.get("messages", "[{}]")
            msgs = Messages.model_validate(messages)
            return msgs.messages
        else:
            return None

