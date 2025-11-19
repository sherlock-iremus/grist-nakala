from dataclasses import dataclass, asdict
from rdflib import Graph, Namespace, DCTERMS, URIRef, XSD
from typing import Any


@dataclass
class Creator:
    authorId: str
    fullName: str
    givenname: str
    orcid: str
    surname: str


@dataclass
class MetadataType:
    lang: bool
    property_uri: URIRef
    qname: str
    type_uri: URIRef

    def __init__(self, lang: bool, property_uri: URIRef, type_uri: URIRef):
        self.lang = lang
        self.property_uri = property_uri
        self.type_uri = type_uri
        self.qname = g.qname(property_uri)


@dataclass
class MetadataValue:
    lang: str | None
    metadata_type: MetadataType
    value: str | URIRef | Creator

    def __init__(self, lang: str | None, metadata_type: MetadataType, value: str | URIRef | Creator):
        self.lang = lang
        self.metadata_type = metadata_type
        self.value = value

    def for_requests(self) -> dict[str, str | dict[str, str]]:
        if type(self.value) == Creator:
            value = asdict(self.value)
        else:
            value = str(self.value)

        x: dict[str, str | list[dict[str, Any]]] = {
            "propertyUri": str(self.metadata_type.property_uri),
            "typeUri": str(self.metadata_type.type_uri),
            "value": value
        }

        if self.lang and self.metadata_type.lang:
            x["lang"] = self.lang

        return x


NAKALA_METADATA_NS = Namespace("http://nakala.fr/terms#")
g = Graph()
g.bind("nakala", NAKALA_METADATA_NS)
g.bind("dcterms", DCTERMS)

METADATAS: list[MetadataType] = [
    MetadataType(False, DCTERMS.identifier, XSD.anyURI),
    MetadataType(False, NAKALA_METADATA_NS.created, XSD.string),
    MetadataType(False, NAKALA_METADATA_NS.creator, XSD.anyURI),
    MetadataType(False, NAKALA_METADATA_NS.license, XSD.string),
    MetadataType(True, NAKALA_METADATA_NS.title, XSD.string),
    MetadataType(False, NAKALA_METADATA_NS.type, XSD.anyURI),
]


def get_metadata_type_by_qname(qname: str) -> MetadataType:
    for x in METADATAS:
        if x.qname == qname:
            return x
    return MetadataType(False, URIRef(''), URIRef(''))
