from __future__ import annotations

from string import Template


MANIFEST_CLI_TEMPLATE = Template(
    "quinkgl manifest create \\\n"
    "  --name ${name} \\\n"
    "  --task-type ${task_type} \\\n"
    "  --input-shape ${input_shape} \\\n"
    "  --output-shape ${output_shape} \\\n"
    "  --label-type ${label_type} \\\n"
    "  --model-framework ${model_framework} \\\n"
    "  --model-arch-hash ${model_arch_hash} \\\n"
    "  --aggregation ${aggregation} \\\n"
    "  --topology ${topology} \\\n"
    "  --sign-with creator.key \\\n"
    "  --output ${output_path}"
)

RUN_PEER_CLI_TEMPLATE = Template(
    "quinkgl run \\\n"
    "  --manifest ${manifest_path} \\\n"
    "  --script ${script_path} \\\n"
    "  --node-id ${node_id} \\\n"
    "  --port ${port} \\\n"
    "  --trust-policy ${trust_policy} \\\n"
    "  --rounds ${rounds}${script_args}"
)

