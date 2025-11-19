SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
source $SCRIPT_DIR/../ENV
python3 $SCRIPT_DIR/../main.py \
    --files_dir /Users/amleth/repositories/mercure-galant-estampes \
    --nakala_api_base $NAKALA_API_BASE \
    --nakala_api_key $NAKALA_API_KEY \
    --grist_api_key $GRIST_API_KEY \
    --grist_base $GRIST_BASE \
    --grist_doc_id $GRIST_DOC_ID \
    --grist_table_id MG_Estampes \