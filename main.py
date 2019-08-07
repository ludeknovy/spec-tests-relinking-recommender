import sys

from SpecTests.TestsProvider import TestsProvider
from SpecSentences.SpecSentencesStorage import SpecSentencesStorage
from SpecSentences.SentencesSimilarityAnalyser import SentencesSimilarityAnalyser
from RecommendedApplying.ApplyingRecommendedSentencesDialog import ApplyingRecommendedSentencesDialog

if len(sys.argv) < 2:
    print("Please, specify the Kotlin compiler repo path as a program argument.")
    exit()

compiler_repo_path = sys.argv[1]


def get_sentence_location(test_path_components):
    paragraph_number = test_path_components.group("paragraph_number")
    sections_path = test_path_components.group("sections").replace("/", ",").lower() + "," + str(paragraph_number)
    sentence_number = int(test_path_components.group("sentence_number"))
    test_type = test_path_components.group("test_type")

    return sections_path, sentence_number, test_type


def analyze_test_files(tests):
    sentences_storage = SpecSentencesStorage()
    (latest_spec_version, latest_spec) = sentences_storage.get_latest()
    recommended_applier = ApplyingRecommendedSentencesDialog(compiler_repo_path, latest_spec_version)
    similarity_analyser = SentencesSimilarityAnalyser((latest_spec_version, latest_spec))

    similarity_analyser.compute_vectors_by_latest_spec()

    for test_path, spec_version in tests.items():
        test_path_components = recommended_applier.test_path_regex.search(test_path)
        sentence_location = get_sentence_location(test_path_components=test_path_components)
        spec_sentences_info = (spec_version, sentences_storage.get(spec_version))

        similarity_analyser.print_comparison_results(spec_sentences_info, sentence_location, test_path)

        most_similar_sentences = similarity_analyser.search_most_similar_sentences(spec_sentences_info, sentence_location)

        if most_similar_sentences:
            path_components =\
                recommended_applier.part_test_path_before_sections_regex.search(test_path)

            test_path_prefix = path_components.group("part_test_path")
            remaining_path = path_components.group("remaining_path")
            (sections_path, sentence_number, _) = sentence_location

            recommended_applier.print_and_request_action_for_recommended_sentence(
                most_similar_sentences,
                (test_path_prefix, remaining_path, test_path_components.group("test_type")),
                (sections_path, sentence_number),
                spec_version
            )


analyze_test_files(
    tests=TestsProvider(compiler_repo_path).get_tests_map()
)
