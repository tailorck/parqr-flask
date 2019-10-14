import spacy
import re

"""
Removes all punctuation and numbers from string before converting all upper
case characters to lower case
    
After installation you need to download a language model. 
python -m spacy download en

Verify all installed models are compatible with spaCy version
python -m spacy validate
"""


def spacy_clean(text):
    '''
    Cleans a string of text by:
        1. Removing all punctuations
        2. Stemming all words
        3. Decapitalize non-proper nouns
        4. Removing all pronouns

        After installation you need to download a language model.
        python -m spacy download en

        Verify all installed models are compatible with spaCy version
        python -m spacy validate
        :param text: input string
        :return: array of cleaned tokens
    '''
    #loading model
    nlp = spacy.load("en_core_web_sm")
    #creating a doc object by applying model to the text
    doc = nlp(text)
    return [token.lemma_ for token in doc if token.pos_ not in {"PUNCT", "PART", "PRON"}]

def main():
    string = ("When Sebastian Thrun started working on self-driving cars at "
              "Google in 2007, few people outside of the company took him "
              "seriously. “I can tell you very senior CEOs of major American "
              "car companies would shake my hand and turn away because I wasn’t "
              "worth talking to,” said Thrun, in an interview with Recode earlier "
              "this week.")
    print(clean_and_split(string))
    print(spacy_clean(string))

if __name__ == "__main__":
    main()
