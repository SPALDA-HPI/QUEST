import pathlib
import re
import unittest
import urllib.parse


REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[1]
LINK_PATTERN = re.compile(r"!?\[[^]]*\]\(([^)]+)\)")


class DocumentationLinkTest(unittest.TestCase):
    def test_local_markdown_links_resolve(self) -> None:
        documents = [REPOSITORY_ROOT / "README.md"]
        documents.append(REPOSITORY_ROOT / "quickstart" / "README.md")
        documents.extend(sorted((REPOSITORY_ROOT / "docs").rglob("*.md")))

        for document in documents:
            text = document.read_text(encoding="utf-8")
            for match in LINK_PATTERN.finditer(text):
                target = match.group(1).strip()
                if target.startswith("<") and ">" in target:
                    target = target[1 : target.index(">")]
                else:
                    target = target.split(maxsplit=1)[0]

                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue

                path_text = urllib.parse.unquote(target.split("#", maxsplit=1)[0])
                if not path_text:
                    continue

                resolved = (document.parent / path_text).resolve()
                self.assertTrue(
                    resolved.exists(),
                    f"{document.relative_to(REPOSITORY_ROOT)}: missing {target}",
                )


if __name__ == "__main__":
    unittest.main()
