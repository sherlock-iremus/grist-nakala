import json
from pprint import pprint
import argparse
from grist_api_helpers import records, patch_record, post_attachment
from nakala_api import post_datas_uploads, get_users_me, post_datas, empty_collection, put_metadatas
from pathlib import Path
import sys
from nakala_metadatas import Creator, MetadataValue, get_metadata_type_by_qname
from nakala_metadata_helpers import extract_required_metadata_from_grist_row

####################################################################################################
# SETUP
####################################################################################################

parser = argparse.ArgumentParser()

# Files
parser.add_argument("--files_dir")

# Nakala
parser.add_argument("--nakala_api_base")
parser.add_argument("--nakala_api_key")

# Grist
parser.add_argument("--grist_api_key")
parser.add_argument("--grist_base")
parser.add_argument("--grist_doc_id")
parser.add_argument("--grist_table_id")

args = parser.parse_args()


####################################################################################################
# INDEX ALL EXISTING FILES BY NAME
####################################################################################################

directory = Path(args.files_dir)
filespaths = [str(f.resolve()) for f in directory.iterdir() if f.is_file()]
allfiles = {}
for f in filespaths:
    allfiles[Path(f).name] = {"path": f}

####################################################################################################
# FETCH ALL GRIST DATA
####################################################################################################

grist_data = records(args.grist_base, args.grist_api_key, args.grist_doc_id, args.grist_table_id)
pc = 0
i = 0

for row in grist_data["records"]:
    # Init loop stuff
    i += 1
    bug = False
    print("-" * 111)

    # SHERLOCK data
    business_id = str(row["fields"]["E42_business_id"])
    nakala_doi = row["fields"]["E42_nakala_doi"]
    nakala_doi_only = nakala_doi.replace("https://nakala.fr/", "").replace("/", "%2F")
    filenames = [x.strip() for x in str(row["fields"]["filenames"]).split(",")] if "filenames" in row["fields"] else None
    sherlock_uuid = row["fields"]["UUID"]

    if not sherlock_uuid or len(filenames) == 0:
        continue

    print("💬", f"{round(i / len(grist_data["records"]) * 100, 2)}% ", "🆔", business_id, sherlock_uuid)

    if bug:
        continue

    if nakala_doi:
        print("✅", business_id, "=>", nakala_doi)
    else:
        ############################################################################################
        # WHICH FILES SHOULD BE UPLOADED WITH THE DATA?
        ############################################################################################

        filepaths = []

        for filename in filenames:
            try:
                filedata = allfiles[filename]
                filepaths.append(filedata["path"])
            except:
                print(f"❌ Non existing file in {directory}: {filename}")
                bug = True

        if bug:
            continue

        ############################################################################################
        # UPLOAD FILES
        ############################################################################################

        files = []

        for filepath in sorted(filepaths):
            print(f"💬 Uploading file: {filepath}")
            r = post_datas_uploads(args.nakala_api_base, args.nakala_api_key, filepath)
            files.append(r)
            print("✅ /datas/uploads =>", r)

        ############################################################################################
        # POST DATA
        ############################################################################################

        r = post_datas(args.nakala_api_base, args.nakala_api_key, files, sherlock_uuid, business_id)
        print("✅ /datas =>", r)
        nakala_doi = r["payload"]["id"]
        print("✅", f"https://nakala.fr/{nakala_doi}")

        ############################################################################################
        # STORE NAKALA DOI IN GRIST
        ############################################################################################

        patch_record(
            args.grist_base,
            args.grist_api_key,
            args.grist_doc_id,
            args.grist_table_id,
            {"records": [{"require": {"E42_business_id": row["fields"]["E42_business_id"]}, "fields": {"E42_nakala_doi": f"https://nakala.fr/{nakala_doi}"}}]}
        )

    ################################################################################################
    # METADATAS
    ################################################################################################

    required_metadata = extract_required_metadata_from_grist_row(row["fields"])
    put_metadatas(args.nakala_api_base, args.nakala_api_key, nakala_doi_only, [x.for_requests() for x in required_metadata])

    ################################################################################################
    # COLLECTION
    ################################################################################################

    # empty_collection(args.nakala_api_base, args.nakala_api_key, args.nakala_collection_doi)
