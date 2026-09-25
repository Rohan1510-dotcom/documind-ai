from statistics import median


def build_document_profile(blocks: list[dict]) -> dict:
    """
    Build a formatting and layout profile from the document itself.
    """

    if not blocks:
        return {
            "body_font_size": None,
            "body_font": None,
            "median_block_gap": 0.0,
        }

    font_sizes = []
    fonts = []
    block_gaps = []

    for block in blocks:
        font_sizes.extend(block.get("font_sizes", []))
        fonts.extend(block.get("fonts", []))

    # Calculate vertical gaps between consecutive blocks
    # on the same page.
    previous_block = None

    for block in blocks:
        bbox = block.get("bbox")

        if (
            previous_block is not None
            and previous_block.get("page") == block.get("page")
        ):
            previous_bbox = previous_block.get("bbox")

            if previous_bbox and bbox:
                gap = bbox[1] - previous_bbox[3]

                if gap >= 0:
                    block_gaps.append(gap)

        previous_block = block

    if not font_sizes:
        return {
            "body_font_size": None,
            "body_font": None,
            "median_block_gap": (
                round(median(block_gaps), 2)
                if block_gaps
                else 0.0
            ),
        }

    body_font_size = median(font_sizes)

    font_counts = {}

    for font in fonts:
        font_counts[font] = font_counts.get(font, 0) + 1

    body_font = (
        max(font_counts, key=font_counts.get)
        if font_counts
        else None
    )

    median_block_gap = (
        median(block_gaps)
        if block_gaps
        else 0.0
    )

    return {
        "body_font_size": round(body_font_size, 2),
        "body_font": body_font,
        "median_block_gap": round(
            median_block_gap,
            2,
        ),
    }


def calculate_heading_strength(
    block: dict,
    profile: dict,
    previous_block: dict | None = None,
) -> float:
    """
    Calculate structural heading strength using typography,
    text length, and relative vertical spacing.
    """

    body_font_size = profile.get("body_font_size")

    if not body_font_size:
        return 0.0

    text = block.get("text", "").strip()

    if not text:
        return 0.0

    block_font_size = block.get(
        "dominant_font_size",
        body_font_size,
    )

    bold_ratio = block.get(
        "bold_span_ratio",
        0.0,
    )

    text_length = len(text)

    size_ratio = block_font_size / body_font_size

    score = 0.0

    # ---------------------------------------------------------
    # 1. Relative font size
    # ---------------------------------------------------------

    if size_ratio >= 1.5:
        score += 0.55

    elif size_ratio >= 1.3:
        score += 0.45

    elif size_ratio >= 1.15:
        score += 0.20

    # ---------------------------------------------------------
    # 2. Bold formatting
    # ---------------------------------------------------------

    if bold_ratio >= 0.9:
        score += 0.20

    elif bold_ratio >= 0.5:
        score += 0.08

    # ---------------------------------------------------------
    # 3. Short text supports heading interpretation
    # ---------------------------------------------------------

    if text_length <= 80:
        score += 0.10

    elif text_length <= 150:
        score += 0.05

    # ---------------------------------------------------------
    # 4. Vertical spacing
    # ---------------------------------------------------------

    median_gap = profile.get(
        "median_block_gap",
        0.0,
    )

    current_bbox = block.get("bbox")

    if (
        previous_block is not None
        and current_bbox
        and previous_block.get("bbox")
        and previous_block.get("page") == block.get("page")
        and median_gap > 0
    ):
        previous_bbox = previous_block["bbox"]

        gap = current_bbox[1] - previous_bbox[3]

        # The block has noticeably more vertical separation
        # than the document's normal block spacing.
        if gap >= median_gap * 1.5:
            score += 0.15

        elif gap >= median_gap * 1.2:
            score += 0.08

    # ---------------------------------------------------------
    # 5. Penalize very long text
    # ---------------------------------------------------------

    if text_length > 300:
        score -= 0.20

    elif text_length > 150:
        score -= 0.10

    return max(0.0, min(score, 1.0))


def classify_block(
    block: dict,
    profile: dict,
    previous_block: dict | None = None,
) -> dict:
    """
    Classify one document block.
    """

    text = block.get("text", "").strip()

    if not text:
        return {
            "text": "",
            "type": "empty",
            "confidence": 1.0,
        }

    # List markers are a strong structural signal.
    if text.startswith(("•", "-", "*")):
        return {
            "text": text,
            "type": "list_item",
            "confidence": 0.9,
        }

    heading_strength = calculate_heading_strength(
        block=block,
        profile=profile,
        previous_block=previous_block,
    )

    if heading_strength >= 0.70:
        block_type = "heading"

    elif heading_strength >= 0.50:
        block_type = "subheading"

    else:
        block_type = "paragraph"

    confidence = (
        0.9
        if block_type == "heading"
        else 0.75
        if block_type == "subheading"
        else 0.7
    )

    if len(text) > 150 and block_type != "heading":
        confidence = 0.9

    return {
        "text": text,
        "type": block_type,
        "confidence": round(
            max(
                confidence,
                heading_strength,
            ),
            2,
        ),
    }


def classify_document_blocks(
    blocks: list[dict],
) -> list[dict]:
    """
    Classify all document blocks using document-level
    formatting and layout context.
    """

    profile = build_document_profile(blocks)

    classified_blocks = []

    for index, block in enumerate(blocks):

        previous_block = (
            blocks[index - 1]
            if index > 0
            else None
        )

        classified = classify_block(
            block=block,
            profile=profile,
            previous_block=previous_block,
        )

        classified["page"] = block.get("page")
        classified["block_number"] = block.get(
            "block_number"
        )

        classified["heading_strength"] = round(
            calculate_heading_strength(
                block=block,
                profile=profile,
                previous_block=previous_block,
            ),
            2,
        )

        classified_blocks.append(classified)

    return classified_blocks