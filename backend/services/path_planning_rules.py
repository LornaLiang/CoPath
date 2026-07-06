from typing import Any


GRAPH_TO_PATH_NODE_IDS = {"recursion_thinking": "recursion"}
PATH_TO_GRAPH_NODE_IDS = {value: key for key, value in GRAPH_TO_PATH_NODE_IDS.items()}


def path_node_id(node_id: str) -> str:
    return GRAPH_TO_PATH_NODE_IDS.get(node_id, node_id)


def select_strategy(
    profile: dict,
    current_path_type: str,
    ai_context: dict,
) -> tuple[str, str]:
    mastery = profile["mastery"]
    signal = ai_context["latest_signal"]
    gap = path_node_id(signal.get("knowledge_gap") or "")
    confusion = float(signal.get("confusion_level") or 0.0)
    preference = ai_context["sustained_preference"] or profile[
        "learning_preference"
    ]
    call_stack_mastery = mastery.get("call_stack", 0.5)
    average_mastery = sum(mastery.values()) / len(mastery) if mastery else 0.5

    if (
        ai_context["sustained_preference"]
        and ai_context["sustained_preference"] != current_path_type
    ):
        selected = ai_context["sustained_preference"]
        return (
            selected,
            f"连续 AI 信号偏好 {selected}，与当前 {current_path_type} 路径不一致，切换路径策略",
        )
    if gap == "call_stack" and (confusion > 0.75 or call_stack_mastery < 0.4):
        return (
            "basic",
            f"call_stack mastery={call_stack_mastery:.2f}, confusion={confusion:.2f}，选择基础补全路径",
        )
    if preference == "example" and (
        gap in {"recursion", "basic_recursion"} or confusion >= 0.5
    ):
        return (
            "example",
            f"学习偏好为 example 且 confusion={confusion:.2f}，选择案例驱动路径",
        )
    if profile["learning_speed"] == "fast" and average_mastery >= 0.75:
        return (
            "fast",
            f"learning_speed=fast 且平均 mastery={average_mastery:.2f}，选择快速路径",
        )
    if call_stack_mastery < 0.4 or profile["learning_speed"] in {
        "slow",
        "medium",
    }:
        return (
            "basic",
            f"基础知识 mastery 偏低或 learning_speed={profile['learning_speed']}，选择基础补全路径",
        )
    if preference in {"basic", "example", "fast"}:
        return preference, f"依据稳定学习偏好 {preference} 选择路径"
    return "basic", "缺少稳定偏好信号，使用基础补全路径"


def adjust_nodes(
    nodes: list[str],
    target_node: str,
    mastery: dict[str, float],
    ai_signal: dict,
    history: dict,
    graph_service: Any,
) -> tuple[list[str], list[dict]]:
    adjusted_nodes = list(nodes)
    adjustments: list[dict] = []

    for node_id in list(adjusted_nodes):
        if node_id == target_node:
            continue
        if (
            mastery.get(node_id, 0.0) > 0.85
            and history["recent_correct"].get(node_id, 0) >= 2
        ):
            adjusted_nodes.remove(node_id)
            adjustments.append(
                {
                    "type": "skip",
                    "target": node_id,
                    "reason": f"{node_id} mastery > 0.85 且 recent_correct >= 2，跳过已掌握节点",
                }
            )

    gap = path_node_id(ai_signal.get("knowledge_gap") or "")
    confusion = float(ai_signal.get("confusion_level") or 0.0)
    remedial_target = None
    if gap and (confusion > 0.75 or mastery.get(gap, 1.0) < 0.4):
        remedial_target = gap
    if remedial_target is None:
        remedial_target = next(
            (
                node_id
                for node_id in adjusted_nodes
                if node_id in mastery and mastery[node_id] < 0.4
            ),
            None,
        )

    if remedial_target is not None:
        prerequisites = graph_service.get_prerequisites(remedial_target)
        prerequisite_ids = [path_node_id(item["id"]) for item in prerequisites]
        if prerequisite_ids:
            remedial_node = min(
                prerequisite_ids,
                key=lambda node_id: (mastery.get(node_id, 0.5), node_id),
            )
            target_index = (
                adjusted_nodes.index(remedial_target)
                if remedial_target in adjusted_nodes
                else 0
            )
            if remedial_node not in adjusted_nodes:
                adjusted_nodes.insert(target_index, remedial_node)
                adjustments.append(
                    {
                        "type": "insert",
                        "target": remedial_node,
                        "reason": f"{remedial_target} mastery/confusion 触发补救，插入前置节点 {remedial_node}",
                    }
                )
            elif remedial_target in adjusted_nodes:
                current_index = adjusted_nodes.index(remedial_node)
                target_index = adjusted_nodes.index(remedial_target)
                if current_index != target_index - 1:
                    adjusted_nodes.pop(current_index)
                    target_index = adjusted_nodes.index(remedial_target)
                    adjusted_nodes.insert(target_index, remedial_node)
                    adjustments.append(
                        {
                            "type": "reorder",
                            "target": remedial_node,
                            "reason": f"将补救节点 {remedial_node} 重排到 {remedial_target} 之前",
                        }
                    )
    return adjusted_nodes, adjustments


def topological_reorder(
    nodes: list[str],
    graph_service: Any,
) -> tuple[list[str], list[dict]]:
    original = list(dict.fromkeys(nodes))
    node_set = set(original)
    edges: dict[str, set[str]] = {node_id: set() for node_id in original}
    indegree = {node_id: 0 for node_id in original}
    for node_id in original:
        for prerequisite in graph_service.get_prerequisites(node_id):
            prerequisite_id = path_node_id(prerequisite["id"])
            if prerequisite_id in node_set and node_id not in edges[prerequisite_id]:
                edges[prerequisite_id].add(node_id)
                indegree[node_id] += 1

    order_index = {node_id: index for index, node_id in enumerate(original)}
    available = [node_id for node_id in original if indegree[node_id] == 0]
    ordered: list[str] = []
    while available:
        available.sort(key=order_index.get)
        node_id = available.pop(0)
        ordered.append(node_id)
        for successor in sorted(edges[node_id], key=order_index.get):
            indegree[successor] -= 1
            if indegree[successor] == 0:
                available.append(successor)

    if len(ordered) != len(original) or ordered == original:
        return original, []
    first_changed = next(
        node_id
        for index, node_id in enumerate(ordered)
        if original[index] != node_id
    )
    return ordered, [
        {
            "type": "reorder",
            "target": first_changed,
            "reason": "根据 Neo4j 前置依赖关系重新排序路径节点",
        }
    ]
