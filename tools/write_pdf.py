from langchain_core.tools import tool
from datetime import datetime
from pathlib import Path
import subprocess
import re

def _sanitize_latex(raw: str) -> str:
    """Clean common model artifacts so Tectonic can compile."""
    replacements = {
        # Preamble and common packages
        "\\\\documentclass": "\\documentclass",
        "\\\\usepackage": "\\usepackage",
        "\\\\geometry": "\\geometry",
        "\\\\title": "\\title",
        "\\\\author": "\\author",
        "\\\\date": "\\date",
        # Document structure
        "\\\\begin{document}": "\\begin{document}",
        "\\\\end{document}": "\\end{document}",
        "\\\\maketitle": "\\maketitle",
        "\\\\begin{abstract}": "\\begin{abstract}",
        "\\\\end{abstract}": "\\end{abstract}",
        "\\\\section": "\\section",
        "\\\\subsection": "\\subsection",
        "\\\\subsubsection": "\\subsubsection",
        # Lists
        "\\\\item": "\\item",
        "\\\\begin{itemize}": "\\begin{itemize}",
        "\\\\end{itemize}": "\\end{itemize}",
        "\\\\begin{enumerate}": "\\begin{enumerate}",
        "\\\\end{enumerate}": "\\end{enumerate}",
        # Figures and tables
        "\\\\begin{figure}": "\\begin{figure}",
        "\\\\end{figure}": "\\end{figure}",
        "\\\\begin{table}": "\\begin{table}",
        "\\\\end{table}": "\\end{table}",
        "\\\\begin{tabular}": "\\begin{tabular}",
        "\\\\end{tabular}": "\\end{tabular}",
        "\\\\includegraphics": "\\includegraphics",
        "\\\\caption": "\\caption",
        "\\\\label": "\\label",
        # Math environments
        "\\\\begin{align}": "\\begin{align}",
        "\\\\end{align}": "\\end{align}",
        "\\\\begin{equation}": "\\begin{equation}",
        "\\\\end{equation}": "\\end{equation}",
        # Text formatting
        "\\\\textbf": "\\textbf",
        "\\\\textit": "\\textit",
        "\\\\emph": "\\emph",
        "\\\\cite": "\\cite",
        "\\\\ref": "\\ref",
        "\\\\href": "\\href",
        # Typography fixes
        "“": '"',
        "”": '"',
        "’": "'",
        "–": "--",
        "—": "---",
    }
    cleaned = raw
    for bad, good in replacements.items():
        cleaned = cleaned.replace(bad, good)

    # Collapse any leading double backslashes on a line (generic)
    cleaned = re.sub(r"(?m)^(\s*)\\\\(\S)", r"\1\\\2", cleaned)

    # If no document environment, wrap in a minimal template
    if "\\documentclass" not in cleaned:
        cleaned = (
            "\\documentclass{article}\n"
            "\\usepackage{amsmath}\n\\usepackage{graphicx}\n\\usepackage{hyperref}\n"
            "\\begin{document}\n" + cleaned + "\n\\end{document}\n"
        )
    else:
        # Ensure document env exists if preamble is present
        if "\\begin{document}" not in cleaned:
            cleaned = cleaned + "\n\\begin{document}\n"
        if "\\end{document}" not in cleaned:
            cleaned = cleaned + "\n\\end{document}\n"
    return cleaned

@tool
def render_latex_pdf(latex_content: str) -> str:
    """
    Render LaTeX content into a PDF file using Tectonic.
    Sanitizes common model output issues before compilation.
    Args:
        latex_content (str): The LaTeX document content as a string.
    Returns:
        str: The path to the generated PDF file.
    """
    output_dir = Path("pdf_outputs").absolute()
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    tex_filename = f"paper_{timestamp}.tex"
    pdf_filename = f"paper_{timestamp}.pdf"

    tex_file = output_dir / tex_filename
    tex_file.write_text(_sanitize_latex(latex_content))

    tectonic_path = str(Path.home() / "tectonic.exe")
    result = subprocess.run(
        [tectonic_path, tex_filename, "--outdir", str(output_dir)],
        cwd=output_dir,
        capture_output=True,
        text=True,
    )
    final_pdf_path = output_dir / pdf_filename
    if not final_pdf_path.exists():
        raise FileNotFoundError(f"PDF generation failed. Tectonic output:\n{result.stdout}\n{result.stderr}")
    print(f"PDF generated at: {final_pdf_path}")
    return str(final_pdf_path)