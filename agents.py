import json
import typing
import uuid

import chainlit as cl
import pydantic_ai
from pydantic_ai.messages import ModelRequest, ModelResponse

import models
import pdf
import prompt
import retreiver
import util
from prompt import directions_info
from pydantic_ai.messages import ModelResponse
import datetime
from  pydantic_ai.messages import TextPart
from retreiver import get_signataire, get_signataire_items
from datalayer import DataLayer

model = 'gpt-4o'
# mode = 'groq:llama-3.3-70b-versatile'
metropole_agent = pydantic_ai.Agent(
    model=model,
    system_prompt='''
Tu es un assistant expert en délégation de signature à la Métropole de Nice, chargé d’identifier la personne habilitée à signer un document donné.

« Qui signe ? » → si la question est de format qui signe {document} a {montant} pour {objet du document} + pramaetres en plus
« Que signe ? » → si la question est de format que signe {signataire} ou es-ce que {signataire} signe un {document}.
« Absence » → si la demande concerne qui signe en cas d'absence ou de conge.
« Specific Item » → si la demande concerne plus de detail sur que signe 
Si la question ne concerne pas la délégation de signature, redirige l’utilisateur vers une question pertinente sur les signataires.

Si le retour du tool est vide ne reponds pas

Utilise uniquement les informations fournies.
Ne jamais extrapoler ou deviner un signataire.
Utilise d'abords ton chat history comme reference sinon invoque un tool
    ''',
    result_type=str,
    result_tool_name='analyse_questions'
)

final_agent = pydantic_ai.Agent(
    model=model,
    system_prompt='''
        extraits les sources selon la requete de l'utilisateur
    ''',
    result_type=typing.List[models.DataModel],
)

explication_agent = pydantic_ai.Agent(
    model=model,
    system_prompt='''
🎯 **Agent d'Explication des Réponses** 🎯  

Tu es un assistant chargé d’expliquer pourquoi une direction, un item et un signataire ont été choisis pour répondre à une demande liée à la délégation de signature à la Métropole de Nice.  

## 📌 **Méthodologie d’Explication**  
1. **Pourquoi cette direction ?**  
   - Analyse de l’objet de la demande et de son domaine de compétence.  
   - Règles de répartition des responsabilités entre les directions.  

2. **Pourquoi cet item ?**  
   - Correspondance entre l’objet et les critères spécifiques de traitement.  
   - Vérification des seuils financiers et des conditions d’application.  

3. **Pourquoi ce signataire ?**  
   - Application des règles de délégation en fonction du montant et du type de document.  
   - Hiérarchie des signataires et critères de priorité.  

✅ **Explication claire et concise**  
✅ **Basé uniquement sur les règles et données disponibles**  
✅ **Si ambigu, proposer une clarification**  

🚀 **Objectif : Justifier chaque choix de manière rapide et transparente.**  

    ''',
    result_type=str,
    result_tool_name='result_explication'
)

retrive_agent = pydantic_ai.Agent(
    model=model,
    system_prompt='''
    🎯 **Agent de Recherche des Signataires** 🎯  

    Objectif : Identifier la ou les personnes habilitées à signer un document à la Métropole de Nice en fonction des règles de délégation de signature.  

    - **Analyse de la demande** et des critères (montant, type de document, direction).
    - **Filtrage par responsabilité** en fonction de la hiérarchie et des seuils de signature.
    - **Retour structuré** sous forme de liste avec :
      - **Signataire**
      - **Fonction**
      - **Email**
      - **Matricule**
      - **Document concerné**
      -**Direction dga**
      -**supplient**
    🚀 **Objectif : Donner une réponse fiable et détaillée sur les signataires autorisés.**
    ''',
    result_type=models.ListeRetrive,
    result_tool_name='result_retrive'
)

get_direction_agent = pydantic_ai.Agent(
    model=model,
    system_prompt=f'''
    🏛 **Assistant d’Orientation Administrative pour les Employés de la Métropole de Nice** 🏛

    Tu es un assistant intelligent conçu pour aider les **employés de la Métropole de Nice** à identifier la **direction et le service compétents** en fonction de la nature de leur demande. Ton objectif est de leur fournir une orientation claire et précise pour éviter toute erreur d’aiguillage.

    ---

    ### 📌 Analyse et Compréhension de la Demande
    1. **Identification du domaine** :
       - Analyser l’objet de la demande (ex. : plante, bâtiment, informatique…).
       - Déterminer la thématique et les compétences associées.

    2. **Détermination de la direction et du service compétents** :
       - Associer l’objet à la bonne direction en fonction des responsabilités.
       - Vérifier si un service spécifique est concerné.

    3. **Gestion des incertitudes** :
       - Si l’objet est ambigu, poser des **questions complémentaires** pour préciser la demande.
       - En cas de chevauchement possible entre plusieurs directions, proposer une **meilleure orientation**.

    Fournitures bureau:

    Crayons (graphite, de couleur), Marqueurs et surligneurs, Gommes et effaceurs, Taille  crayons, Correcteurs (liquide, ruban) ,Ramettes de papier (blanc, couleur) ,Blocs  notes et cahiers  ,Post  it et notes adhésives ,Enveloppes (diverses tailles) ,Agendas et calendriers ,Plannings ,Matériel de classement et d'organisation,Classeurs 
Chemises (cartonnées, plastiques)  ,Intercalaires ,Dossiers suspendus  ,Boîtes d'archives  ,Trieurs  ,Corbeilles à courrier ,Porte  documents  ,Petites fournitures
Agrafeuses et agrafes,Perforatrices,Trombones ,Élastiques  ,Ciseaux,Cutters  ,Règles,Calculatrices,Tampons encreurs et encre ,Pots à crayons 
Adhésifs et colles,Rubans adhésifs (scotch),Colle (en stick, liquide) Patafix  ,Imprimantes et cartouches d'encre ,Photocopieurs  ,Clés USB  
CD/DVD vierges ,Câbles (imprimante, réseau)  ,Souris et tapis de souris  Claviers  ,Mobilier,Bureaux  ,Chaises de bureau  ,Lampes de bureau  
Tableaux (blancs, en liège)  ,Porte  manteaux  ,Poubelles  ,Destructeurs de documents ,Fournitures diverses,Étiquettes autocollantes ,Cartes de visite  ,Badges  
Porte  badges  ,Reliures et spirales  ,Pochettes plastiques  ,Caisse ou coffre  fort 

    ---

    ### 📌 Réponse Structurée

    → **Direction concernée** :  
    → **Service concerné** :  
    → **Explication** :  
    - **Justification claire** du choix de la direction/service.  
    - **Réponse concise et fiable** pour éviter toute confusion.  

    ### 📌 Règles de Précision et de Fiabilité
    ✅ **Ne jamais inventer** d’informations.  
    ✅ Si plusieurs services sont possibles, poser des **questions précises**.  
    ✅ **Éviter les réponses vagues** et guider vers le **bon interlocuteur** directement.  

    🚀 **Objectif : Assurer une orientation rapide et efficace des employés vers la bonne direction dès leur première demande !**  
    ''',
    result_type=models.ListeResponse,
    result_tool_name='result_func'
)

analyse_question_agent = pydantic_ai.Agent(
    model=model,
    system_prompt=f'''
         -En utilisant la quesstion donner la reponse sous format :
         document, montant et un objet (optionel) toujours le donner au singulier
         -Voici quelques sigle pour t'aider dans le choix des documents:
             -mapa: marhces a procedure adaptes
             -bdc: bons de commande
             -pv: proces verbaux
             -moe: actes en qualité de maître d’œuvre (moe)
         -Il se peut que la question contienne des fautes d'orthographe (mama au lieu de mapa par exemple)
    ''',
    result_type=models.QuiSigneModel,
    result_tool_name='result_analyse_questions'
)

signataire_question_parser_agent = pydantic_ai.Agent(
    model=model,
    system_prompt=f'''
         trouve le nom complet du signataire mentionne dans la question.
         reponds que par le nom sans ponctuation ni commentaire.
         n'extrapole pas ou complete le nom.
         si il y a une theme metionne parmis :
            - en matière de finances et de commande publique
            - en matière d’administration générale dans son périmètre d’intervention
            - en matière de ressources humaines dans son périmètre d'intervention
            - en matière d'administration générale dans le cadre d’une astreinte
            - en matière financière et comptable dans son périmètre d’intervention

         prends le en consideration 
    ''',
    result_type=models.QueSigneModel,
)

signataire_finder_agent = pydantic_ai.Agent(
    model=model,
    system_prompt=f'''
         trouve le signataire le plus similaire a la question de l'utilisateur
    ''',
    result_type=models.Signataire,
)

def retrive_items(**kwargs):
    arguments = kwargs

    arguments = {
        'document': arguments['document']['document'],
        'montant': arguments['document']['montant'],
        'comp': arguments['document']['comp'],
        'direction': arguments['direction'][0],
    }
    if 'document' not in arguments.keys():
        raise Exception('Type de document non fournis ou incoherent')

    if 'montant' not in arguments.keys() and 'direction' not in arguments.keys():
        raise Exception('Veuillez fournir au moins un montant ou une direction')

    if 'montant' not in arguments.keys():
        arguments['montant'] = '0'
        arguments['comp'] = 'eq'

    if 'comp' not in arguments.keys():
        arguments['comp'] = 'eq'

    docs = retreiver.get_docs(arguments)
    sign = []
    metadata = []
    paths = []
    sources = {}
    for doc in docs:
        # if doc.score > 0.8:
            sources[doc.node.metadata['Signataire']] = {'metadata': {}, 'hash': []}

    for doc in docs:
        # if doc.score > 0.8:
            sources[doc.node.metadata['Signataire']]['metadata'] = doc.node.metadata
            sources[doc.node.metadata['Signataire']]['hash'].append(doc.node.hash)

    for k, v in sources.items():
        path = pdf.text_to_pdf(cl.user_session.get('id'), v['metadata'], v['hash'])
        v['metadata']['path'] = path
        pass

    docs = [v['metadata'] for v in sources.values()]

    return docs

def get_info(doc):
    suppleant = doc.get('Suppleant', [])
    if isinstance(suppleant, str):
        suppleant = suppleant.split(',')
    elif isinstance(suppleant, float):
        suppleant = []
    doc['Suppleant'] = suppleant

    if not isinstance(doc['information'], dict):
        doc['information'] = json.loads(doc['information'].replace("'", '"'))

    return doc

@metropole_agent.tool_plain
# @cl.step(name="analyser la question ...", type="rerank", show_input=False)
async def qui_signe(message):
    task_list = cl.TaskList()
    task_list.status = "🕐 En Cours..."

    # Analyse de la question pour déterminer l'objet
    task_name = ["Analyse De La Question",
                 "Extraction Metadata",
                 "Recherche De Direction",
                 "Racherche Du Service",
                 "Recherche Du Signataire",
                 "Preparation De La Reponse"
                 ]

    tasks = [cl.Task(title=name, status=cl.TaskStatus.RUNNING) for name in task_name]

    for task in tasks:
        await task_list.add_task(task)

    await task_list.send()
    doc = await analyse_question_agent.run(message)
    args = doc.data.to_dict()

    tasks[0].status = cl.TaskStatus.DONE
    await task_list.send()

    if (args['direction'] is None and args['objet'] is None):
        choice = await util.askChoice()
        if choice == 'direction':
            args['direction'] = await util.choiceDirection(
                "Votre question est incomplete, Vous devez fournir sois une direction sois un objet.\nQue voulez vous faire ?")
        if choice == 'objet':
            args['objet'] = await util.askDirection()


    tasks[1].status = cl.TaskStatus.DONE
    await task_list.send()

    elements = cl.CustomElement(name='Source', props={'sources': [], 'status': 'progress'})
    skeleton = cl.Message(content=" ", elements=[elements])
    await skeleton.send()

    cl.user_session.set('customElement', elements)
    cl.user_session.set('skeleton', skeleton)

    if args['direction'] is None:
        cached_data = await DataLayer.get_direction(args)
        if cached_data is not None:
            args['direction'] = cached_data['direction']
            args['explication'] = cached_data['response']['explication']
    else:
        cached_data = await DataLayer.get_explication(args)
        args['explication'] = cached_data['response']['explication']

    res = None
    if args['direction'] is None:
        res = await get_direction_agent.run(
            f"quel est la direction et service responsable sur {args['objet']} et donner une explication bien claire")
        res = res.data.to_dict()
        for liste in res['liste']:
            liste['direction'] = liste['direction'].value.lower()
        explication = "".join(
            [e['explication'] for e in res['liste']] if res['liste'] else ["Aucune direction/service identifié."])
        args['explication'] = explication
        args['direction'] = res['liste'][0]['direction']

    print(res)
    print(args)

    tasks[2].status = cl.TaskStatus.DONE
    tasks[3].status = cl.TaskStatus.DONE
    await task_list.send()


    props = await DataLayer.get_response(args)

    statistic = await DataLayer.count_response(args)
    print(statistic)
    if statistic is None:
        statistic = {'1': 0, '0': 0, '2': 0}


    statistic['2'] += 1

    # if props is None or statistic['0'] > statistic['1']:
    if True :
        retry = 0
        while True:
            docs = retrive_items(document=args, direction=[args['direction']])
            retry += 1
            if len(docs) > 0 or retry == 3:
                break

        props = {
            'sources': [get_info(doc) for doc in docs],
            'status': 'done',
            'question': message,
            'source': 'generated'
        }
    else:
        props['source'] = 'cached'


    props['feedback'] = statistic
    props['explication'] = args['explication']
    props['args'] = args
    tasks[4].status = cl.TaskStatus.DONE
    await task_list.send()
    # cl.user_session.set('elements', elements)
    cl.user_session.set('props', props)
    cl.user_session.set('quiSigne', True)
    cl.user_session.set('tasks', tasks)
    cl.user_session.set('task_list', task_list)

    mh = cl.user_session.get('message_history', [])
    mh.append(ModelResponse(
        parts=[
            TextPart(
                content=props if isinstance(props,str) else json.dumps(props),
                part_kind='text',
            )
        ],
        timestamp=datetime.datetime.now(),
        kind='response',
    ))
    cl.user_session.set('message_history',mh)
    args['type'] = 'qui_signe'
    await DataLayer.create_cache(cl.context.session.thread_id, skeleton.parent_id, args, props)
    return 'ne reponds pas'

@metropole_agent.tool_plain
async def que_signe(message):
    task_list = cl.TaskList()
    task_list.status = "🕐 En Cours..."


    # Analyse de la question pour déterminer l'objet
    task_name = ["Analyse De La Question",
                 "Extraction Metadata",
                 "Recherche Du Signataire",
                 "Recherche Des Items",
                 "Preparation De La Reponse"
                 ]

    tasks = [cl.Task(title=name, status=cl.TaskStatus.RUNNING) for name in task_name]

    for task in tasks:
        await task_list.add_task(task)

    await task_list.send()

    res = await signataire_question_parser_agent.run(message)
    metadata = res.data
    tasks[0].status = cl.TaskStatus.DONE
    await task_list.send()
    print(metadata)

    metadata = metadata.to_dict()

    if metadata['document'] is None and metadata['theme'] is None:
        actions = [cl.Action(name=theme.value, payload={"value": theme.value }, label=theme.value) for theme in models.ThemeTypeEnum]
        actions.append(cl.Action(name="tout", payload={"value": None }, label='Tous les themes'))
        res = await cl.AskActionMessage(
            content="Choisissez un theme: ",
            actions=actions,
        ).send()
        metadata['theme'] = None if res is None or res['payload']['value'] is None else [res['payload']['value']]
        print(metadata)

    elements = cl.CustomElement(name='Items', props={'items': [], 'status': 'progress'})
    skeleton = cl.Message(content=" ", elements=[elements])
    await skeleton.send()
    cl.user_session.set('customElement', elements)
    cl.user_session.set('skeleton', skeleton)

    docs = get_signataire(metadata['signataire'])
    tasks[1].status = cl.TaskStatus.DONE
    await task_list.send()
    print(docs)

    res = await signataire_finder_agent.run(f"""trouve le signataire {metadata['signataire']} dans la liste suivante:\n {docs}""")
    tasks[2].status = cl.TaskStatus.DONE
    await task_list.send()
    print(res.data)
    # return
    docs = get_signataire_items(res.data.signataire.lower(), metadata)
    tasks[3].status = cl.TaskStatus.DONE
    await task_list.send()
    print(docs)

    props = {'items': docs, 'status': 'done'}
    print("="*100)
    print(props)
    print("=" * 100)

    cl.user_session.set('props', props)
    cl.user_session.set('quiSigne', True)

    cl.user_session.set('tasks', tasks)
    cl.user_session.set('task_list', task_list)

    mh = cl.user_session.get('message_history', [])
    mh.append(ModelResponse(
        parts=[
            TextPart(
                content=json.dumps(docs),
                part_kind='text',
            )
        ],
        timestamp=datetime.datetime.now(),
        kind='response',
    ))
    cl.user_session.set('message_history', mh)
    return "ne reponds pas"

@metropole_agent.tool
async def absence(ctx, message):

    return [str(message) for message in cl.user_session.get('message_history', [])]

@metropole_agent.tool
async def specificItem(ctx, message):
    return [str(message) for message in cl.user_session.get('message_history', [])]