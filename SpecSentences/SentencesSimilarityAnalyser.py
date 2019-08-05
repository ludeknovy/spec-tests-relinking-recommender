import spacy

from spacy.errors import ModelsWarning
import warnings
import sys

warnings.filterwarnings("ignore", category=ModelsWarning)
warnings.filterwarnings("ignore", category=UserWarning)


class SentencesSimilarityAnalyser:
    latest_spec_sentence_vectors = {}
    nlp = spacy.load("en_core_web_lg")
    similarities = {}

    def __init__(self, spec_info):
        (self.latest_spec_version, self.latest_spec_sentences) = spec_info

    @staticmethod
    def print_recommended_sentence_info(similarity, sentence_candidate_in_latest_spec):
        print("---> P (%.2f): %s" % (similarity, sentence_candidate_in_latest_spec))

    def compute_vectors_by_latest_spec(self):
        for path in self.latest_spec_sentences:
            for sentence in self.latest_spec_sentences[path]:
                if path not in self.latest_spec_sentence_vectors:
                    self.latest_spec_sentence_vectors[path] = []

                self.latest_spec_sentence_vectors[path].append(self.nlp(sentence))

    def print_comparison_results(self, spec_sentences_info, sentence_location):
        (sections_hierarchy, sentence_number) = sentence_location
        (spec_version, sentences) = spec_sentences_info

        sentence_index = sentence_number - 1

        print("------------------------------------------")

        print("\"%s\"" % (sections_hierarchy + "," + str(sentence_number)), file=sys.stderr)

        if sections_hierarchy in sentences and len(sentences[sections_hierarchy]) > sentence_number:
            print("---> E: " + sentences[sections_hierarchy][sentence_index])
        else:
            print("Invalid the spec version in the test (sentence not found in %s)" % spec_version, file=sys.stderr)
            return

        if sections_hierarchy in self.latest_spec_sentences and len(
                self.latest_spec_sentences[sections_hierarchy]) > sentence_number:
            print("---> A: " + self.latest_spec_sentences[sections_hierarchy][sentence_index])
        else:
            print("---> A: sentence not found in %s spec version" % self.latest_spec_version, file=sys.stderr)

    def search_most_similar_sentence(self, spec_sentences_info, sentence_location):
        (sections_hierarchy, sentence_number) = sentence_location
        (spec_version, sentences) = spec_sentences_info

        sentence_index = sentence_number - 1

        exist_in_spec_sentences = sections_hierarchy in sentences
        exist_in_latest_spec_sentences = sections_hierarchy in sentences

        if exist_in_spec_sentences and exist_in_latest_spec_sentences and len(sentences[sections_hierarchy]) > sentence_number and len(self.latest_spec_sentences[sections_hierarchy]) > sentence_number and sentences[sections_hierarchy][sentence_index] == self.latest_spec_sentences[sections_hierarchy][sentence_index]:
            return

        if exist_in_spec_sentences and exist_in_latest_spec_sentences and len(sentences[sections_hierarchy]) > sentence_number and len(self.latest_spec_sentences[sections_hierarchy]) > sentence_number and sentences[sections_hierarchy][sentence_index] != self.latest_spec_sentences[sections_hierarchy][sentence_index]:
            if not sections_hierarchy + "," + str(sentence_index) in self.similarities:
                search_doc = self.nlp(sentences[sections_hierarchy][sentence_index])
                max_similarity = (0, "")

                for path in self.latest_spec_sentences:
                    for index, sentence in enumerate(self.latest_spec_sentences[path]):

                        main_doc = self.latest_spec_sentence_vectors[path][index]

                        sim = search_doc.similarity(main_doc)
                        if sim > max_similarity[0]:
                            max_similarity = (sim, sentence)

                similarity = max_similarity[0]
                most_similar_sentence_in_latest_spec = max_similarity[1]
                self.similarities[sections_hierarchy + "," + str(sentence_index)] = max_similarity
            else:
                similarity_components = self.similarities[sections_hierarchy + "," + str(sentence_index)]
                similarity = similarity_components[0]
                most_similar_sentence_in_latest_spec = similarity_components[1]

            return similarity, most_similar_sentence_in_latest_spec
        else:
            return None
