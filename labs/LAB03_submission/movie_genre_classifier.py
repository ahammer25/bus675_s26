"""
Lab 3 — Part A: Multimodal Movie Genre Classifier
==================================================
Complete this file to build and train your multimodal neural network.
How you structure the training script (entry point, argument handling, etc.)
is up to you.
"""

import json
import os
from collections import Counter
from pathlib import Path
import argparse

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from tqdm import tqdm


GENRES = ["Animation", "Comedy", "Documentary", "Horror", "Romance", "Sci-Fi"]
NUMERIC_COLS = ["runtime", "vote_average", "vote_count", "release_year", "popularity", "budget", "revenue"]
LIST_FIELDS = ["cast", "directors", "writers", "production_companies"]
SINGLE_CAT_FIELDS = ["mpaa_rating"]

IMAGE_SIZE = 128
MAX_LIST_LEN = 20
TOP_N_VOCAB = 50
EMBED_DIM = 32


class VocabBuilder:
    PAD_IDX = 0
    UNK_IDX = 1

    def __init__(self, top_n=TOP_N_VOCAB):
        self.top_n = top_n
        self.vocabs = {}
        self.sizes = {}

    def fit(self, df):
        for field in LIST_FIELDS:
            counts = Counter()
            for val in df[field].dropna():
                if val:
                    counts.update(v.strip() for v in str(val).split("|") if v.strip())
            top_tokens = [tok for tok, _ in counts.most_common(self.top_n)]
            vocab = {tok: idx + 2 for idx, tok in enumerate(top_tokens)}
            self.vocabs[field] = vocab
            self.sizes[field] = len(vocab) + 2

        for field in SINGLE_CAT_FIELDS:
            unique_vals = [v for v in df[field].unique() if isinstance(v, str) and v.strip()]
            vocab = {v: idx + 2 for idx, v in enumerate(sorted(unique_vals))}
            self.vocabs[field] = vocab
            self.sizes[field] = len(vocab) + 2
        return self

    def encode_list(self, val, field, max_len=MAX_LIST_LEN):
        vocab = self.vocabs.get(field, {})
        if not isinstance(val, str) or not val.strip():
            return [self.PAD_IDX] * max_len
        tokens = [v.strip() for v in val.split("|") if v.strip()]
        ids = [vocab.get(tok, self.UNK_IDX) for tok in tokens][:max_len]
        ids += [self.PAD_IDX] * (max_len - len(ids))
        return ids

    def encode_single(self, val, field):
        vocab = self.vocabs.get(field, {})
        if not isinstance(val, str) or not val.strip():
            return self.PAD_IDX
        return vocab.get(val.strip(), self.UNK_IDX)

    def save(self, path):
        Path(path).write_text(json.dumps({"vocabs": self.vocabs, "sizes": self.sizes, "top_n": self.top_n}))


class NumericScaler:
    def __init__(self):
        self.means = {}
        self.stds = {}

    def fit(self, df):
        for col in NUMERIC_COLS:
            vals = pd.to_numeric(df[col], errors="coerce")
            self.means[col] = float(vals.mean())
            self.stds[col] = max(float(vals.std()), 1e-8)
        return self

    def transform_row(self, row):
        values = []
        for col in NUMERIC_COLS:
            val = pd.to_numeric(row.get(col, np.nan), errors="coerce")
            if pd.isna(val):
                val = self.means.get(col, 0.0)
            values.append((float(val) - self.means.get(col, 0.0)) / self.stds.get(col, 1.0))
        return np.array(values, dtype=np.float32)


class MoviePosterDataset(Dataset):
    def __init__(self, df, data_dir, vocab_builder, numeric_scaler, transform=None):
        self.df = df.reset_index(drop=True)
        self.data_dir = Path(data_dir)
        self.vocab_builder = vocab_builder
        self.numeric_scaler = numeric_scaler
        self.transform = transform
        self.label_to_idx = {g: i for i, g in enumerate(GENRES)}

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]

        img_path = self.data_dir / row["image_path"]
        try:
            image = Image.open(img_path).convert("RGB")
        except Exception:
            image = Image.new("RGB", (IMAGE_SIZE, IMAGE_SIZE), color=(0, 0, 0))

        if self.transform:
            image = self.transform(image)

        numeric = torch.tensor(self.numeric_scaler.transform_row(row), dtype=torch.float32)

        list_inputs = {
            field: torch.tensor(self.vocab_builder.encode_list(row.get(field, ""), field), dtype=torch.long)
            for field in LIST_FIELDS
        }

        single_inputs = {
            field: torch.tensor(self.vocab_builder.encode_single(row.get(field, ""), field), dtype=torch.long)
            for field in SINGLE_CAT_FIELDS
        }

        label = torch.tensor(self.label_to_idx[row["label"]], dtype=torch.long)

        return {
            "image": image,
            "numeric": numeric,
            "list_inputs": list_inputs,
            "single_inputs": single_inputs,
            "label": label,
        }


class ImageBranch(nn.Module):
    """Custom CNN branch for Part A."""

    def __init__(self, out_dim=128):
        super().__init__()
        self.cnn = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),

            nn.AdaptiveAvgPool2d((1, 1)),
        )
        self.proj = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256, out_dim),
            nn.ReLU(),
            nn.Dropout(0.30),
        )

    def forward(self, x):
        return self.proj(self.cnn(x))


class TabularBranch(nn.Module):
    def __init__(self, vocab_sizes, numeric_dim=len(NUMERIC_COLS), out_dim=128):
        super().__init__()

        self.list_embeddings = nn.ModuleDict({
            field: nn.Embedding(vocab_sizes[field], EMBED_DIM, padding_idx=0)
            for field in LIST_FIELDS
        })

        self.single_embeddings = nn.ModuleDict({
            field: nn.Embedding(vocab_sizes[field], EMBED_DIM, padding_idx=0)
            for field in SINGLE_CAT_FIELDS
        })

        self.numeric_net = nn.Sequential(
            nn.Linear(numeric_dim, 32),
            nn.ReLU(),
            nn.Dropout(0.20),
        )

        total_cat_dim = EMBED_DIM * (len(LIST_FIELDS) + len(SINGLE_CAT_FIELDS))
        self.combiner = nn.Sequential(
            nn.Linear(32 + total_cat_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.30),
            nn.Linear(128, out_dim),
            nn.ReLU(),
        )

    def mean_pool_embedding(self, emb_layer, token_ids):
        emb = emb_layer(token_ids)
        mask = (token_ids != 0).float().unsqueeze(-1)
        denom = mask.sum(dim=1).clamp(min=1)
        return (emb * mask).sum(dim=1) / denom

    def forward(self, numeric, list_inputs, single_inputs):
        pieces = [self.numeric_net(numeric)]

        for field in LIST_FIELDS:
            pieces.append(self.mean_pool_embedding(self.list_embeddings[field], list_inputs[field]))

        for field in SINGLE_CAT_FIELDS:
            pieces.append(self.single_embeddings[field](single_inputs[field]))

        return self.combiner(torch.cat(pieces, dim=1))


class MultimodalGenreClassifier(nn.Module):
    def __init__(self, vocab_sizes, num_classes=len(GENRES)):
        super().__init__()
        self.image_branch = ImageBranch(out_dim=128)
        self.tabular_branch = TabularBranch(vocab_sizes, out_dim=128)
        self.fusion_head = nn.Sequential(
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.40),
            nn.Linear(128, num_classes),
        )

    def forward(self, image, numeric, list_inputs, single_inputs):
        image_features = self.image_branch(image)
        tab_features = self.tabular_branch(numeric, list_inputs, single_inputs)
        return self.fusion_head(torch.cat([image_features, tab_features], dim=1))


def move_batch_to_device(batch, device):
    return {
        "image": batch["image"].to(device),
        "numeric": batch["numeric"].to(device),
        "list_inputs": {k: v.to(device) for k, v in batch["list_inputs"].items()},
        "single_inputs": {k: v.to(device) for k, v in batch["single_inputs"].items()},
        "label": batch["label"].to(device),
    }


def run_epoch(model, loader, criterion, optimizer, device, train=True):
    model.train() if train else model.eval()
    total_loss, correct, total = 0.0, 0, 0

    loop = tqdm(loader, desc="train" if train else "eval", leave=False)

    for batch in loop:
        batch = move_batch_to_device(batch, device)

        with torch.set_grad_enabled(train):
            logits = model(batch["image"], batch["numeric"], batch["list_inputs"], batch["single_inputs"])
            loss = criterion(logits, batch["label"])

            if train:
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

        preds = logits.argmax(dim=1)
        total_loss += loss.item() * batch["label"].size(0)
        correct += (preds == batch["label"]).sum().item()
        total += batch["label"].size(0)

    return total_loss / total, correct / total


@torch.no_grad()
def evaluate_per_class(model, loader, device):
    model.eval()
    correct = torch.zeros(len(GENRES), dtype=torch.long)
    total = torch.zeros(len(GENRES), dtype=torch.long)

    for batch in tqdm(loader, desc="test", leave=False):
        batch = move_batch_to_device(batch, device)
        logits = model(batch["image"], batch["numeric"], batch["list_inputs"], batch["single_inputs"])
        preds = logits.argmax(dim=1)

        for label, pred in zip(batch["label"].cpu(), preds.cpu()):
            total[label] += 1
            correct[label] += int(label == pred)

    print("\nPer-class test accuracy:")
    overall_correct = correct.sum().item()
    overall_total = total.sum().item()

    for i, genre in enumerate(GENRES):
        acc = correct[i].item() / max(total[i].item(), 1)
        print(f"{genre:<12} {acc:.3f}  ({correct[i].item()}/{total[i].item()})")

    print(f"{'Overall':<12} {overall_correct / max(overall_total, 1):.3f}  ({overall_correct}/{overall_total})")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="/Users/ameli/Documents/Bus675/bus675_s26/data/movie_posters")
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--checkpoint", type=str, default="best_model_partA.pth")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    train_df = pd.read_csv(data_dir / "train_manifest.csv")
    val_df = pd.read_csv(data_dir / "val_manifest.csv")
    test_df = pd.read_csv(data_dir / "test_manifest.csv")

    vocab_builder = VocabBuilder(top_n=TOP_N_VOCAB).fit(train_df)
    numeric_scaler = NumericScaler().fit(train_df)

    train_tfms = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.RandomHorizontalFlip(p=0.25),
        transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.10),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    eval_tfms = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    train_ds = MoviePosterDataset(train_df, data_dir, vocab_builder, numeric_scaler, train_tfms)
    val_ds = MoviePosterDataset(val_df, data_dir, vocab_builder, numeric_scaler, eval_tfms)
    test_ds = MoviePosterDataset(test_df, data_dir, vocab_builder, numeric_scaler, eval_tfms)

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, num_workers=2)
    test_loader = DataLoader(test_ds, batch_size=args.batch_size, shuffle=False, num_workers=2)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    model = MultimodalGenreClassifier(vocab_builder.sizes).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", patience=2, factor=0.5)

    best_val_acc = 0.0
    best_path = Path(args.checkpoint)

    for epoch in range(args.epochs):
        train_loss, train_acc = run_epoch(model, train_loader, criterion, optimizer, device, train=True)
        val_loss, val_acc = run_epoch(model, val_loader, criterion, optimizer, device, train=False)
        scheduler.step(val_acc)

        print(
            f"Epoch {epoch + 1:02d}/{args.epochs} | "
            f"train_loss={train_loss:.4f} train_acc={train_acc:.3f} | "
            f"val_loss={val_loss:.4f} val_acc={val_acc:.3f}"
        )

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_acc": val_acc,
                "vocab_sizes": vocab_builder.sizes,
            }, best_path)
            print(f"Saved new best checkpoint: {best_path}")

    print(f"\nLoading best checkpoint from {best_path}")
    checkpoint = torch.load(best_path, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    evaluate_per_class(model, test_loader, device)


if __name__ == "__main__":
    main()

