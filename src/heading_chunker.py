from __future__ import annotations

import re

from .chunking import RecursiveChunker


class HeadingSectionChunker:
    """Split policy text on Markdown/heading boundaries, then size-limit sections.

    Designed for e-commerce policy docs structured as numbered sections or
    Markdown headings. Oversized sections are further split with RecursiveChunker
    and each fragment is prefixed with the section title for context.
    """

    HEADING_RE = re.compile(
        r"(?m)^(?:#{1,6}\s+.+|[0-9]+(?:\.[0-9]+)*\.?\s+[A-ZÀ-Ỵ].+)$"
    )

    def __init__(self, max_chars: int = 800) -> None:
        self.max_chars = max(100, max_chars)
        self._fallback = RecursiveChunker(chunk_size=self.max_chars)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        sections = self._split_sections(text)
        chunks: list[str] = []
        for title, body in sections:
            section_text = f"{title}\n\n{body}".strip() if title else body.strip()
            if not section_text:
                continue
            if len(section_text) <= self.max_chars:
                chunks.append(section_text)
                continue
            for piece in self._fallback.chunk(body if body.strip() else section_text):
                if title and not piece.lstrip().startswith(title[: min(20, len(title))]):
                    chunks.append(f"{title}\n\n{piece}".strip())
                else:
                    chunks.append(piece.strip())
        return [c for c in chunks if c]

    def _split_sections(self, text: str) -> list[tuple[str, str]]:
        matches = list(self.HEADING_RE.finditer(text))
        if not matches:
            return [("", text.strip())]

        sections: list[tuple[str, str]] = []
        if matches[0].start() > 0:
            preamble = text[: matches[0].start()].strip()
            if preamble:
                sections.append(("", preamble))

        for index, match in enumerate(matches):
            title = match.group(0).strip()
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            sections.append((title, body))
        return sections
