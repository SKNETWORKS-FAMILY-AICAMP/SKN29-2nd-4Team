import torch
import torch.nn as nn
from config import STATIC_CAT_FEATURES, EMB_DIM, STATIC_HIDDEN, DYNAMIC_HIDDEN, DROPOUT, FOCAL_ALPHA, FOCAL_GAMMA


class FocalLoss(nn.Module):
    """Binary Focal Loss: FL = -alpha*(1-p)^gamma*log(p) for positives."""

    def __init__(self, alpha: float = FOCAL_ALPHA, gamma: float = FOCAL_GAMMA):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        bce = nn.functional.binary_cross_entropy_with_logits(logits, targets, reduction="none")
        probs = torch.sigmoid(logits)
        pt    = torch.where(targets == 1, probs, 1 - probs)
        alpha_t = torch.where(targets == 1,
                              torch.full_like(targets, self.alpha),
                              torch.full_like(targets, 1 - self.alpha))
        focal_weight = alpha_t * (1 - pt) ** self.gamma
        return (focal_weight * bce).mean()


def _make_block(in_dim: int, out_dim: int, dropout: float, last: bool = False):
    layers: list[nn.Module] = [nn.Linear(in_dim, out_dim)]
    if not last:
        layers += [nn.BatchNorm1d(out_dim), nn.GELU(), nn.Dropout(dropout)]
    return nn.Sequential(*layers)


class StaticFCNN(nn.Module):
    def __init__(self, vocab_sizes: dict, n_num: int):
        super().__init__()
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
        return x


class DynamicFCNN(nn.Module):
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
        return self.head(x).squeeze(1)


class TwoStageFCNN(nn.Module):
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
        return self.dynamic_net(repr_, dynamic)

    @torch.no_grad()
    def encode_static(self, static_num: torch.Tensor, static_cat: torch.Tensor) -> torch.Tensor:
        self.eval()
        return self.static_net(static_num, static_cat)
