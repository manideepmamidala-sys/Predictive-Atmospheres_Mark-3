"""
CLI Entry Point for Predictive Atmospheres
===========================================
Train and evaluate models without Streamlit.

Usage:
    python -m src.cli train                     # Train with defaults
    python -m src.cli train --model "Random Forest"
    python -m src.cli info                      # Show experiment info
    python -m src.cli predict 10.0 8.0 3.5      # Predict V/A for a room
"""
import argparse
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def cmd_train(args):
    from src.models.train import Trainer
    print(f"Training model: {args.model}")
    print(f"Feature mode : {args.feature_mode}")
    trainer = Trainer(model_type=args.model, feature_mode=args.feature_mode)
    result = trainer.train()
    print(f"\n{'='*50}")
    print(f"Model type : {result.model_type}")
    print(f"Features   : {result.feature_mode}")
    print(f"Converged  : {result.converged}")
    print(f"Final LR   : {result.final_lr:.6f}")
    print(f"Metrics:")
    for k, v in result.metrics.items():
        print(f"  {k:15s}: {v:.6f}")
    print(f"Data points: {len(result.X_spatial)}")
    if result.artifacts:
        print("Artifacts:")
        for key, value in result.artifacts.items():
            print(f"  {key:24s}: {value}")
    print(f"{'='*50}")


def cmd_info(args):
    from src.data.experiment_registry import discover_experiments
    experiments = discover_experiments()
    if not experiments:
        print("No experiments discovered.")
        return
    for exp in experiments:
        print(f"\n{exp.name}")
        print(f"  Biometric : {exp.biometric_csv}")
        print(f"  Spatial   : {exp.spatial_csv}")
        print(f"  Raw dir   : {exp.raw_dir}")
        print(f"  Rows      : {exp.num_rows}")
        print(f"  Spatial   : {exp.spatial_columns}")
        print(f"  Has data  : {exp.has_data}")


def cmd_predict(args):
    from src.models.train import Trainer
    import torch

    trainer = Trainer(model_type='PyTorch MLP')
    result = trainer.train()
    model = result.model
    model.eval()

    inp = torch.tensor([[args.length, args.width, args.height]], dtype=torch.float32)
    with torch.no_grad():
        out = model(inp).numpy().flatten()

    print(f"Room: L={args.length}, W={args.width}, H={args.height}")
    print(f"Predicted Valence: {out[0]:.4f}")
    print(f"Predicted Arousal: {out[1]:.4f}")
    print(f"Neuro-Score     : {(out[0]+1)/2:.4f}")


def main():
    parser = argparse.ArgumentParser(
        prog='predictive-atmospheres',
        description='Predictive Atmospheres CLI'
    )
    sub = parser.add_subparsers(dest='command')

    # train
    p_train = sub.add_parser('train', help='Train a model')
    p_train.add_argument('--model', default='PyTorch MLP',
                         choices=['PyTorch MLP', 'Random Forest', 'Ridge Regression'])
    p_train.add_argument('--feature-mode', default='baseline',
                         choices=['baseline', 'full'],
                         help='baseline: Length/Width/Height only, full: all engineered spatial parameters')

    # info
    sub.add_parser('info', help='Show experiment info')

    # predict
    p_pred = sub.add_parser('predict', help='Predict V/A for a room')
    p_pred.add_argument('length', type=float)
    p_pred.add_argument('width', type=float)
    p_pred.add_argument('height', type=float)

    args = parser.parse_args()
    if args.command == 'train':
        cmd_train(args)
    elif args.command == 'info':
        cmd_info(args)
    elif args.command == 'predict':
        cmd_predict(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
