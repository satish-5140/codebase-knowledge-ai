import networkx as nx
from pyvis.network import Network
from typing import Dict
import os
from config.settings import BASE_DIR


OUTPUT_PATH = BASE_DIR / "data" / "graph.html"


def build_networkx_graph(dependency_data: Dict):
    """
    Converts our dependency data into a NetworkX graph object.
    """
    G = nx.DiGraph()

    graph = dependency_data["graph"]

    for source_file, imported_files in graph.items():
        # Add source node
        G.add_node(source_file, label=source_file.split("/")[-1])

        for target_file in imported_files:
            # Add target node
            G.add_node(target_file, label=target_file.split("/")[-1])
            # Add edge (connection)
            G.add_edge(source_file, target_file)

    return G


def get_node_color(filepath: str) -> str:
    """
    Colors nodes by file type/location.
    """
    if "test" in filepath.lower():
        return "#f39c12"   # Orange for test files
    elif "src" in filepath.lower():
        return "#2ecc71"   # Green for source files
    elif "config" in filepath.lower():
        return "#9b59b6"   # Purple for config files
    else:
        return "#3498db"   # Blue for others


def build_visual_graph(dependency_data: Dict) -> str:
    """
    Builds an interactive HTML graph using PyVis.
    Returns the path to the saved HTML file.
    """
    print("\n🕸️  Building visual code graph...")

    G = build_networkx_graph(dependency_data)

    # Create PyVis network
    net = Network(
        height="750px",
        width="100%",
        bgcolor="#1a1a2e",
        font_color="white",
        directed=True
    )

    # Add nodes with colors and sizes
    reverse_graph = dependency_data["reverse_graph"]

    for node in G.nodes():
        # More imported = bigger node
        importance = len(reverse_graph.get(node, [])) + 1
        size = min(10 + importance * 3, 50)
        color = get_node_color(node)
        label = node.split("/")[-1]  # Just filename not full path

        net.add_node(
            node,
            label=label,
            title=node,        # Tooltip on hover
            color=color,
            size=size,
            font={"size": 12}
        )

    # Add edges
    for source, target in G.edges():
        net.add_edge(source, target, color="#ffffff30", arrows="to")

    # Physics settings for nice layout
    net.set_options("""
    {
        "physics": {
            "enabled": true,
            "barnesHut": {
                "gravitationalConstant": -8000,
                "centralGravity": 0.3,
                "springLength": 150,
                "springConstant": 0.04
            },
            "stabilization": {
                "iterations": 200
            }
        },
        "interaction": {
            "hover": true,
            "tooltipDelay": 100
        }
    }
    """)

    # Save to HTML file
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    net.save_graph(str(OUTPUT_PATH))

    print(f"✅ Graph saved to: {OUTPUT_PATH}")
    print(f"📊 Nodes: {len(G.nodes())} | Edges: {len(G.edges())}")

    return str(OUTPUT_PATH)


def get_graph_stats(dependency_data: Dict) -> Dict:
    """
    Returns statistics about the codebase graph.
    """
    G = build_networkx_graph(dependency_data)

    return {
        "total_files": G.number_of_nodes(),
        "total_connections": G.number_of_edges(),
        "most_connected": sorted(
            G.nodes(),
            key=lambda n: G.in_degree(n),
            reverse=True
        )[:5]
    }


if __name__ == "__main__":
    from ingestion.repo_reader import load_repository
    from ingestion.code_parser import parse_all_files
    from graph.dependency_graph import build_dependency_graph

    records = load_repository("https://github.com/pallets/flask")
    parsed = parse_all_files(records)

    print("\n🔗 Building dependency graph...")
    dependency_data = build_dependency_graph(parsed)

    # Build visual graph
    output_path = build_visual_graph(dependency_data)

    # Print stats
    stats = get_graph_stats(dependency_data)
    print(f"\n📊 Graph Stats:")
    print(f"  Total Files      : {stats['total_files']}")
    print(f"  Total Connections: {stats['total_connections']}")
    print(f"  Most Connected   : {stats['most_connected']}")

    print(f"\n🌐 Open this file in your browser:")
    print(f"  {output_path}")