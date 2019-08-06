import re
import sys

from heapq import heappush, nlargest, nsmallest, heapreplace
from SpecSentences.SentencesSimilarityAnalyser import SentencesSimilarityAnalyser
from SpecTests.TestsProvider import TestsProvider


class ApplyingRecommendedSentencesDialog:
    part_test_path_before_sections_regex = re.compile("^(?P<part_test_path>.*?/linked)(?P<remaining_path>.*?)$")
    answers = {}
    recommended_sentences = {}

    @staticmethod
    def print_recommended_sentence_info(most_similar_sentences, test_path_prefix, sentence_location):
        most_n_similar_sentences = nlargest(
            SentencesSimilarityAnalyser.recommended_sentences_number,
            most_similar_sentences,
            key=lambda t: t[0]
        )
        ApplyingRecommendedSentencesDialog.recommended_sentences[sentence_location] = most_n_similar_sentences
        for index, similarity_info in enumerate(most_n_similar_sentences):
            (similarity, new_test_path, sentence_candidate_in_latest_spec) = similarity_info
            print("–––> R{index} ({similarity:.6})".format(index=index + 1, similarity=similarity))
            print("        {sentence}".format(sentence=sentence_candidate_in_latest_spec))
            print("        ––> New path: {new_test_path}".format(new_test_path=test_path_prefix + new_test_path))

        print("––––––––––––––––––––––––––––––––––––––––––")
        print("A – apply the first recommendation, A{n} – apply n-th recommendation, S – skip, Q – quit.")
        print("Append ! if you want apply it only for current test.")

    @staticmethod
    def waiting_for_type(sentence_location, test_path_components, compiler_repo_path):
        (test_path_prefix, remaining_path) = test_path_components

        while True:
            if sentence_location in ApplyingRecommendedSentencesDialog.answers:
                answer = ApplyingRecommendedSentencesDialog.answers[sentence_location]
            else:
                print("Enter your answer: ")
                answer = sys.stdin.readline().rstrip('\n')[::-1]
            if answer == "A" or answer == "A!":
                new_test_path = ApplyingRecommendedSentencesDialog.recommended_sentences[sentence_location][0][1]
                test_path_full_prefix = compiler_repo_path + "/" + TestsProvider.tests_spec_path + "/" + test_path_prefix
                print(test_path_full_prefix + remaining_path)
                print(test_path_full_prefix + "/" + new_test_path)
                print("Applied!")

                if answer == "A":
                    ApplyingRecommendedSentencesDialog.answers[sentence_location] = answer
                break
            elif answer == "S" or answer == "S!":
                if answer == "S":
                    ApplyingRecommendedSentencesDialog.answers[sentence_location] = answer
                break
            elif answer == "Q":
                exit(0)
            else:
                regex = re.compile("A(?P<recommendation_number>[1–5])(?P<apply_to_only_current>!)?")
                applying_n_matches = regex.search(answer)
                if applying_n_matches:
                    recommendation_number = applying_n_matches.group("recommendation_number")
                    print("Applied {n}!".format(n=recommendation_number))
                    if not applying_n_matches.group("apply_to_only_current"):
                        ApplyingRecommendedSentencesDialog.answers[sentence_location] = answer
                    break
