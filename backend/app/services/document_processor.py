from pathlib import Path
from collections import Counter
import fitz


def extract_blocks_from_pdf(file_path: str) -> list[dict]:
    """
    Extract PDF text into logical blocks while preserving typography
    and layout metadata.

    A PDF block may contain multiple logical structures. We therefore
    process its lines individually and split when there is a strong
    formatting transition between lines.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    document = fitz.open(path)
    blocks = []

    try:
        for page_number, page in enumerate(document, start=1):
            data = page.get_text("dict")

            for pdf_block in data["blocks"]:
                if pdf_block.get("type") != 0:
                    continue

                lines = []

                for line in pdf_block.get("lines", []):
                    spans = []

                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()

                        if not text:
                            continue

                        font = span.get("font", "")
                        font_size = span.get("size", 0)
                        flags = span.get("flags", 0)
                        bbox = span.get("bbox")

                        is_bold = (
                            "BOLD" in font.upper()
                            or bool(flags & 16)
                        )

                        spans.append(
                            {
                                "text": text,
                                "font": font,
                                "font_size": font_size,
                                "is_bold": is_bold,
                                "bbox": bbox,
                            }
                        )

                    if spans:
                        lines.append(spans)

                if not lines:
                    continue

                current_lines = []
                current_spans = []
                previous_line_profile = None

                def get_line_profile(line_spans):
                    sizes = [
                        round(span["font_size"], 2)
                        for span in line_spans
                    ]

                    fonts = [
                        span["font"]
                        for span in line_spans
                    ]

                    bold_count = sum(
                        1
                        for span in line_spans
                        if span["is_bold"]
                    )

                    dominant_size = Counter(
                        sizes
                    ).most_common(1)[0][0]

                    dominant_font = Counter(
                        fonts
                    ).most_common(1)[0][0]

                    bold_ratio = (
                        bold_count / len(line_spans)
                        if line_spans
                        else 0.0
                    )

                    return {
                        "dominant_size": dominant_size,
                        "dominant_font": dominant_font,
                        "bold_ratio": bold_ratio,
                    }

                def is_strong_transition(
                    previous_profile,
                    current_profile,
                ):
                    if previous_profile is None:
                        return False

                    size_changed = (
                        previous_profile["dominant_size"]
                        != current_profile["dominant_size"]
                    )

                    font_changed = (
                        previous_profile["dominant_font"]
                        != current_profile["dominant_font"]
                    )

                    previous_bold = (
                        previous_profile["bold_ratio"] >= 0.5
                    )

                    current_bold = (
                        current_profile["bold_ratio"] >= 0.5
                    )

                    bold_changed = (
                        previous_bold != current_bold
                    )

                    # A font-size transition is the strongest
                    # structural signal.
                    if size_changed:
                        return True

                    # A font and bold transition together provide
                    # additional structural evidence.
                    if font_changed and bold_changed:
                        return True

                    return False

                def finalize_block():
                    if not current_spans:
                        return

                    text = "\n".join(
                        " ".join(
                            span["text"]
                            for span in line
                        )
                        for line in current_lines
                    ).strip()

                    if not text:
                        return

                    font_sizes = [
                        span["font_size"]
                        for span in current_spans
                    ]

                    fonts = [
                        span["font"]
                        for span in current_spans
                    ]

                    bold_flags = [
                        span["is_bold"]
                        for span in current_spans
                    ]

                    font_size_counter = Counter(
                        round(size, 2)
                        for size in font_sizes
                    )

                    font_counter = Counter(fonts)

                    dominant_font_size = (
                        font_size_counter.most_common(1)[0][0]
                        if font_size_counter
                        else None
                    )

                    dominant_font = (
                        font_counter.most_common(1)[0][0]
                        if font_counter
                        else None
                    )

                    bold_span_count = sum(
                        1 for flag in bold_flags if flag
                    )

                    total_span_count = len(bold_flags)

                    bold_span_ratio = (
                        bold_span_count / total_span_count
                        if total_span_count
                        else 0.0
                    )

                    unique_font_sizes = sorted(
                        set(
                            round(size, 2)
                            for size in font_sizes
                        )
                    )

                    unique_fonts = sorted(
                        set(fonts)
                    )

                    all_bboxes = [
                        span["bbox"]
                        for span in current_spans
                        if span["bbox"]
                    ]

                    bbox = None

                    if all_bboxes:
                        bbox = [
                            min(b[0] for b in all_bboxes),
                            min(b[1] for b in all_bboxes),
                            max(b[2] for b in all_bboxes),
                            max(b[3] for b in all_bboxes),
                        ]

                    blocks.append(
                        {
                            "page": page_number,
                            "block_number": len(blocks),
                            "bbox": bbox,
                            "text": text,
                            "block_type": 0,

                            # Layout metadata
                            "block_height": (
                                bbox[3] - bbox[1]
                                if bbox
                                else None
                            ),
                            "block_width": (
                                bbox[2] - bbox[0]
                                if bbox
                                else None
                            ),
                            "line_count": len(current_lines),

                            # Typography metadata
                            "fonts": fonts,
                            "font_sizes": font_sizes,
                            "is_bold": any(bold_flags),
                            "dominant_font": dominant_font,
                            "dominant_font_size": dominant_font_size,
                            "bold_span_ratio": round(
                                bold_span_ratio,
                                3,
                            ),
                            "unique_font_sizes": unique_font_sizes,
                            "unique_fonts": unique_fonts,
                            "mixed_formatting": (
                                len(unique_font_sizes) > 1
                                or len(unique_fonts) > 1
                                or (
                                    0 < bold_span_ratio < 1
                                )
                            ),
                            "span_count": total_span_count,
                        }
                    )

                for line in lines:
                    current_profile = get_line_profile(line)

                    if is_strong_transition(
                        previous_line_profile,
                        current_profile,
                    ):
                        finalize_block()

                        current_lines = []
                        current_spans = []

                    current_lines.append(line)
                    current_spans.extend(line)

                    previous_line_profile = current_profile

                finalize_block()

    finally:
        document.close()

    return blocks


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract plain text from a PDF using the structured block extractor.
    """

    blocks = extract_blocks_from_pdf(file_path)

    return "\n\n".join(
        block["text"]
        for block in blocks
    )