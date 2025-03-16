from typing import Literal, Any

import pydantic
import typing
import pandas as pd
import enum

from pandas.core.methods.to_dict import to_dict
from pydantic.main import IncEx
from pydantic_ai.messages import ModelMessage

df = pd.read_excel('bdd/document_type.xlsx', sheet_name="Sheet1")
document_types = df['document'].values

DocumentTypeEnum = enum.Enum("DocumentTypeEnum",
                             {item.upper().replace(" ", "_").replace("é", "e"): item for item in document_types})

df = pd.read_excel('bdd/dga.xlsx', sheet_name="Sheet1")
direction_types = df['Direction DGA'].values

DirectionTypeEnum = enum.Enum("DirectionTypeEnum",
                              {item.upper().replace(" ", "_").replace("é", "e").replace(",",""): item for item in direction_types})

df = pd.read_excel('bdd/themes.xlsx', sheet_name="Sheet1")
theme_types = df['Theme Title'].values

ThemeTypeEnum = enum.Enum("ThemeTypeEnum",
                              {item.upper().replace(" ", "_").replace("é", "e").replace(",",""): item for item in theme_types})

class Information(pydantic.BaseModel):
    civilite: str
    email: str
    fonction: typing.Optional[str]
    matricule: str
    nom: str
    prenom: str

    def to_dict(self):
        return self.model_dump()

class DataModel(pydantic.BaseModel):
    Numero: str
    Collectivite: str
    Direction_DGA: DirectionTypeEnum
    Signataire: str
    information: Information
    Suppleant: str
    Item_Text: str
    document: typing.List[str]
    montant_min: int
    montant_max: int
    operateur: str

    def to_dict(self):
        dic = self.model_dump()
        dic['Direction_DGA'] = self.Direction_DGA.value
        return dic

class Signe_Retrive(pydantic.BaseModel):
    signataire: str = pydantic.Field(..., description="Nom du signataire", example="Jean Dupont")
    fonction: str = pydantic.Field(..., description="Fonction du signataire", example="Directeur des Finances")
    email: str = pydantic.Field(..., description="Email professionnel du signataire", example="jean.dupont@metropole.fr")
    matricule: str = pydantic.Field(..., description="Matricule du signataire")
    doc: str = pydantic.Field(..., description="numero de document pour chaque signataire", example="2024-adm-nca")
    direction_dga: str = pydantic.Field(..., description="Direction concernée", example="Direction des Finances")
    supplient: str = pydantic.Field(..., description="supplient des signataire", )

class ListeRetrive(pydantic.BaseModel):
    liste: typing.List[Signe_Retrive] = pydantic.Field(..., description="Liste des signataires potentiels")

class Signataire(pydantic.BaseModel):
    signataire: str = pydantic.Field(..., description="nom et prenom complet du signataire tel que donner")
    civilite: str = pydantic.Field(..., description="civilite du signataire")
    email: str = pydantic.Field(..., description="email du signataire")
    fonction: str = pydantic.Field(..., description="fonction du signataire")
    # coordonnes: dict = pydantic.Field(..., description="coordonnes du signataire {civilite, email, fonction}")

class Messages(pydantic.BaseModel):
  messages: list[ModelMessage]

class ResponseModel(pydantic.BaseModel):
    direction: DirectionTypeEnum = pydantic.Field(..., description="Direction du service ou de la réponse", example="Nord")
    service: str = pydantic.Field(..., description="Nom du service concerné", example="Transport")
    explication: str = pydantic.Field(..., min_length=5, description="Explication détaillée de la réponse", example="Le service est opérationnel.")
    confidence: float = pydantic.Field(..., ge=0.0, le=1.0, description="Niveau de confiance entre 0 et 1", example=0.85)

    def model_dump(
        self,
        *,
        mode: Literal['json', 'python'] | str = 'python',
        include: IncEx | None = None,
        exclude: IncEx | None = None,
        context: Any | None = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool | Literal['none', 'warn', 'error'] = True,
        serialize_as_any: bool = False,
    ) -> dict[str, Any]:
        dic = super().model_dump()
        dic['direction'] = self.direction.value
        return dic

class ListeResponse(pydantic.BaseModel):
    liste: typing.List[ResponseModel] = pydantic.Field(..., description="Liste des réponses du service")

    def to_dict(self):
        return self.model_dump()
        # l = []
        # dic = {}
        # # for liste in self.liste:
        # #     l.append(liste.to_dict())
        # dic['liste'] = l
        # return dic

class QuiSigneModel(pydantic.BaseModel):
    document: DocumentTypeEnum = pydantic.Field(..., description="Type de document à signer, ex: 'bon de commande', 'contrat', etc.")
    fournitures: bool = pydantic.Field(..., description="si c'est des fournitures bureau mention")
    objet: typing.Optional[str] = pydantic.Field(..., description="Objet du document à signer, ex: 'chatbot', 'logiciel', etc. toujours au singulier" )
    montant: float = pydantic.Field(..., description="Montant mentionné ou montant minimum si un intervalle est mentionné, 0 si rien n'est mentionné")
    montant_sup: float = pydantic.Field(..., description="Montant superieur si interval, 0 sinon")
    comp: typing.Literal["sup", "inf", "eq", "entre"] = pydantic.Field(..., description=("Comparateur utilisé pour le montant :\n"
            "- 'sup' : supérieur à, plus de, minimum\n"
            "- 'inf' : inférieur à, moins de, maximum\n"
            "- 'eq' : la somme est mentionnée sans comparaison")
                                                                       )

    def to_dict(self):
        return {
            'document': self.document.value,
            # 'direction': self.direction.value if self.direction else None,
            'direction': None,
            'fournitures': self.fournitures,
            'objet': self.objet if self.objet else None,
            'montant': self.montant,
            'montant_sup': self.montant_sup,
            'comp': self.comp,
        }

class QueSigneModel(pydantic.BaseModel):
    signataire: str = pydantic.Field(..., description="nom du signataire mentionne")
    document: typing.Optional[DocumentTypeEnum] = pydantic.Field(..., description="Type de document à signer, ex: 'bon de commande', 'contrat', etc. si mentionne")
    themes: typing.Optional[typing.List[ThemeTypeEnum]] = pydantic.Field(..., description="theme du secteur d'operation si mentionnee")
    def model_dump(self, **kwargs):
        dic = to_dict()
        return dic

    def to_dict(self):
        return {
            'signataire': self.signataire,
            'document': None if self.document is None else self.document.value,
            'theme': None if self.themes is None else [theme.value for theme in self.themes],
        }

__all__ = [
    'Information',
    'DataModel',
    'Signe_Retrive',
    'ListeRetrive',
    'ResponseModel',
    'ListeResponse',
    'QuiSigneModel',
    'Messages'
]