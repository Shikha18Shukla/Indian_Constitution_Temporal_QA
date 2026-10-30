"""Page-aware PDF loading and stable, provenance-preserving chunking for System B."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
from pathlib import Path
import re


DEFAULT_CONSTITUTION = Path("raw/constitution/Constitution_of_India_2024.pdf")
DEFAULT_AMENDMENTS_DIR = Path("raw/amendments")
CORPUS_SNAPSHOT_FORMAT = "sha256"
DEFAULT_CHUNK_SIZE = 1800
DEFAULT_CHUNK_OVERLAP = 200

ARTICLE_HEADING = re.compile(
    r"(?m)^\s*(?:\d+\[)?(?P<number>\d{1,3}[A-Z]?)\.\s+"
    r"(?P<title>[\s\S]{1,250}?)(?:—|–)"
)
STRUCTURAL_PAGE_HEADING = re.compile(r"^(?:PART|CHAPTER|SCHEDULE|APPENDIX|THE CONSTITUTION)\b", re.IGNORECASE)


@dataclass(frozen=True)
class DocumentPage:
    source_document: str
    source_type: str
    page_number: int
    page_text: str
    source_sha256: str


@dataclass(frozen=True)
class CorpusChunk:
    document_id: str
    chunk_id: str
    source_document: str
    source_type: str
    page_number: int
    article_number: str | None
    section_or_heading: str | None
    chunk_text: str
    corpus_snapshot: str
    source_locator: str

    def metadata(self) -> dict:
        return asdict(self)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_manifest(root: Path, constitution: Path, amendments_dir: Path) -> list[dict]:
    """Fingerprint all candidate source PDFs, including scanned/excluded files."""
    candidates = [constitution, *sorted(amendments_dir.glob("*.pdf"))]
    manifest = []
    for path in candidates:
        if not path.is_file():
            raise FileNotFoundError(f"Corpus source PDF not found: {path}")
        manifest.append({
            "source_document": path.resolve().relative_to(root.resolve()).as_posix(),
            "sha256": _sha256(path),
        })
    return manifest


def snapshot_id(manifest: list[dict]) -> str:
    content = "\n".join(f"{item['source_document']}\0{item['sha256']}" for item in manifest)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def load_pdf_pages(
    root: Path,
    constitution: Path = DEFAULT_CONSTITUTION,
    amendments_dir: Path = DEFAULT_AMENDMENTS_DIR,
) -> tuple[list[DocumentPage], list[dict], str]:
    """Extract page text from the fixed PDF sources; retain 1-based PDF page locators.

    The Constitution's cover, preface, abbreviation pages and table of contents
    (PDF pages 1–31) are excluded. Its preamble and operative text (page 32 onward)
    are included. Amendment PDFs include each page with extractable text.
    """
    try:
        import pymupdf
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is required to extract corpus PDFs; install requirements.txt") from exc

    manifest = source_manifest(root, constitution, amendments_dir)
    snapshot = snapshot_id(manifest)
    pages: list[DocumentPage] = []
    excluded: list[dict] = []
    paths = [constitution, *sorted(amendments_dir.glob("*.pdf"))]
    for path in paths:
        relative = path.resolve().relative_to(root.resolve()).as_posix()
        source_type = "constitution" if path.resolve() == constitution.resolve() else "amendment_act"
        source_hash = next(row["sha256"] for row in manifest if row["source_document"] == relative)
        doc = pymupdf.open(path)
        added = 0
        try:
            for page_index, page in enumerate(doc):
                page_number = page_index + 1
                if source_type == "constitution" and page_number < 32:
                    continue
                page_text = page.get_text("text")
                if not page_text.strip():
                    continue
                pages.append(DocumentPage(relative, source_type, page_number, page_text, source_hash))
                added += 1
        finally:
            doc.close()
        if not added:
            excluded.append({
                "source_document": relative,
                "reason": "No extractable text in any included PDF page; OCR is not performed.",
                "sha256": source_hash,
            })
    return pages, excluded, snapshot


def normalize_extracted_text(text: str) -> str:
    """Collapse PDF layout whitespace while preserving extracted words/punctuation."""
    return re.sub(r"\s+", " ", text).strip()


def _split_spans(text: str, chunk_size: int, overlap: int) -> list[tuple[int, int]]:
    spans = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            floor = start + chunk_size // 2
            boundary = max(text.rfind(". ", floor, end), text.rfind("; ", floor, end), text.rfind(" ", floor, end))
            if boundary > start:
                end = boundary + (1 if text[boundary] in ".;" else 0)
        if end <= start:
            end = min(start + chunk_size, len(text))
        spans.append((start, end))
        if end == len(text):
            break
        next_start = max(start + 1, end - overlap)
        # Do not begin the overlap halfway through a word.
        next_space = text.find(" ", next_start, min(next_start + 80, end))
        start = next_space + 1 if next_space >= 0 else next_start
    return spans


def chunk_pages(
    pages: list[DocumentPage],
    corpus_snapshot: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[CorpusChunk]:
    if chunk_size < 200 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Require chunk_size >= 200 and 0 <= overlap < chunk_size")
    chunks: list[CorpusChunk] = []
    current_article: tuple[str, str] | None = None
    for page in pages:
        text = normalize_extracted_text(page.page_text)
        if not text:
            continue
        if page.source_type != "constitution" or not 33 <= page.page_number <= 283:
            current_article = None
        headings = []
        # Article-number metadata is populated only from explicit Article headings
        # in the Constitution's main body. This avoids treating numbered material
        # in the TOC, amendment Acts, schedules, or appendices as an Article.
        if page.source_type == "constitution" and 33 <= page.page_number <= 283:
            for match in ARTICLE_HEADING.finditer(page.page_text):
                number = match.group("number")
                if int(re.match(r"\d+", number).group()) > 395:
                    continue
                start_offset = len(normalize_extracted_text(page.page_text[:match.start()]))
                title = normalize_extracted_text(match.group("title")).rstrip(" .")
                headings.append((start_offset, number, title))
        if headings:
            segments = []
            if headings[0][0] > 0:
                prior_number, prior_title = current_article or (None, None)
                if STRUCTURAL_PAGE_HEADING.match(text[:headings[0][0]].strip()):
                    prior_number, prior_title = None, None
                segments.append((0, headings[0][0], prior_number, prior_title))
            for position, heading in enumerate(headings):
                segment_end = headings[position + 1][0] if position + 1 < len(headings) else len(text)
                if segment_end > heading[0]:
                    segments.append((heading[0], segment_end, heading[1], heading[2]))
            current_article = (headings[-1][1], headings[-1][2])
        else:
            prior_number, prior_title = current_article or (None, None)
            if STRUCTURAL_PAGE_HEADING.match(text):
                prior_number, prior_title = None, None
                current_article = None
            segments = [(0, len(text), prior_number, prior_title)]

        ordinal = 0
        for segment_start, segment_end, article_number, section_or_heading in segments:
            segment_text = text[segment_start:segment_end]
            for local_start, local_end in _split_spans(segment_text, chunk_size, overlap):
                start, end = segment_start + local_start, segment_start + local_end
                chunk_text = text[start:end].strip()
                if not chunk_text:
                    continue
                locator = f"PDF page {page.page_number} (1-based), extracted character offsets {start}:{end}"
                identity = "\0".join((page.source_document, str(page.page_number), str(ordinal), chunk_text))
                chunk_id = "chunk-" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:24]
                document_id = "doc-" + hashlib.sha256(page.source_document.encode("utf-8")).hexdigest()[:24]
                chunks.append(CorpusChunk(
                    document_id=document_id,
                    chunk_id=chunk_id,
                    source_document=page.source_document,
                    source_type=page.source_type,
                    page_number=page.page_number,
                    article_number=article_number,
                    section_or_heading=section_or_heading,
                    chunk_text=chunk_text,
                    corpus_snapshot=corpus_snapshot,
                    source_locator=locator,
                ))
                ordinal += 1
    return chunks
