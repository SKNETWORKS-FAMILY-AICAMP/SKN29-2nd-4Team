import torch
import torch.nn as nn
from config import STATIC_CAT_FEATURES, EMB_DIM, STATIC_HIDDEN, DYNAMIC_HIDDEN, DROPOUT


def _make_block(in_dim: int, out_dim: int, dropout: float, last: bool = False):
    """Linear → (BN → ReLU → Dropout) unless last layer."""
    layers: list[nn.Module] = [nn.Linear(in_dim, out_dim)]
    if not last:
        layers += [nn.BatchNorm1d(out_dim), nn.ReLU(inplace=True), nn.Dropout(dropout)]
    return nn.Sequential(*layers)


class StaticFCNN(nn.Module):
    """First stage: encodes scheduled / route / airline info into a latent vector.

    Input  : static_num  (batch, n_static_num)
             static_cat  (batch, n_cat_features)  -- integer-encoded
    Output : (batch, STATIC_HIDDEN[-1])
    """

    def __init__(self, vocab_sizes: dict, n_num: int):
        super().__init__()
        # One embedding table per categorical feature
        self.embeddings = nn.ModuleDict({
            col: nn.Embedding(vocab_sizes[col] + 1, EMB_DIM[col], padding_idx=0)
            for col in STATIC_CAT_FEATURES
        })
        emb_total = sum(EMB_DIM[col] for col in STATIC_CAT_FEATURES)

        dims = [n_num + emb_total] + STATIC_HIDDEN
        self.blocks = nn.ModuleList([
            _make_block(dims[i], dims[i + 1], DROPOUT, last=(i == len(dims) - 2))
            for i in range(len(dims) - 1)
        ])
        self.out_dim = STATIC_HIDDEN[-1]

    def forward(self, static_num: torch.Tensor, static_cat: torch.Tensor) -> torch.Tensor:
        embs = [
            self.embeddings[col](static_cat[:, i])
            for i, col in enumerate(STATIC_CAT_FEATURES)
        ]
        x = torch.cat([static_num, *embs], dim=1)
        for block in self.blocks:
            x = block(x)
        return x  # (batch, out_dim)


class DynamicFCNN(nn.Module):
    """Second stage: combines static repr with real-time weather / ops features.

    Input  : static_repr  (batch, static_out_dim)
             dynamic      (batch, n_dynamic)
    Output : (batch,)  raw logits  (apply sigmoid for probability)
    """

    def __init__(self, static_out_dim: int, n_dynamic: int):
        super().__init__()
        dims = [static_out_dim + n_dynamic] + DYNAMIC_HIDDEN
        self.blocks = nn.ModuleList([
            _make_block(dims[i], dims[i + 1], DROPOUT, last=(i == len(dims) - 2))
            for i in range(len(dims) - 1)
        ])
        self.head = nn.Linear(DYNAMIC_HIDDEN[-1], 1)

    def forward(self, static_repr: torch.Tensor, dynamic: torch.Tensor) -> torch.Tensor:
        x = torch.cat([static_repr, dynamic], dim=1)
        for block in self.blocks:
            x = block(x)
        return self.head(x).squeeze(1)  # (batch,) raw logits


class TwoStageFCNN(nn.Module):
    """Full two-stage model: StaticFCNN → DynamicFCNN."""

    def __init__(self, vocab_sizes: dict, n_static_num: int, n_dynamic: int):
        super().__init__()
        self.static_net  = StaticFCNN(vocab_sizes, n_static_num)
        self.dynamic_net = DynamicFCNN(self.static_net.out_dim, n_dynamic)

    def forward(
        self,
        static_num: torch.Tensor,
        static_cat: torch.Tensor,
        dynamic:    torch.Tensor,
    ) -> torch.Tensor:
        repr_ = self.static_net(static_num, static_cat)
        return self.dynamic_net(repr_, dynamic)  # raw logits

    @torch.no_grad()
    def encode_static(self, static_num: torch.Tensor, static_cat: torch.Tensor) -> torch.Tensor:
        """Extract static latent representation (for analysis / transfer)."""
        self.eval()
        return self.static_net(static_num, static_cat)
