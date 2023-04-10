import spacy
# Download the model so that importing it will work
# see https://stackoverflow.com/a/47297686/4306257
spacy.cli.download("en_core_web_sm")

# Patch import
from .patch.patch_spacy_tags import TAG_MAP
__all__ = ["TAG_MAP"]  # make the linter happy (unused import), this is a patch because of framework conflicts
