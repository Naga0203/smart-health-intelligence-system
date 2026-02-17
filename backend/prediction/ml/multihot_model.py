
import torch
import torch.nn as nn

# ============================================================================
# MODEL ARCHITECTURE
# ============================================================================

class ResidualBlock(nn.Module):
    """Residual block with skip connection for better gradient flow"""
    def __init__(self, in_dim, out_dim, dropout=0.3):
        super(ResidualBlock, self).__init__()

        self.block = nn.Sequential(
            nn.Linear(in_dim, out_dim),
            nn.BatchNorm1d(out_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout)
        )

        # Projection shortcut if dimensions don't match
        self.shortcut = nn.Sequential()
        if in_dim != out_dim:
            self.shortcut = nn.Sequential(
                nn.Linear(in_dim, out_dim),
                nn.BatchNorm1d(out_dim)
            )

    def forward(self, x):
        return self.block(x) + self.shortcut(x)


class SymptomClassifier(nn.Module):
    """Enhanced symptom classifier with residual connections"""
    def __init__(self, input_dim, num_classes, hidden_dims=[512, 512, 256, 256], dropout=0.3):
        super(SymptomClassifier, self).__init__()

        # Input projection
        self.input_layer = nn.Sequential(
            nn.Linear(input_dim, hidden_dims[0]),
            nn.BatchNorm1d(hidden_dims[0]),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout)
        )

        # Residual blocks
        self.residual_blocks = nn.ModuleList()
        for i in range(len(hidden_dims) - 1):
            self.residual_blocks.append(
                ResidualBlock(hidden_dims[i], hidden_dims[i+1], dropout)
            )

        # Output layer
        self.output_layer = nn.Linear(hidden_dims[-1], num_classes)

        self._initialize_weights()

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm1d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)

    def forward(self, x):
        x = self.input_layer(x)

        for block in self.residual_blocks:
            x = block(x)

        x = self.output_layer(x)
        return x
