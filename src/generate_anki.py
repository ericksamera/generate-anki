#!/usr/bin/env python3
"""
Purpose: Generate a set of notes.
"""
__author__ = "Erick Samera"
__version__ = "0.5.0"
__comments__ = "It works ???"
# --------------------------------------------------
from argparse import (
    Namespace,
    ArgumentParser,
    ArgumentDefaultsHelpFormatter)
from pathlib import Path
# --------------------------------------------------
import spacy
from nltk.tokenize import sent_tokenize
import genanki
import random
import html
# --------------------------------------------------
nlp = spacy.load("en_core_sci_lg")
# --------------------------------------------------
def get_args() -> Namespace:
    """ Get command-line arguments """

    parser = ArgumentParser(
        #usage='%(prog)s',
        description="Generate a set of notes",
        epilog=f"v{__version__} : {__author__} | {__comments__}",
        formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        'input_path',
        type=Path,
        help="path of directory containing directories of notes")
    parser.add_argument(
        '-o',
        '--out',
        dest='output_path',
        metavar='DIR',
        type=Path,
        help="path of output dir # currently doesn't work")

    args = parser.parse_args()

    # parser errors and processing
    # --------------------------------------------------
    args.input_path = args.input_path.resolve()
    if args.output_path:
        args.output_path = args.output_path.resolve()

    return args
# --------------------------------------------------

def _generate_cloze(statement_arg: str, model_arg: genanki.Model=genanki.CLOZE_MODEL) -> str:
    statement_doc = nlp(statement_arg)

    cloze_txt: str = str(statement_doc)
    reduced_list = list(set([str(word) for word in statement_doc.ents]))
    for index, value in enumerate(reduced_list):
        cloze_index = index+1
        cloze_replace_text = '{{' + f'c{cloze_index}::{str(value)}' + '}}'
        cloze_txt = cloze_txt.replace(f' {str(value)}', f' {cloze_replace_text}')
    
    new_cloze_note = genanki.Note(
        model=model_arg,
        fields=[f'{html.escape(cloze_txt)}', ''])
    return new_cloze_note
def _preprocess_text(file_arg: Path) -> str:
    _common_punctuation = ' .?!,:;--[]{}()\'\"'
    newline_stripped_txt = ''.join([line.strip('\n') for line in file_arg.readlines()])
    alpha_numeric_filtered = ''.join(char for char in newline_stripped_txt if char.isalnum() or char in _common_punctuation).strip()
    return alpha_numeric_filtered
def main() -> None:
    """ Insert docstring here """

    args = get_args()

    directories_list: list = [f for f in args.input_path.iterdir() if f.is_dir()]
    for directory in directories_list:
        root_model_id = random.randrange(1 << 30, 1 << 31)
        root_deck_name = f'{directory.name}'
        root_deck = genanki.Deck(
                    root_model_id,
                    root_deck_name)
        
        subdecks_list: list = []
        for file in directory.glob('*.txt'):
            with open(file) as input_file:
                model_id = random.randrange(1 << 30, 1 << 31)
                anki_deck = genanki.Deck(
                    model_id,
                    f'{root_deck_name}::{file.stem}')

                statements_list: list = sent_tokenize(_preprocess_text(input_file))
                
                for statement in statements_list:
                    anki_deck.add_note(_generate_cloze(statement))
                subdecks_list.append(anki_deck)

        genanki.Package(subdecks_list).write_to_file(f'{directory.name}.apkg')
# --------------------------------------------------
if __name__ == '__main__':
    main()
