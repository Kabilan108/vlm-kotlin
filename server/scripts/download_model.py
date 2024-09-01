from transformers import AutoModel, AutoTokenizer
import torch


torch.manual_seed(0)


def main():
    model = AutoModel.from_pretrained(
        "openbmb/MiniCPM-V-2_6",
        trust_remote_code=True,
        attn_implementation="sdpa",
        torch_dtype=torch.bfloat16,
        cache_dir="/models",
    )

    tokenizer = AutoTokenizer.from_pretrained(
        "openbmb/MiniCPM-V-2_6", trust_remote_code=True, cache_dir="/models"
    )

    print(model)
    print(tokenizer)


if __name__ == "__main__":
    main()
