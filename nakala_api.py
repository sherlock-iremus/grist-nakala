from datetime import datetime
import json
import requests

requests.packages.urllib3.disable_warnings()
session = requests.Session()
session.verify = False


def post_datas_uploads(api_base: str, api_key: str, file: str):
    with open(file, "rb") as f:
        return session.post(
            url=f"https://{api_base}/datas/uploads",
            headers={"accept": "application/json", "X-API-KEY": api_key},
            files={"file": f},
        ).json()


def get_users_me(api_base: str, api_key: str):
    return session.get(
        url=f"https://{api_base}/users/me",
        headers={"accept": "application/json", "X-API-KEY": api_key}
    ).json()


def get_metadatas(api_base: str, api_key: str, identifier: str):
    r = session.get(
        url=f"https://{api_base}/datas/{identifier}/metadatas?metadata-format=qdc",
        headers={"accept": "application/json", "X-API-KEY": api_key, "Content-Type": "application/json"}
    )
    r.raise_for_status()
    return r.json()


def put_metadatas(api_base: str, api_key: str, identifier: str, metadatas: list[dict[str, str]]):
    url = f"https://{api_base}/datas/{identifier}"
    data = {
        "metas": metadatas
    }
    try:
        r = session.put(
            url=url,
            headers={"accept": "application/json", "X-API-KEY": api_key, "Content-Type": "application/json"},
            data=json.dumps(data)
        )
        r.raise_for_status()
        return r
    except requests.exceptions.RequestException as err:
        print("❌", url, json.dumps(err.response.json(), indent=4))


def post_datas(api_base: str, api_key: str, files: str, sherlock_uuid: str, title: str):
    # https://documentation.huma-num.fr/nakala-guide-de-description/#fonctionnement-des-proprietes-nakala-obligatoires
    data = {
        # "collectionsIds": [collectionId],
        "files": files,
        "status": "published",
        "metas": [
            {
                "value": title,
                "propertyUri": "http://nakala.fr/terms#title",
                "typeUri": "http://www.w3.org/2001/XMLSchema#string"
            },
            {
                "propertyUri": "http://nakala.fr/terms#type",
                "value": "http://purl.org/coar/resource_type/c_c513",
                "typeUri": "http://www.w3.org/2001/XMLSchema#anyURI"
            },
            {
                "propertyUri": "http://purl.org/dc/terms/identifier",
                "value": f"http://data-iremus.huma-num.fr/id/{sherlock_uuid}",
                "typeUri": "http://www.w3.org/2001/XMLSchema#anyURI"
            },
            {
                "propertyUri": "http://nakala.fr/terms#creator",
                "value": None,
                "typeUri": "http://www.w3.org/2001/XMLSchema#anyURI"
            },
            {
                "value": datetime.now().strftime("%Y-%m-%d"),
                "propertyUri": "http://nakala.fr/terms#created",
                "typeUri": "http://www.w3.org/2001/XMLSchema#string"
            },
            {
                "value": "PDM",  # licence code : https://apitest.nakala.fr/vocabularies/licenses
                "propertyUri": "http://nakala.fr/terms#license",
                "typeUri": "http://www.w3.org/2001/XMLSchema#string"
            }
        ]
    }
    try:
        r = session.post(
            url=f"https://{api_base}/datas",
            headers={"accept": "application/json", "X-API-KEY": api_key, "Content-Type": "application/json"},
            data=json.dumps(data)
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as err:
        print("❌", json.dumps(err.response.json(), indent=4))


def empty_collection(base: str, api_key: str, collection_id: str):
    page = 1
    r = session.get(
        f"{base}/collections/{collection_id}/datas?page={page}&limit=25",
        headers={"accept": "application/json", "X-API-KEY": api_key, "Content-Type": "application/json"}
    )
    # r.json()["data"]
