import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.config import FIGURE_DIR

def save_confusion_matrix(metrics):
    matrix = metrics.get("confusion_matrix", [[0,0],[0,0]])
    fig, ax = plt.subplots(figsize=(5,4))
    image = ax.imshow(matrix, cmap="Blues")
    ax.set_xticks([0,1], labels=["Normal", "Threat"])
    ax.set_yticks([0,1], labels=["Normal", "Threat"])
    ax.set_xlabel("Predicted label"); ax.set_ylabel("Actual label"); ax.set_title("Threat classifier — confusion matrix")
    for i in range(2):
        for j in range(2): ax.text(j, i, str(matrix[i][j]), ha="center", va="center", color="black", fontsize=12)
    fig.colorbar(image, ax=ax, fraction=.046, pad=.04); fig.tight_layout()
    path = FIGURE_DIR / "confusion_matrix.png"; fig.savefig(path, dpi=150); plt.close(fig)
    return path
