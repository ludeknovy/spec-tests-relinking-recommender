import re

from SpecTests.TestsProvider import TestsProvider
from SpecSentences.SpecSentencesStorage import SpecSentencesStorage
from SpecSentences.SentencesSimilarityAnalyser import SentencesSimilarityAnalyser
from RecommendedApplying.ApplyingRecommendedSentencesDialog import ApplyingRecommendedSentencesDialog

# pip3 install spacy
# python3 -m spacy download en_core_web_lg
# pip3 install lxml
# pip3 install sortedcontainers

test_path_regex = re.compile("linked/(?P<sections>.*?)/p-(?P<paragraph>[1-9]\d*)/"
                             "(?P<test_type>pos|neg)/(?P<sentence_number>[1-9]\d*)\.(?P<test_number>[1-9]\d*)\.kt$")


def get_sentence_location(test_path):
    test_path_components = test_path_regex.search(test_path)
    paragraph_number = test_path_components.group("paragraph")
    sections_path = test_path_components.group("sections").replace("/", ",").lower() + "," + str(paragraph_number)
    sentence_number = int(test_path_components.group("sentence_number"))
    test_type = test_path_components.group("test_type")

    return sections_path, sentence_number, test_type


def analyze_test_files(tests):
    sentences_storage = SpecSentencesStorage()
    similarity_analyser = SentencesSimilarityAnalyser(sentences_storage.get_latest())

    similarity_analyser.compute_vectors_by_latest_spec()

    for test_path, spec_version in tests.items():
        sentence_location = get_sentence_location(test_path)
        spec_sentences_info = (spec_version, sentences_storage.get(spec_version))

        similarity_analyser.print_comparison_results(spec_sentences_info, sentence_location, test_path)

        search_result = similarity_analyser.search_most_similar_sentence(spec_sentences_info, sentence_location)

        if search_result:
            path_components =\
                ApplyingRecommendedSentencesDialog.part_test_path_before_sections_regex.search(test_path)

            test_path_prefix = path_components.group("part_test_path")
            remaining_path = path_components.group("remaining_path")
            ApplyingRecommendedSentencesDialog.print_recommended_sentence_info(search_result, test_path_prefix, sentence_location)
            ApplyingRecommendedSentencesDialog.waiting_for_type(sentence_location, (test_path_prefix, remaining_path), compiler_repo_path)


compiler_repo_path = "/Users/victor.petukhov/IdeaProjects/kotlin-2"
test_provider = TestsProvider(compiler_repo_path)

analyze_test_files(test_provider.get_tests_map())
