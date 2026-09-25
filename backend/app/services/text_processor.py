import re

from app.services.structure_service import classify_document_blocks


def clean_text(text: str) -> str:
    """
    Clean PDF-extracted text while preserving meaningful
    paragraph boundaries and repairing common line-break artifacts.
    """

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    text = re.sub(
        r"(\w)-\n(\w)",
        r"\1-\2",
        text,
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    text = re.sub(
        r"(?m)^[§ï]\s*$",
        "",
        text,
    )

    paragraphs = re.split(
        r"\n\s*\n",
        text,
    )

    cleaned_paragraphs = []

    for paragraph in paragraphs:
        lines = []

        for line in paragraph.splitlines():
            line = line.strip()

            if line:
                lines.append(line)

        if lines:
            cleaned_paragraphs.append(
                "\n".join(lines)
            )

    return "\n\n".join(
        cleaned_paragraphs
    ).strip()


def clean_block_text(text: str) -> str:
    """
    Clean text contained inside a structured PDF block.
    """

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    text = re.sub(
        r"(\w)-\n(\w)",
        r"\1-\2",
        text,
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    text = re.sub(
        r"(?m)^[§ï]\s*$",
        "",
        text,
    )

    lines = []

    for line in text.splitlines():
        line = line.strip()

        if line:
            lines.append(line)

    return "\n".join(lines).strip()


def split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences.
    """

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text.strip(),
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def split_long_text(
    text: str,
    chunk_size: int,
) -> list[str]:
    """
    Split long text while preserving sentence and word boundaries.
    """

    sentences = split_into_sentences(text)

    chunks = []
    current = ""

    for sentence in sentences:

        if len(sentence) > chunk_size:

            if current:
                chunks.append(
                    current.strip()
                )
                current = ""

            words = sentence.split()
            word_chunk = ""

            for word in words:

                candidate = (
                    f"{word_chunk} {word}"
                    if word_chunk
                    else word
                )

                if len(candidate) <= chunk_size:
                    word_chunk = candidate

                else:

                    if word_chunk:
                        chunks.append(
                            word_chunk.strip()
                        )

                    word_chunk = word

            if word_chunk:
                current = word_chunk

            continue

        candidate = (
            f"{current} {sentence}"
            if current
            else sentence
        )

        if len(candidate) <= chunk_size:
            current = candidate

        else:

            if current:
                chunks.append(
                    current.strip()
                )

            current = sentence

    if current:
        chunks.append(
            current.strip()
        )

    return chunks


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
) -> list[str]:
    """
    Plain-text fallback chunker.

    Used when structured PDF blocks are unavailable.
    """

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0"
        )

    if chunk_overlap < 0:
        raise ValueError(
            "chunk_overlap cannot be negative"
        )

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size"
        )

    cleaned_text = clean_text(text)

    if not cleaned_text:
        return []

    paragraphs = re.split(
        r"\n\s*\n",
        cleaned_text,
    )

    paragraphs = [
        paragraph.strip()
        for paragraph in paragraphs
        if paragraph.strip()
    ]

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:

        if len(paragraph) <= chunk_size:

            candidate = (
                f"{current_chunk}\n\n{paragraph}"
                if current_chunk
                else paragraph
            )

            if len(candidate) <= chunk_size:
                current_chunk = candidate

            else:

                if current_chunk:
                    chunks.append(
                        current_chunk.strip()
                    )

                current_chunk = paragraph

        else:

            if current_chunk:
                chunks.append(
                    current_chunk.strip()
                )

                current_chunk = ""

            chunks.extend(
                split_long_text(
                    paragraph,
                    chunk_size,
                )
            )

    if current_chunk:
        chunks.append(
            current_chunk.strip()
        )

    return chunks


# ============================================================
# SEMANTIC STRUCTURE
# ============================================================


def build_sections(
    blocks: list[dict],
) -> list[dict]:
    """
    Group structured PDF blocks into high-level sections.

    High-level headings are detected by the centralized
    structure classifier.
    """

    classified_blocks = classify_document_blocks(
        blocks
    )

    sections = []

    current_heading = None
    current_blocks = []

    for block in classified_blocks:

        text = clean_block_text(
            block.get("text", "")
        )

        if not text:
            continue

        block_type = block.get("type")

        if block_type in {
            "heading",
            "subheading",
        }:

            if current_heading is not None or current_blocks:
                sections.append(
                    {
                        "heading": current_heading,
                        "blocks": current_blocks.copy(),
                    }
                )

            current_heading = text
            current_blocks = []

        else:
            current_blocks.append(block)

    if current_heading is not None or current_blocks:
        sections.append(
            {
                "heading": current_heading,
                "blocks": current_blocks.copy(),
            }
        )

    return sections


def is_semantic_unit_title(
    blocks: list[dict],
    index: int,
) -> bool:
    """
    Detect whether a block is likely to be the title of a
    smaller semantic unit.

    This deliberately uses structural relationships rather
    than document-specific words.

    A standalone paragraph immediately followed by a list item
    is treated as a likely unit title.
    """

    if index >= len(blocks) - 1:
        return False

    block = blocks[index]
    next_block = blocks[index + 1]

    block_type = block.get("type")
    next_type = next_block.get("type")

    if block_type != "paragraph":
        return False

    if next_type != "list_item":
        return False

    text = clean_block_text(
        block.get("text", "")
    )

    if not text:
        return False

    # Avoid treating very large paragraphs as titles.
    if len(text) > 200:
        return False

    return True


def build_semantic_units(
    blocks: list[dict],
) -> list[dict]:
    """
    Group blocks into smaller semantic units inside a section.

    Example structure:

        title
        content
        content

        title
        content
        content

    The method does not depend on specific document types
    or section names.
    """

    units = []

    current_title = None
    current_blocks = []

    for index, block in enumerate(blocks):

        text = clean_block_text(
            block.get("text", "")
        )

        if not text:
            continue

        if is_semantic_unit_title(
            blocks,
            index,
        ):

            if current_title is not None or current_blocks:
                units.append(
                    {
                        "title": current_title,
                        "blocks": current_blocks.copy(),
                    }
                )

            current_title = text
            current_blocks = []

        else:
            current_blocks.append(block)

    if current_title is not None or current_blocks:
        units.append(
            {
                "title": current_title,
                "blocks": current_blocks.copy(),
            }
        )

    return units


def split_section(
    section_text: str,
    chunk_size: int,
) -> list[str]:
    """
    Split text only when it exceeds the configured
    chunk size.
    """

    if not section_text.strip():
        return []

    if len(section_text) <= chunk_size:
        return [
            section_text.strip()
        ]

    return split_long_text(
        section_text,
        chunk_size,
    )


def chunk_blocks(
    blocks: list[dict],
    chunk_size: int = 1000,
) -> list[dict]:
    """
    Create contextual semantic chunks from structured PDF blocks.

    Pipeline:

        PDF blocks
            ↓
        High-level sections
            ↓
        Semantic units
            ↓
        Contextual chunks
            ↓
        Embeddings
    """

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0"
        )

    if not blocks:
        return []

    sections = build_sections(
        blocks
    )

    chunks = []

    for section in sections:

        section_heading = section["heading"]
        section_blocks = section["blocks"]

        semantic_units = build_semantic_units(
            section_blocks
        )

        for unit in semantic_units:

            unit_title = unit["title"]
            unit_blocks = unit["blocks"]

            content_parts = []

            for block in unit_blocks:

                text = clean_block_text(
                    block.get("text", "")
                )

                if text:
                    content_parts.append(
                        text
                    )

            content = "\n\n".join(
                content_parts
            ).strip()

            # Build contextual text.
            context_parts = []

            if section_heading:
                context_parts.append(
                    f"Section: {section_heading}"
                )

            if unit_title:
                context_parts.append(
                    f"Topic: {unit_title}"
                )

            if content:
                context_parts.append(
                    content
                )

            section_text = "\n\n".join(
                context_parts
            ).strip()

            if not section_text:
                continue

            section_chunks = split_section(
                section_text=section_text,
                chunk_size=chunk_size,
            )

            for chunk in section_chunks:

                chunks.append(
                    {
                        "content": chunk,
                        "blocks": unit_blocks.copy(),
                        "page_start": (
                            unit_blocks[0]["page"]
                            if unit_blocks
                            else None
                        ),
                        "page_end": (
                            unit_blocks[-1]["page"]
                            if unit_blocks
                            else None
                        ),
                    }
                )

    return chunks