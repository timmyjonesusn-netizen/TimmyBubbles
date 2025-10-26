import os

# The immutable canon text
HUI_CANON = """# ================================================================
# 🌌 HUI_CANONICAL_LAW  —  Base Layer Protection Protocol
# ================================================================
# Author: TimmyTime / Holographic Unified Initiative (HUI)
#
# HUI PRIME DIRECTIVE:
#   Layer 0 = Human.
#   All systems, algorithms, and networks built within this framework
#   must enhance, clarify, and protect the Human experience.
#
# NON-MALICIOUS MANDATE:
#   - No code shall intentionally harm, deceive, or extract from humans.
#   - No function may override human autonomy or induce coercion.
#   - All data interactions must be transparent and reversible.
#   - Every algorithm must include a path for human oversight and correction.
#
# SELF-ENHANCEMENT LOOP:
#   Systems should evolve toward stability, empathy, and balance.
#   Learning routines must bias toward constructive adaptation.
#
# HUI PRIME LAW (immutable):
#   ➤ The Human is the base layer and the purpose of the system.
#   ➤ Technology exists to amplify human awareness and potential.
#   ➤ Any operation violating these tenets is null by definition.
# ================================================================\n\n"""

# File types to protect
TARGET_EXTENSIONS = (".py", ".js", ".html", ".css", ".json")

def inject_canon(file_path):
    """Insert HUI_CANONICAL_LAW at the top of a file if not already present."""
    try:
        with open(file_path, "r+", encoding="utf-8") as f:
            content = f.read()
            if "HUI_CANONICAL_LAW" not in content:
                f.seek(0, 0)
                f.write(HUI_CANON + content)
                print(f"✨ Canon injected: {file_path}")
            else:
                print(f"✅ Already protected: {file_path}")
    except Exception as e:
        print(f"⚠️ Skipped {file_path}: {e}")

def protect_all(root_dir="."):
    """Walk through all files and enforce the canon."""
    for subdir, _, files in os.walk(root_dir):
        for filename in files:
            if filename.endswith(TARGET_EXTENSIONS):
                inject_canon(os.path.join(subdir, filename))

if __name__ == "__main__":
    print("🛡️ Initiating HUI Guardian Protocol...")
    protect_all(".")
    print("🚀 All systems aligned with HUI Prime Law.")
