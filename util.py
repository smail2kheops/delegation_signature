import chainlit as cl
from models import DirectionTypeEnum

async def askChoice():
    while True:
        res = await cl.AskActionMessage(
            content="Votre question est incomplete, Vous devez fournir sois une direction sois un objet.\nQue voulez vous faire ?",
            actions=[
                cl.Action(name="direction", payload={"value": "direction"}, label="Donner une direction"),
                cl.Action(name="objet", payload={"value": "objet"}, label="Donner un objet"),
            ],
        ).send()

        if res:
            return res.get("payload").get("value")



    # await choiceDirection()

async def choiceDirection(message):
    while True:
        res = await cl.AskActionMessage(
            content=message,
            actions=[
                cl.Action(name="direction", payload={"value": member.value}, label=member.value)
                for member in (DirectionTypeEnum)
            ],
        ).send()

        if res:
            return res.get("payload").get("value")

async def askDirection():
    while True:
        res = await cl.AskUserMessage(
            content="Quel est l'objet de votre demande",
        ).send()

        if res:
            return res['output']