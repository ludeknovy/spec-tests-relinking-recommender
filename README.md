# spec-tests-relinking-recommender

## Description

The tool is used for consistency control between the [Kotlin compiler spec tests](https://github.com/JetBrains/kotlin/tree/master/compiler/tests-spec/testData) and the [latest Kotlin specification](https://kotlin.github.io/kotlin-spec/) ([repo](https://github.com/JetBrains/kotlin-spec)).
It compares sentences, by which tests were written, to sentences from the latest Kotlin specification.
If these sentences aren't equals, then the tool recommends sentence from the latest Kotlin specification, into which the sentence from a previous specification was most likely transformed.

When you apply recommendation, the tool does following:
- actualizes spec version in the test file,
- move the test to the folder, that corresponds to the accepted sentence (if location is changed),
- change information about spec location in the test (if location is changed).

## Prepare to use

Before use you need install some python libraries:
- spacy: `pip3 install spacy` – NLP library; for similary sentences analysis;
- en_core_web_lg: `python3 -m spacy download en_core_web_lg` – CNN, pre-trained on English words; for spec sentences vectorization;
- lxml: `pip3 install lxml` – library for processing XML (used for parsing HTML version of the Kotlin specification)

## How to

To analyze the consistency of spec tests, you need to pass the path to the Kotlin repository as a program argument.

For example: `python3 main.py /Users/me/IdeaProjects/kotlin`.

