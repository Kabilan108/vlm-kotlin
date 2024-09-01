from transformers import AutoModel, AutoTokenizer
import torch

torch.manual_seed(0)


async def get_model():
    """Load and prepare the MiniCPM-V-2_6 model for inference."""
    model = AutoModel.from_pretrained(
        "openbmb/MiniCPM-V-2_6",
        trust_remote_code=True,
        attn_implementation="sdpa",
        torch_dtype=torch.bfloat16,
    )
    return model.eval().cuda()


async def get_tokenizer():
    """Load the tokenizer for the MiniCPM-V-2_6 model."""
    return AutoTokenizer.from_pretrained(
        "openbmb/MiniCPM-V-2_6", trust_remote_code=True
    )
