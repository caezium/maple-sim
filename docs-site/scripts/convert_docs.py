import re
import shutil
import json
from pathlib import Path

SRC_ROOT = Path("docs")
DST_ROOT = Path("docs-site/content")

ADMONITION_RE = re.compile(
    r'^(?P<indent>\s*)(?P<marker>\?\?\?|!!!)\s*(?P<type>\w+)?\s*(?P<title>"[^"]*")?\s*$'
)
IMAGE_ATTR_RE = re.compile(
    r'!\[(?P<alt>[^\]]*)\]\((?P<src>[^)]+)\)\s*\{(?P<attrs>[^}]*)\}'
)
IMAGE_MD_RE = re.compile(r'!\[(?P<alt>[^\]]*)\]\((?P<src>[^)]+)\)')
RAW_IMG_RE = re.compile(r'<img(?P<attrs>[^>]*)>')
CODE_FENCE_RE = re.compile(r'^(?P<indent>\s*)```(?P<lang>\w+)?\s*$')

CALLOUT_TYPE_MAP = {
    "info": "info",
    "tip": "tip",
    "warning": "warning",
    "success": "success",
    "failure": "error",
    "bug": "error",
    "abstract": "note",
    "example": "info",
    "question": "info",
}

PATH_OVERRIDES = {
    "installing-maple-sim.md": "getting-started/installing-maple-sim.mdx",
    "using-the-simulated-arena.md": "core-concepts/using-the-simulated-arena.mdx",
    "swerve-simulation-overview.md": "swerve-simulation/swerve-simulation-overview.mdx",
    "swerve-sim-easy.md": "swerve-simulation/swerve-sim-easy.mdx",
    "swerve-sim-hardware-abstraction.md": "swerve-simulation/swerve-sim-hardware-abstraction.mdx",
    "simulating-intake.md": "mechanisms/simulating-intake.mdx",
    "simulating-projectiles.md": "mechanisms/simulating-projectiles.mdx",
    "simulating-opponent-robots.md": "match-simulation/simulating-opponent-robots.mdx",
    "rebuilt.md": "match-simulation/rebuilt.mdx",
    "CONTRIBUTION.md": "contribution/index.mdx",
}

LINK_REWRITES = {
    "./simulation-details.md": "./simulation-details",
    "./installing-maple-sim.md": "./getting-started/installing-maple-sim",
    "./using-the-simulated-arena.md": "./core-concepts/using-the-simulated-arena",
    "./swerve-simulation-overview.md": "./swerve-simulation/swerve-simulation-overview",
    "./simulating-intake.md": "./mechanisms/simulating-intake",
    "./simulating-projectiles.md": "./mechanisms/simulating-projectiles",
    "./simulating-opponent-robots.md": "./match-simulation/simulating-opponent-robots",
    "./CONTRIBUTION.md": "./contribution",
    "./swerve-sim-easy.md": "./swerve-sim-easy",
    "./swerve-sim-hardware-abstraction.md": "./swerve-sim-hardware-abstraction",
}

META_FILES = {
    "meta.json": {
        "title": "Docs",
        "pages": [
            "index",
            "simulation-details",
            "getting-started",
            "core-concepts",
            "swerve-simulation",
            "mechanisms",
            "match-simulation",
            "contribution",
            "release-notes",
        ],
    },
    "getting-started/meta.json": {"title": "Getting Started", "pages": ["installing-maple-sim"]},
    "core-concepts/meta.json": {"title": "Core Concepts", "pages": ["using-the-simulated-arena"]},
    "swerve-simulation/meta.json": {
        "title": "Swerve Simulation",
        "pages": ["swerve-simulation-overview", "swerve-sim-easy", "swerve-sim-hardware-abstraction"],
    },
    "mechanisms/meta.json": {"title": "Mechanisms", "pages": ["simulating-intake", "simulating-projectiles"]},
    "match-simulation/meta.json": {
        "title": "Match Simulation",
        "pages": ["simulating-opponent-robots", "rebuilt"],
    },
    "contribution/meta.json": {"title": "Contribution", "pages": ["index"]},
    "release-notes/meta.json": {
        "title": "Release Notes",
        "pages": ["version0.3.0-beta2", "version0.2.0-beta1"],
    },
}


def title_case_from_filename(name: str) -> str:
    return name.replace("-", " ").replace("_", " ").strip().title()


def convert_admonitions(lines: list[str]) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        match = ADMONITION_RE.match(line)
        if not match:
            out.append(line)
            i += 1
            continue

        indent = match.group("indent") or ""
        marker = match.group("marker")
        kind = (match.group("type") or "").strip()
        raw_title = match.group("title")
        title = raw_title.strip()[1:-1] if raw_title else None

        i += 1
        block: list[str] = []
        while i < len(lines):
            next_line = lines[i]
            if next_line.strip() == "":
                block.append("")
                i += 1
                continue
            if next_line.startswith(indent + "    "):
                block.append(next_line[len(indent) + 4 :])
                i += 1
                continue
            break

        while block and block[-1] == "":
            block.pop()

        if marker == "???":
            summary = title or (kind.title() if kind else "Details")
            out.append("<details>")
            out.append(f"<summary>{summary}</summary>")
            out.append("")
            out.extend(block)
            out.append("")
            out.append("</details>")
        else:
            callout_type = CALLOUT_TYPE_MAP.get(kind, "note")
            attrs = [f'type="{callout_type}"']
            if title:
                attrs.append(f'title="{title}"')
            out.append(f"<Callout {' '.join(attrs)}>")
            out.append("")
            out.extend(block)
            out.append("")
            out.append("</Callout>")

        if i < len(lines) and lines[i].strip() != "":
            out.append("")
    return out


def convert_image_attrs(line: str) -> str:
    def repl(match: re.Match) -> str:
        alt = match.group("alt") or ""
        src = match.group("src").strip()
        attrs = match.group("attrs")
        width = None
        for part in attrs.split():
            if "width" in part:
                key, _, value = part.partition("=")
                if key.strip() == "width":
                    width = value.strip().strip('"')
        style = f" style={{{{ width: \"{width}\" }}}}" if width else ""
        return f"<img src=\"{src}\" alt=\"{alt}\"{style} />"

    return IMAGE_ATTR_RE.sub(repl, line)


def convert_markdown_images(line: str) -> str:
    def repl(match: re.Match) -> str:
        alt = match.group("alt") or ""
        src = match.group("src").strip()
        return f'<img src="{src}" alt="{alt}" />'

    return IMAGE_MD_RE.sub(repl, line)


def normalize_html_img(line: str) -> str:
    def repl(match: re.Match) -> str:
        attrs = match.group("attrs").strip()
        return f"<img {attrs} />" if attrs else "<img />"

    if "<img" in line and "/>" not in line:
        return RAW_IMG_RE.sub(repl, line)
    return line


HTML_REWRITES = {
    '<div class="grid cards" markdown>': '<div className="grid cards">',
    '<div style="display: flex;" markdown>': '<div style={{ display: "flex" }}>',
    '<div style="display: flex; justify-content: space-between;" markdown>': (
        '<div style={{ display: "flex", justifyContent: "space-between" }}>'
    ),
}


def rewrite_html_line(line: str) -> str:
    return HTML_REWRITES.get(line, line)


STYLE_RE = re.compile(r'style="([^"]+)"')


def convert_style_attr(line: str) -> str:
    if 'style="' not in line:
        return line

    def repl(match: re.Match) -> str:
        style = match.group(1)
        parts = [p.strip() for p in style.split(";") if p.strip()]
        pairs: list[str] = []
        for part in parts:
            if ":" not in part:
                continue
            key, val = part.split(":", 1)
            key = key.strip()
            val = val.strip()
            segments = key.split("-")
            key = segments[0] + "".join(s.capitalize() for s in segments[1:])
            val = val.replace('"', '\\"')
            pairs.append(f'{key}: "{val}"')
        if not pairs:
            return match.group(0)
        return f"style={{{{ {', '.join(pairs)} }}}}"

    return STYLE_RE.sub(repl, line)


def normalize_code_fence(line: str) -> str:
    match = CODE_FENCE_RE.match(line)
    if not match:
        return line
    lang = (match.group("lang") or "").strip()
    if lang.lower() == "java":
        return f"{match.group('indent')}```text"
    return line


def rewrite_links(text: str, dest_rel: str) -> str:
    for old, new in LINK_REWRITES.items():
        text = text.replace(old, new)
    if dest_rel.startswith("mechanisms/"):
        text = text.replace("./mechanisms/", "./")
    elif dest_rel.startswith("core-concepts/") or dest_rel.startswith("match-simulation/"):
        text = text.replace("./mechanisms/", "../mechanisms/")
    return text


def convert_tabs(lines: list[str]) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('=== "'):
            tabs: list[tuple[str, list[str]]] = []
            while i < len(lines) and lines[i].startswith('=== "'):
                title = lines[i].split('"', 2)[1]
                i += 1
                block: list[str] = []
                while i < len(lines):
                    next_line = lines[i]
                    if next_line.strip() == "":
                        block.append("")
                        i += 1
                        continue
                    if next_line.startswith("    "):
                        block.append(next_line[4:])
                        i += 1
                        continue
                    break
                while block and block[-1] == "":
                    block.pop()
                tabs.append((title, block))
                if i < len(lines) and lines[i].strip() == "":
                    i += 1
            items = ", ".join([f'"{title}"' for title, _ in tabs])
            out.append(f"<Tabs items={{[{items}]}}>")
            for title, block in tabs:
                out.append(f'<Tab value="{title}">')
                out.append("")
                out.extend(block)
                out.append("")
                out.append("</Tab>")
            out.append("</Tabs>")
            continue
        out.append(line)
        i += 1
    return out


def fix_inline_code_fences(lines: list[str]) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if "Use ```java" in line:
            indent = line.split("Use", 1)[0]
            out.append(f"{indent}Use:")
            out.append(f"{indent}```java")
            i += 1
            if i < len(lines):
                out.append(f"{indent}{lines[i].strip()}")
                i += 1
            if i < len(lines) and "```" in lines[i]:
                trailing = lines[i].strip()
                after = trailing.split("```", 1)[1].strip()
                out.append(f"{indent}```")
                if after:
                    out.append(f"{indent}{after}")
                i += 1
            continue
        out.append(line)
        i += 1
    return out


def main() -> None:
    if DST_ROOT.exists():
        shutil.rmtree(DST_ROOT)
    DST_ROOT.mkdir(parents=True)

    count = 0
    for src_path in SRC_ROOT.rglob("*.md"):
        if "javadocs" in src_path.parts:
            continue
        rel = src_path.relative_to(SRC_ROOT)
        rel_key = rel.as_posix()
        if rel_key in PATH_OVERRIDES:
            dest_path = DST_ROOT / PATH_OVERRIDES[rel_key]
        else:
            dest_path = (DST_ROOT / rel).with_suffix(".mdx")
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        lines = src_path.read_text(encoding="utf-8").splitlines()

        if lines[:1] == ["---"]:
            try:
                end = lines[1:].index("---") + 1
                lines = lines[end + 1 :]
            except ValueError:
                pass

        title = None
        new_lines: list[str] = []
        removed_h1 = False
        for line in lines:
            if not removed_h1:
                match = re.match(r"^#\s+(.*)$", line)
                if match:
                    title = match.group(1).strip()
                    removed_h1 = True
                    continue
            new_lines.append(line)

        lines = new_lines
        if not title:
            title = title_case_from_filename(src_path.stem)

        lines = [convert_image_attrs(line) for line in lines]
        lines = [convert_markdown_images(line) for line in lines]
        lines = [normalize_html_img(line) for line in lines]
        lines = [convert_style_attr(line) for line in lines]
        lines = convert_admonitions(lines)
        lines = convert_tabs(lines)
        lines = [rewrite_html_line(line) for line in lines]
        lines = [normalize_code_fence(line) for line in lines]
        lines = fix_inline_code_fences(lines)

        dest_rel = dest_path.relative_to(DST_ROOT).as_posix()
        if dest_rel == "index.mdx":
            title = "Overview"
        text = "\n".join(lines)
        text = rewrite_links(text, dest_rel)
        lines = text.splitlines()

        out_lines: list[str] = []
        in_center_block = False
        for line in lines:
            if line.strip().lower().startswith('<p align="center"'):
                out_lines.append('<div className="flex flex-col items-center gap-4">')
                in_center_block = True
                continue
            if line.strip() == "</p>" and in_center_block:
                out_lines.append("</div>")
                in_center_block = False
                continue
            out_lines.append(line)

        frontmatter = ["---", f'title: "{title}"', "---", ""]
        dest_path.write_text("\n".join(frontmatter + out_lines).rstrip() + "\n", encoding="utf-8")
        count += 1

    print(f"Converted {count} files")

    for rel_path, data in META_FILES.items():
        meta_path = DST_ROOT / rel_path
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        meta_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
