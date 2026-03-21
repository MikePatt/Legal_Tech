import re
from dataclasses import dataclass


TOKEN_RE = re.compile(r"\w+")


@dataclass(frozen=True)
class TokenSpan:
    token: str
    start: int
    end: int


class InvertedIndex:
    def __init__(self, text: str) -> None:
        self.text = text
        self.tokens: list[TokenSpan] = []
        self.postings: dict[str, list[int]] = {}
        self._build()

    def _build(self) -> None:
        for i, match in enumerate(TOKEN_RE.finditer(self.text)):
            token = match.group(0).lower()
            span = TokenSpan(token=token, start=match.start(), end=match.end())
            self.tokens.append(span)
            self.postings.setdefault(token, []).append(i)

    def phrase_matches(self, query: str) -> list[tuple[int, int]]:
        query_tokens = [m.group(0).lower() for m in TOKEN_RE.finditer(query)]
        if not query_tokens:
            return []

        first_positions = self.postings.get(query_tokens[0], [])
        if not first_positions:
            return []

        matches: list[tuple[int, int]] = []
        query_len = len(query_tokens)
        token_count = len(self.tokens)

        for pos in first_positions:
            end_pos = pos + query_len - 1
            if end_pos >= token_count:
                continue
            ok = True
            for offset, q_token in enumerate(query_tokens):
                if self.tokens[pos + offset].token != q_token:
                    ok = False
                    break
            if ok:
                start = self.tokens[pos].start
                end = self.tokens[end_pos].end
                matches.append((start, end))
        return matches
