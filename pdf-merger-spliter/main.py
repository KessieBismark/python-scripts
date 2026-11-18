#!/usr/bin/env python3
"""Merge several PDFs into one, or split a PDF into single-page files.

Usage:
    python3 main.py merge a.pdf b.pdf c.pdf            # -> a_merged.pdf
    python3 main.py merge a.pdf b.pdf -o combined.pdf
    python3 main.py split report.pdf                   # -> report_page_1.pdf, ...
    python3 main.py split report.pdf -d pages/

Needs pypdf (`pip install pypdf`); the older PyPDF2 also works.
"""
import argparse
import sys
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:  # pypdf used to be called PyPDF2
    try:
        from PyPDF2 import PdfReader, PdfWriter
    except ImportError:
        sys.exit("No PDF library found. Install one with:  python3 -m pip install pypdf")


def _open(pdf):
    """Read a PDF, unlocking it if it only has an empty owner password."""
    reader = PdfReader(str(pdf))
    if reader.is_encrypted and not reader.decrypt(""):
        raise ValueError(f"{pdf} is password-protected")
    return reader


def merge_pdfs(pdfs, output):
    """Write the pages of every file in `pdfs`, in order, into `output`."""
    pdfs = [Path(p) for p in pdfs]
    output = Path(output)

    missing = [p for p in pdfs if not p.is_file()]
    if missing:
        raise FileNotFoundError("not found: " + ", ".join(str(p) for p in missing))
    if any(p.resolve() == output.resolve() for p in pdfs if p.exists()):
        raise ValueError("the output file is also an input; choose another name")

    pdf_maker = PdfWriter()
    for pdf in pdfs:
        reader = _open(pdf)
        for page in reader.pages:
            pdf_maker.add_page(page)
        print(f"  + {pdf.name} ({len(reader.pages)} pages)")

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as out:
        pdf_maker.write(out)
    print(f"\n-> {output}  ({len(pdf_maker.pages)} pages, {output.stat().st_size / 1024:.0f} KB)")
    return output


def split_pdf(pdf, outdir=None):
    """Save each page of `pdf` as its own file; returns the paths written."""
    pdf = Path(pdf)
    if not pdf.is_file():
        raise FileNotFoundError(f"not found: {pdf}")

    outdir = Path(outdir) if outdir else pdf.parent
    outdir.mkdir(parents=True, exist_ok=True)

    reader = _open(pdf)
    written = []
    for page_num, page in enumerate(reader.pages, start=1):
        writer = PdfWriter()
        writer.add_page(page)
        target = outdir / f"{pdf.stem}_page_{page_num}.pdf"
        with target.open("wb") as out:
            writer.write(out)
        print(f"  -> {target.name}")
        written.append(target)
    print(f"\n{len(written)} page(s) written to {outdir}")
    return written


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    m = sub.add_parser("merge", help="merge PDFs into one file")
    m.add_argument("pdfs", nargs="+", help="files to merge, in the order given")
    m.add_argument("-o", "--output", help="output path (default: <first>_merged.pdf)")
    m.add_argument("-f", "--force", action="store_true", help="overwrite the output if it exists")

    s = sub.add_parser("split", help="split a PDF into one file per page")
    s.add_argument("pdf", help="file to split")
    s.add_argument("-d", "--outdir", help="where to write the pages (default: beside the input)")

    args = parser.parse_args(argv)

    try:
        if args.command == "merge":
            # check the inputs first, so a typo reports the typo and not the output
            missing = [p for p in args.pdfs if not Path(p).is_file()]
            if missing:
                sys.exit("error: not found: " + ", ".join(missing))
            first = Path(args.pdfs[0])
            output = Path(args.output) if args.output else first.with_name(f"{first.stem}_merged.pdf")
            if output.exists() and not args.force:
                sys.exit(f"error: {output} already exists (pass --force to overwrite)")
            merge_pdfs(args.pdfs, output)
        else:
            split_pdf(args.pdf, args.outdir)
    except (FileNotFoundError, ValueError) as exc:
        sys.exit(f"error: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
