import json
import os
import chainlit as cl
import logfire
import dotenv
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from chainlit.element import ElementDict
import agents
import pdf
# from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from chainlit.types import ThreadDict
from storage import load_source, upload_source
from datalayer import DataLayer
from models import Messages

DataLayer()

datalayer = SQLAlchemyDataLayer(conninfo=os.environ.get("DATABASE_URL"), ssl_require=True, show_logger=True, storage_provider=pdf.storage)

@cl.data_layer
def get_data_layer():
    return datalayer

@cl.password_auth_callback
async def auth_callback(username: str, password: str):
    if username == 'admin' and password == 'kheopadmin':
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    return cl.User(
        identifier="metropole2", metadata={"role": "admin", "provider": "credentials"}
    )

dotenv.load_dotenv()
logfire.configure()

model = 'gpt-4o-mini'

@cl.set_starters
async def set_starters():
    questions = [
        "que signe anne marie atlan",
        "que signe anne marie atlan comme bon de commande",
        "que signe anne marie atlan en finance",
        "Qui signe les bon de commande pour superieur de 80000 euros pour ordinateur",
        "Qui signe les bon de commande pour tablette pour les ecoles",
        "Qui signe marchés à procédure adaptée pour 90000 euros pour des plantes",
        "Qui signe marchés à procédure adaptée pour 40000 euros",
        "qui signe les bdc a 25k pour Achat de matériel comptable",
        "Qui signe un bdc d'achat de lampadaire de rue pour 20000 euros ?",
    ]

    return [
        cl.Starter(
            label=value,
            message=value
        ) for value in questions
    ]

@cl.on_chat_start
async def on_start():
    # await agents.metropole_agent.run("Qui signe les bon de commande superieur a 80000 euros ordinateur")
    cl.user_session.set('test', [])

    cl.user_session.set('ElementSidebar', cl.ElementSidebar())

async def affichage():
    elements = cl.user_session.get('customElement', None)
    elements.props = cl.user_session.get('props')
    await DataLayer.update_element(elements, cl.user_session.get('id'))
    user_id = await get_data_layer()._get_user_id_by_thread(elements.thread_id)
    file_object_key = f"{user_id}/{elements.id}/Source"
    print(file_object_key)

    await elements.update()
    # upload_source(file_object_key, json.dumps(elements.props))
    return

@cl.on_message
async def main(message):
    mh = cl.user_session.get("message_history", [])

    async with agents.metropole_agent.run_stream(message.content, message_history=mh) as response:
        if not cl.user_session.get('quiSigne'):
            msg = cl.Message("", author="Assistant")

        final_msg_content = ""  # Variable pour stocker le message final
        async for rest in response.stream():
            if not cl.user_session.get('quiSigne'):
                await msg.stream_token(rest, True)
                final_msg_content += rest  # Stocker chaque token reçu
            print(rest, end='')
        if not cl.user_session.get('quiSigne'):
            await msg.update()

    if cl.user_session.get('quiSigne'):
        await affichage()
        tasks = cl.user_session.get('tasks')
        task_list = cl.user_session.get('task_list')
        tasks[-1].status = cl.TaskStatus.DONE
        task_list.status = "✅ Fin "
        await task_list.send()
    mh = cl.user_session.get("message_history", [])
    mh.extend(response.all_messages())
    cl.user_session.set("message_history", mh)
    cl.user_session.set('quiSigne', False)
    await DataLayer.update_messages(cl.context.session.thread_id, Messages(messages=mh))

    # json.dump(response.all_messages().decode('utf-8'),open('messages','w',encoding='utf-8'), indent=4)

@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    mh = await DataLayer.get_messages(thread['id'])
    cl.user_session.set("message_history", mh)
    for step in thread['elements']:
        if step['type'] == 'custom':
            res = await DataLayer.get_element(step['threadId'],step['id'])
            print(step)
            step['props'] = res['props']
            if 'feedback' in res['props'].keys():
                statistic = await DataLayer.count_response(step['props']['args'])
                step['props']['source'] = 'cached'
                step['props']['feedback'] = statistic
                print(statistic)

    json.dump(thread, open('output.json','w',encoding='utf-8'), indent=4)
    # print(json.dumps(thread, indent=4))