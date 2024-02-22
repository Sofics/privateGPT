import re

from pydantic import BaseModel, Field

class ContextFilter(BaseModel):
    docs_ids: list[str] | None = Field(
        examples=[["c202d5e6-7b69-4869-81cc-dd574ee8ee11"]]
    )


def get_sofics_context_filter(prompt: str, ingest_service) -> ContextFilter:
    """Get a custom, efficient Sofics context filter based on keywords from given prompt."""
    # NOTE: checking everything lowercase except for capturing names
    lowered_prompt = prompt.lower()

    project_code = None
    match = re.search(r"(cpa|rpa|opa)\d{1,3}", lowered_prompt)
    if match:
        project_code = match.group(0)

    # Captures groups of capitalized words (important names / simply start of sentence):
    possible_names = re.findall(r"([A-Z]+[\d\w]*(?:\s*[A-Z]+[\d\w]*)*)", prompt)
    # Note adding space because for example IT also gave a match to "feasibility"
    lowered_possible_names = [f" {name.lower()}" for name in possible_names]
    if "sofics" in lowered_possible_names:
        lowered_possible_names.remove("sofics")  # resulted in many random spaces as relevant context
    # print(f"Possible important names: {lowered_possible_names}")

    confluence_keyword_dict = {
        # NOTE: put intentional spaces in front of keywords that could be part of another word
        "hiring": ["new employee", "new hire", "new colleague", "interview", "cv"],
        "ip follow-up": [" ip", "invention"],
        "lunch & learn": ["l&l", "lunch"],
        "office wiki": ["office", "building", "at work", "sofics"],  # TODO DN
        "samsung": ["samsung"],
        "sharknet help": ["sharknet"],
        "it admin": ["admin", "localadmin"],
        "labadmin": ["admin", " lab"],
        "technoadmin": ["admin", "techno"],
        "tooladmin": ["admin", "tool"],
        "wiki admin": ["admin"],
        "sofics r&d": ["r&d", "research", "development", "invention"],
        "pq pmg admin": [" esd", "powerqubic", "pq", "testchip", "ehc", "rcs", "smos"],
        "takecharge portfolio management": ["takecharge"],  # TODO BS / JVDB
        "phystar pmg": ["phystar"],
        # TODO Fix Nordic exports <-> OM (special char / ...?)
        # NOTE: big spaces are split up into main pages:
        "shark wiki esd design": [" esd", "testchip", "ehc", "rcs", "smos"],  # TODO  + keywords takecharge
        "shark wiki circuit design": ["analog", " io", "levelshift", "amplifier", "noise", "clock", "i/o", "ovt", "ldo", "circuit design", "lin", "can"],
        "shark wiki lab": ["lab", "equipment"],
        "shark wiki software & simulations": ["simulation", "program", "software", " tool", "teggy", "pyshark"],
        "shark wiki standards": ["standard", " iso", " iec", "hbm standard", "cdm standard"],
        "shark wiki prodedures and manuals": ["procedure", "the way to", "manual", "how to"],
        "business development bd": [" bd", "business", "nda"],
        "business development customers": ["correspondent", "customer"],
        "business development marketing": ["marketing", "blog", "promotion", "press"],
        "business development events": ["event", " boot", "conference"],
    }

    relevant_doc_ids = set()
    relevant_file_names = set()
    file_names_checked = set()
    docs = ingest_service.list_ingested()
    for doc in docs:
        file_name = doc.doc_metadata["file_name"]

        if file_name in relevant_file_names:
            # Note: very efficient for pdfs! - so you don't have to redo all checks for page (Doc)
            relevant_doc_ids.add(doc.doc_id)

        elif file_name not in file_names_checked:
            # Inspect this filename for the first time:
            lowered_file_name = file_name.lower()

            # Relevant if project_code is in the filename
            if project_code is not None and project_code.lower() in lowered_file_name:
                relevant_doc_ids.add(doc.doc_id)
                relevant_file_names.add(file_name)

            else:
                not_relevant_yet = True

                # if file_name is a known space, check if the file is relevant based on space keywords:
                for confluence_name, keywords in confluence_keyword_dict.items():
                    if confluence_name in lowered_file_name:
                        for keyword in keywords:
                            if keyword in lowered_prompt:
                                relevant_doc_ids.add(doc.doc_id)
                                relevant_file_names.add(file_name)
                                not_relevant_yet = False
                                break

                if not_relevant_yet:
                    # Relevant if file name contains a group of words that was capitalized in the prompt
                    if file_name not in relevant_file_names:
                        # Relevant if file name contains a capitalized group of words from the prompt
                        for name in lowered_possible_names:
                            if name in lowered_file_name:
                                relevant_doc_ids.add(doc.doc_id)
                                relevant_file_names.add(file_name)
                                break

            file_names_checked.add(file_name)

    print(f"Sofics ContextFilter - Relevant files: {relevant_file_names} (Document count: {len(relevant_doc_ids)})")

    return ContextFilter(docs_ids=list(relevant_doc_ids))



