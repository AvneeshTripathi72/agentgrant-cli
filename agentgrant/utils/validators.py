from __future__ import annotations

from agentgrant.core.constants import SUPPORTED_OUTPUTS
from agentgrant.core.exceptions import ValidationError


def validate_output_format(output: str) -> str:
    if output not in SUPPORTED_OUTPUTS:
        raise ValidationError(
            f"Unsupported output format '{output}'. Expected one of: {', '.join(SUPPORTED_OUTPUTS)}"
        )
    return output
