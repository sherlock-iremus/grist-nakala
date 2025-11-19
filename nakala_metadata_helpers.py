from dataclasses import asdict
from nakala_metadatas import get_metadata_type_by_qname, MetadataType, METADATAS, MetadataValue, Creator
from rdflib import URIRef


def grist_column_id_to_metadata_type(x: str) -> MetadataType:
    x = x.replace('__', ':')
    for mdt in METADATAS:
        if mdt.qname == x:
            return mdt
    return MetadataType(False, URIRef(''), URIRef(''))


def extract_required_metadata_from_grist_row(fields: dict[str, str]) -> list[MetadataValue]:
    required_metadata: list[MetadataValue] = []
    creator: Creator = Creator(authorId="", fullName="", givenname="", orcid="", surname="")

    for column_id in fields:
        if column_id.startswith('nakala__creator'):
            creator_column_id_parts = list(filter(lambda x: x, column_id.split('_')))
            property_local_name = creator_column_id_parts[-1]
            creator.__setattr__(property_local_name, fields[column_id])
            qname = ":".join(creator_column_id_parts[0:2])
        elif column_id.startswith('nakala__') or column_id.startswith('dcterms__'):
            qname = column_id.replace('__', ':')
            metadata_type: MetadataType | None = get_metadata_type_by_qname(qname)
            if metadata_type:
                required_metadata.append(MetadataValue('fr', metadata_type, str(fields[column_id])))

    creator_metadata_type: MetadataType = get_metadata_type_by_qname("nakala:creator")
    if creator_metadata_type:
        required_metadata.append(MetadataValue(None, creator_metadata_type, creator))

    return required_metadata
