import pathlib
from collections import defaultdict, Counter
from datetime import date
from dateutil import parser
from typing import List, Dict, Set

import colored
import flask

WRONG = "dark_gray"
RIGHT_POS = "green"
WRONG_POS = "yellow"

COLOR_TO_EMOJI = {
    WRONG: '⬛',
    RIGHT_POS: '🟩',
    WRONG_POS: '🟨'
}
ALL_LETTERS = [chr(i + ord("a")) for i in range(26)]
LENGTH = 5


def get_words():
    import requests
    r = requests.get('https://www.nytimes.com/games/wordle/main.4d41d2be.js')
    words = [x for x in str(r.content).split(";") if 'robin' in x][0]
    return words.split("[")[1].split("]")[0].strip('"').split('","')


def get_wod(words, which_day=None):
    if not which_day:
        which_day = date.today()
    if type(which_day) == str:
        which_day = parser.parse(which_day).date()
    start_day = date(2021, 6, 19)
    word_ind = (len(words) + (which_day - start_day).days) % len(words)
    return words[word_ind]


class Output:
    @staticmethod
    def expand_lambda(v):
        LAMBDA = lambda: 0
        is_lambda = isinstance(v, type(LAMBDA)) and v.__name__ == LAMBDA.__name__
        if is_lambda:
            return v()
        else:
            return v

    def trace(self, *args):
        pass

    def debug_print(self, *args):
        pass

    def print(self, *args):
        pass

    def color_fn(self, col, text):
        return text


class StdOutput(Output):
    def debug_print(self, *args):
        self.print(*args)

    def print(self, *args):
        print(" ".join(Output.expand_lambda(v) for v in args))

    def color_fn(self, col, text):
        return colored.fg(col) + text + colored.attr('reset')


class HtmlOutput(Output):
    def __init__(self, debug):
        self._out = []
        self._debug = debug
        self._color_map = {
            WRONG: "gray",
            RIGHT_POS: "green",
            WRONG_POS: "yellow",
        }

    def debug_print(self, *args):
        if self._debug:
            self.print(*args)

    def print(self, *args):
        txt = " ".join(Output.expand_lambda(v) for v in args)
        txt = txt.replace(" ", "&nbsp;").replace("####SPACE####", " ").replace("\n", "<br>")
        txt = txt + "<br>"
        self._out.append(txt)

    def color_fn(self, col, text):
        return f'<span####SPACE####style="color:{self._color_map[col]}">{text}</span>'

    def get_html(self):
        body = "\n".join(self._out)
        out_txt = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        body {{
          font-family: 'Monaco', monospace;
          background-color: black;
          color:white
        }}
        </style>
        </head>
        <body>
        {body}        
        </body>
        </html>
        """
        return out_txt


class WordSpec:
    def __init__(self, word: str, match_res: List[str]):
        self.word = word
        self.match_res = match_res
        self.is_solved = set(match_res) == {RIGHT_POS}

    def debug_str(self, output: Output):
        res = "".join(
            [output.color_fn(m, ch) for m, ch in zip(self.match_res, self.word)]
        )
        res_without_chars = "".join(COLOR_TO_EMOJI[m] for m in self.match_res)
        return res, res_without_chars


class Checker:
    def __init__(self, correct_word):
        self.correct_word = correct_word

    def mode(self):
        return "bot"

    def match(self, word) -> List[str]:
        res = [WRONG for _ in self.correct_word]
        leftover_target = defaultdict(int)
        for i in range(len(self.correct_word)):
            if word[i] == self.correct_word[i]:
                res[i] = RIGHT_POS
            else:
                leftover_target[self.correct_word[i]] += 1
        for i in range(len(word)):
            if res[i] == RIGHT_POS:
                continue
            if leftover_target.get(word[i], 0) > 0:
                res[i] = WRONG_POS
                leftover_target[word[i]] -= 1
        return res

    def match_with_wordspec(self, word) -> "WordSpec":
        return WordSpec(word, self.match(word))


class Solver:
    def __init__(self, ro_word_cache: "WordCache", checker: Checker, output: Output):
        # options[i] = possible letters at position i
        self.options = [set(ALL_LETTERS).copy() for _ in range(LENGTH)]
        self.all_words = ro_word_cache.all_words.copy()
        # These characters dont exist in the word
        self.blocked_chars = set()
        # These characters exist in the word
        self.confirmed_chars = Counter()
        self.output = output
        self.checker = checker

    @staticmethod
    def remove_from_set(s: Set[str], c: str):
        if c in s:
            # debug_print(f"{s} - {c}")
            s.remove(c)

    def print_word_scores(self, feasile_words, word_scores):
        feasile_words = feasile_words if len(feasile_words) < 10 else feasile_words[:10] + ["..."]
        word_scores = word_scores if len(word_scores) < 10 else word_scores[:10] + [("...", "")]
        self.output.debug_print(lambda: ' ' * (LENGTH + 1) + ' '.join(feasile_words))
        self.output.debug_print(
            lambda: ' ' * (LENGTH + 1) + ' '.join([f'{w}->{s}' for w, s in word_scores]))

    def _options_str(self):
        return " ".join(["".join(sorted(x)) for x in self.options])

    def _confirmed_chars_str(self):
        return "".join(sorted(self.confirmed_chars.elements()))

    def _debug_info(self):
        self.output.trace("==========DEBUG INFO============")
        self.output.trace(f"options         -> {self._options_str()}")
        self.output.trace(f"blocked_chars   -> {self.blocked_chars}")
        self.output.trace(f"confirmed_chars -> {self._confirmed_chars_str()}")

    # Use the word spec and update the state
    def _update_char_info(self, w: WordSpec):
        # Confirmed chars based on this guess
        confirmed_chars_per_spec = Counter()
        for c, match in zip(w.word, w.match_res):
            if match in (WRONG_POS, RIGHT_POS):
                confirmed_chars_per_spec[c] += 1

        for ind, c, match in zip(range(len(w.word)), w.word, w.match_res):
            # debug_print(ind, c, match)
            if match == WRONG:
                Solver.remove_from_set(self.options[ind], c)
                # c does not exist in the word. Add it to blocked chars and remove from self.options
                # Note that if num_occurances(`c`, word) >= num_occurances(`c`, soln) then
                #  match(c) will be wrong atleast once. So dont remove c if its in
                #  confirmed_chars_per_spec
                #  E.g - soln=abcde guess=aaaaa => [RIGHT_POS, WRONG, WRONG, WRONG, WRONG]
                if c not in confirmed_chars_per_spec:
                    self.blocked_chars.add(c)
                    for i in range(LENGTH):
                        Solver.remove_from_set(self.options[i], c)
            elif match == WRONG_POS:
                Solver.remove_from_set(self.options[ind], c)
            elif match == RIGHT_POS:
                self.options[ind] = {c}
        for c, cnt in confirmed_chars_per_spec.items():
            self.confirmed_chars[c] = max(cnt, self.confirmed_chars[c])

    def _is_word_possible(self, word: str) -> bool:
        for c in word:
            if c in self.blocked_chars:
                return False
        chr_counter = Counter(word)
        for c, confirmed_cnt in self.confirmed_chars.items():
            if confirmed_cnt > chr_counter.get(c, 0):
                return False

        for i, c in enumerate(word):
            if c not in self.options[i]:
                return False
        return True

    def _score_all_words2(self, feasible_words) -> Dict[str, float]:
        freq = Counter()
        for w in feasible_words:
            for c in w:
                if c not in self.confirmed_chars:
                    freq[c] += 1
        ret = defaultdict(float)
        self.output.debug_print(
            lambda: " " * (LENGTH + 1)
                    + " ".join(
                [f"{k}{v}" for k, v in sorted(freq.items(), key=lambda x: -x[1])]
            )
        )
        for w in self.all_words:
            ret[w] = 1
            for c in set(w):  # score(abc) = score(aaabc)
                if c not in self.confirmed_chars:
                    ret[w] += freq[c]
            yellows_in_wrong_pos = set()
            for i, c in enumerate(w):
                if len(self.options[i]) == 1:
                    continue
                if c in self.confirmed_chars and c in self.options[i]:
                    yellows_in_wrong_pos.add(c)
            if sum(self.confirmed_chars.values()) > 3:
                yellow_guess_boost = 3 ** len(yellows_in_wrong_pos)
            else:
                yellow_guess_boost = 1.2 ** len(yellows_in_wrong_pos)
            ret[w] = ret[w] * yellow_guess_boost
        return ret

    def _score_all_words(self, feasible_words) -> Dict[str, float]:
        freq = Counter()
        for w in feasible_words:
            for c in w:
                if c not in self.confirmed_chars:
                    freq[c] += 1
        ret = defaultdict(float)
        self.output.debug_print(
            lambda: " " * (LENGTH + 1)
                    + " ".join(
                [f"{k}{v}" for k, v in sorted(freq.items(), key=lambda x: -x[1])]
            )
        )
        for w in self.all_words:
            ret[w] = 1
            for c in set(w):  # score(abc) score(aaabc)
                if c not in self.confirmed_chars:
                    ret[w] += freq[c]
            yellows_in_wrong_pos = set()
            for i, c in enumerate(w):
                if len(self.options[i]) == 1:
                    continue
                if c in self.confirmed_chars and c in self.options[i]:
                    yellows_in_wrong_pos.add(c)
            if sum(self.confirmed_chars.values()) > 3:
                yellow_guess_boost = 3 ** len(yellows_in_wrong_pos)
            else:
                yellow_guess_boost = 1.2 ** len(yellows_in_wrong_pos)
            ret[w] = ret[w] * yellow_guess_boost
        return ret

    def _find_possible_words(self) -> List[str]:
        return [w for w in self.all_words if self._is_word_possible(w)]

    def _next(self):
        feasible_words = self._find_possible_words()
        if len(feasible_words) == 1:
            self.output.debug_print("Only one")
            return feasible_words[0]
        all_word_scores = sorted(
            self._score_all_words(feasible_words).items(), key=lambda x: -x[-1]
        )
        if len(feasible_words) <= 3:
            all_word_scores = [
                (k, s) for k, s in all_word_scores if k in feasible_words
            ]
        self.print_word_scores(feasible_words, all_word_scores)
        if len(all_word_scores) == 0:
            return None
        return all_word_scores[0][0]

    def solve_next_word_for_cheat(self, guesses_so_far: List[str]):
        for g in guesses_so_far:
            spec = self.checker.match_with_wordspec(g)
            self._update_char_info(spec)
            a, b = spec.debug_str(self.output)
            self.output.print(
                lambda: f"{a} {self._options_str()}"
            )
            if spec.is_solved:
                return
        guess = self._next()
        if not guess:
            self.output.print(f"Failed to wordle the word")
            return
        self.output.print(guess)

    def solve(self):
        shareable_res = ""
        for i in range(20):
            guess = self._next()
            if not guess:
                self.output.print(f"Failed to wordle the word")
            self.all_words.remove(guess)
            spec = self.checker.match_with_wordspec(guess)
            self._update_char_info(spec)
            self._debug_info()
            a, b = spec.debug_str(self.output)
            self.output.print(
                lambda: f"{a} {self._options_str()}"
            )
            shareable_res += (b + "\n")
            if spec.is_solved:
                self.output.print(f"\n{i + 1} attempts by dotslash/wordle.py")
                self.output.print(shareable_res)
                return i + 1
        self.output.print(f"\nfailure")
        self.output.print(shareable_res)
        return 30


class WordCache:
    def __init__(self, word_list_path: pathlib.Path = None):
        # wordle word list (all of the size LENGTH)
        if word_list_path is not None:
            self.all_words_list = word_list_path.read_text().splitlines()
        else:
            self.all_words_list = get_words()
        self.all_words: Set[str] = set(
            w.strip() for w in self.all_words_list
        )


def default_word_list_path():
    pwd = str(pathlib.Path(__file__).parent.resolve())
    return pathlib.Path(f"{pwd}/wordle.txt")


cache = {}


def ensure_cache():
    if 'word_cache' not in cache:
        cache['word_cache'] = WordCache()


# https://cloud.google.com/functions/docs/first-python is a shame. I have to use flask 1.0
def solve_for_http_request(request):
    ensure_cache()
    word_cache = cache['word_cache']

    def parse_request():
        word = request.args.get("word")
        if not word and word != '_cheat':
            word = request.path.strip("/").split("/")[-1]
        if word == '_cheat':
            guess_date = request.args.get("date")
            word = get_wod(word_cache.all_words_list, which_day=guess_date)
        guesses = [w.strip()
                   for w in request.args.get("guesses", default="").split(",")
                   if w.strip()]
        return {
            'word': word,
            'guesses': guesses,
            'is_cheat': 'guesses' in request.args
        }

    def plain_text_response_400(mesage):
        resp = flask.make_response(mesage, 400)
        resp.content_type = 'text/plain'
        return resp

    parsed_rqst = parse_request()
    word, guesses, is_cheat = parsed_rqst['word'], parsed_rqst['guesses'], parsed_rqst['is_cheat']

    usage_string = (
        "\n"
        "usage: https://us-central1-booming-client-211100.cloudfunctions.net/wordle/<5_letter_word>"
    )
    if not word:
        return plain_text_response_400(f"bad request: word param missing{usage_string}")
    elif len(word) != LENGTH:
        return plain_text_response_400(
            f"bad request: word should have length {LENGTH}{usage_string}")
    elif word not in word_cache.all_words:
        return plain_text_response_400(f"bad request: word seems to invalid{usage_string}")
    checker = Checker(word)
    ho = HtmlOutput(debug=request.args.get("debug") == "true")
    s = Solver(ro_word_cache=word_cache, checker=checker, output=ho)
    if guesses or is_cheat:
        s.solve_next_word_for_cheat(guesses)
    else:
        s.solve()
    return ho.get_html()


def rate_algo():
    distribution = Counter()

    def print_distribution():
        print("=============")
        weighted_avg = sum(k * v for k, v in distribution.items()) / sum(
            distribution.values()
        )
        print(f"weighted_avg {weighted_avg}")
        print(sorted(distribution.items()))

    for i, w in enumerate(cache['word_dict'].all_words):
        if i % 100 == 1:
            print(f"==={i}===")
            print_distribution()
        s = Solver(ro_word_cache=cache['word_dict'], checker=Checker(w), output=Output())
        distribution[s.solve()] += 1
    print_distribution()


if __name__ == "__main__":
    import argparse

    dictionary_default_val = f'{pathlib.Path(__file__).parent}/wordle.txt'
    p = argparse.ArgumentParser("wordle_solver")
    p.add_argument("--mode", choices=["normal", "rate_algo", "local_server"],
                   default="normal",
                   help="(default: %(default)s)")
    p.add_argument("--dictionary", default=str(default_word_list_path()),
                   help="path to wordlist file (default: %(default)s)")
    p.add_argument("--word", help=f"{LENGTH} letter word to guess. Required in normal mode")
    args = p.parse_args()
    if args.mode == "rate_algo":
        rate_algo()
    elif args.mode == "normal":
        assert args.word and len(args.word) == LENGTH
        s = Solver(ro_word_cache=WordCache(pathlib.Path(args.dictionary)),
                   checker=Checker(args.word),
                   output=StdOutput()
                   )
        s.solve()
    elif args.mode == 'local_server':
        app = flask.Flask(__name__)


        @app.route("/<word>")
        def solve_wordle_for_word(word):
            return solve_for_http_request(flask.request)


        @app.route("/")
        def solve_wordle_for_word_no_args():
            return solve_for_http_request(flask.request)


        app.run(host="127.0.0.1", port=7865)
