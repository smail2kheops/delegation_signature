from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.core import load_index_from_storage
from llama_index.core.storage import StorageContext
from llama_index.core.vector_stores import (
    MetadataFilter,
    MetadataFilters,
    FilterOperator
)
from llama_index.embeddings.openai import OpenAIEmbedding

load_dotenv()

def load_index():
    embed_model = OpenAIEmbedding()
    Settings.embed_model=embed_model
    storage_context = StorageContext.from_defaults(persist_dir="store2")
    return load_index_from_storage(storage_context)

def load_signaitaire_index():
    embed_model = OpenAIEmbedding()
    Settings.embed_model=embed_model
    storage_context = StorageContext.from_defaults(persist_dir="signataire_store")
    return load_index_from_storage(storage_context)

def get_signataire(nom):
    docs = signataire_index.as_retriever(similarity_top_k=3).retrieve(nom)
    # docs = [{"signataire":doc.node.text, "coordonnees":doc.node.metadata} for doc in docs]
    docs = [doc.node.metadata['coordonees'].replace("{", f"'nom et prenom':'{doc.node.text}',") for doc in docs]
    return docs

def get_signataire_items(nom, metadata):
    # metadata = metadata.to_dict()
    filters = [
        MetadataFilter(key="Signataire", value=nom, operator=FilterOperator.IN),
    ]
    if metadata['document'] is not None:
        filters.append(MetadataFilter(key="Item Text", value=metadata['document'], operator=FilterOperator.CONTAINS))

    if metadata['theme'] is not None:
        filters.append(MetadataFilter(key="Theme Title", value=metadata['theme'], operator=FilterOperator.IN))

    # filters = []
    filters = MetadataFilters(filters=filters, )
    docs = index.as_retriever(similarity_top_k=100, filters=filters).retrieve(" ")
    # docs = [{"signataire":doc.node.text, "coordonnees":doc.node.metadata} for doc in docs]
    docs = [{'text':doc.node.text, 'theme':doc.node.metadata['Theme Title']} for doc in docs]
    return docs

def get_index():
    return index

def get_decret(doc):
    filter = MetadataFilters(
        filters=[
            MetadataFilter(key="Signataire", value=doc['Signataire'], operator=FilterOperator.EQ),
            MetadataFilter(key="Numero", value=doc['Numero'], operator=FilterOperator.EQ),
            MetadataFilter(key="Direction DGA", value=doc['Direction DGA'], operator=FilterOperator.EQ),
        ])

    retriever = index.as_retriever(similarity_top_k=100, filters=filter)
    return retriever.retrieve(doc['Signataire'])

def get_docs(arguments):
    filters = [
        MetadataFilter(key="Direction DGA", value=arguments['direction'], operator=FilterOperator.IN),
        MetadataFilter(key="Item Text", value=arguments['document'], operator=FilterOperator.CONTAINS)
    ]

    if arguments['montant'] not in ['0', ''] and arguments['comp'] in ['eq']:
        filters.extend(
            [
                MetadataFilter(key="montant_max", value=float(arguments['montant']), operator=FilterOperator.GTE),
                MetadataFilter(key="montant_min", value=float(arguments['montant']), operator=FilterOperator.LTE),
            ]
        )

    if arguments['montant'] not in ['0', ''] and arguments['comp'] in ['entre']:
        filters.extend(
            [
                MetadataFilter(key="montant_max", value=float(arguments['montant_max']), operator=FilterOperator.GTE),
                MetadataFilter(key="montant_min", value=float(arguments['montant_min']), operator=FilterOperator.LTE),
            ]
        )

    if arguments['comp'] in ['sup']:
        filters.extend(
            [
                MetadataFilter(key="montant_max", value=float(arguments['montant']), operator=FilterOperator.GTE),
                # MetadataFilter(key="montant_min", value=float(arguments['montant']), operator=FilterOperator.GTE),
            ]
        )

    if arguments['comp'] in ['inf']:
        filters.extend(
            [
                MetadataFilter(key="montant_max", value=float(arguments['montant']), operator=FilterOperator.GTE),
                MetadataFilter(key="montant_min", value=float(arguments['montant']), operator=FilterOperator.LTE),
            ]
        )

    price_filter = MetadataFilters(filters=filters, )
    retriever = index.as_retriever(similarity_top_k=100, filters=price_filter)
    return retriever.retrieve(arguments['document'])


print('Load Index')
index = None
index = load_index()
print(len(index.docstore.docs))
signataire_index = load_signaitaire_index()
print(len(signataire_index.docstore.docs))
print('Index Loaded')
