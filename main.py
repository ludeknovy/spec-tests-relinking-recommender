import re

from SpecTests.TestsProvider import TestsProvider
from SpecSentences.SpecSentencesStorage import SpecSentencesStorage
from SpecSentences.SentencesSimilarityAnalyser import SentencesSimilarityAnalyser

# pip3 install spacy
# python3 -m spacy download en_core_web_lg
# pip3 install lxml


compiler_repo_path = "/Users/victor.petukhov/IdeaProjects/kotlin-2"
test_provider = TestsProvider(compiler_repo_path)
tests = test_provider.get_tests_map()
sentences_storage = SpecSentencesStorage()
similarity_analyser = SentencesSimilarityAnalyser(sentences_storage.get_latest())
similarity_analyser.compute_vectors_by_latest_spec()

for test_path, spec_version in tests.items():
    spec_sentences = sentences_storage.get(spec_version)
    test_path_components = re.findall('^(.*?)/p-([1-9]\d*)/(pos|neg)/([1-9]\d*)\.([1-9]\d*)\.kt$', test_path)[0]
    paragraph_number = test_path_components[1]
    sections_path = test_path_components[0].replace("/", ",").lower() + "," + str(paragraph_number)
    sentence_number = int(test_path_components[3])
    sentence_location = (sections_path, sentence_number)
    spec_sentences_info = (spec_version, spec_sentences)

    similarity_analyser.print_comparison_results(spec_sentences_info, sentence_location)

    search_result = similarity_analyser.search_most_similar_sentence(spec_sentences_info, sentence_location)

    if search_result:
        (similarity, sentence) = search_result
        similarity_analyser.print_recommended_sentence_info(similarity, sentence)

