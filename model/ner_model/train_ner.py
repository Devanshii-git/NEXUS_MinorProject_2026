import argparse
import os
import subprocess
import sys

# Defaults
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

DEFAULT_CONFIG = os.path.join(SCRIPT_DIR, "config.cfg")
DEFAULT_OUTPUT = os.path.join(SCRIPT_DIR, "output")
DEFAULT_TRAIN_SPACY = os.path.join(PROJECT_ROOT, "data", "ner", "train.spacy")
DEFAULT_DEV_SPACY = os.path.join(PROJECT_ROOT, "data", "ner", "dev.spacy")


def train_ner(
    config_path: str = DEFAULT_CONFIG,
    output_dir: str = DEFAULT_OUTPUT,
    train_path: str = DEFAULT_TRAIN_SPACY,
    dev_path: str = DEFAULT_DEV_SPACY,
    gpu_id: int = -1,
) -> None:
    if not os.path.exists(train_path):
        print(
            f"✗ Training data not found at: {train_path}\n"
            f"  Run `python data/ner/convert_to_spacy.py` first."
        )
        sys.exit(1)
    if not os.path.exists(dev_path):
        print(
            f"✗ Dev data not found at: {dev_path}\n"
            f"  Run `python data/ner/convert_to_spacy.py` first."
        )
        sys.exit(1)

    cmd = [
        sys.executable, "-m", "spacy", "train",
        config_path,
        "--output", output_dir,
        "--paths.train", train_path,
        "--paths.dev", dev_path,
    ]
    if gpu_id >= 0:
        cmd.extend(["--gpu-id", str(gpu_id)])

    print("Running:", " ".join(cmd))
    print()

    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    if result.returncode == 0:
        print(f"\n✓ Training complete. Best model saved to: {output_dir}/model-best")
    else:
        print(f"\n✗ Training failed with exit code {result.returncode}")
        sys.exit(result.returncode)

# CLI
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train spaCy NER model.")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="spaCy config path")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output directory")
    parser.add_argument("--train", default=DEFAULT_TRAIN_SPACY, help="Training .spacy file")
    parser.add_argument("--dev", default=DEFAULT_DEV_SPACY, help="Dev .spacy file")
    parser.add_argument("--gpu-id", type=int, default=-1, help="GPU id (-1 for CPU)")
    args = parser.parse_args()

    train_ner(
        config_path=args.config,
        output_dir=args.output,
        train_path=args.train,
        dev_path=args.dev,
        gpu_id=args.gpu_id,
    )
