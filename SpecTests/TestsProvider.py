import glob
import json
import re


class TestsProvider:
    tests_spec_path = "compiler/tests-spec/testData"
    tests_map_filename = "testsMap.json"

    def __init__(self, compiler_repo_path):
        self.compiler_repo_path = compiler_repo_path

    def get_tests_map(self):
        tests = {}

        for filename in glob.iglob(
                '%s/%s/**/linked/**/%s' % (self.compiler_repo_path, self.tests_spec_path, self.tests_map_filename),
                recursive=True):
            tests_map = json.loads(open(filename).read())

            for paragraph, paragraphTests in tests_map.items():
                for testType, testTypeTests in paragraphTests.items():
                    for sentence, sentenceTests in testTypeTests.items():
                        for testNumber, test in enumerate(sentenceTests):
                            full_path = filename.strip(self.tests_map_filename) +\
                                        "p-" + paragraph + "/" + testType + "/" + sentence + "." + str(testNumber + 1) + ".kt"
                            path = re.findall('(?<=linked/).*$', full_path)[0]
                            tests[path] = test["specVersion"]

        return tests
