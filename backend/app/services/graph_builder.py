"""
Graph Builder Service

Builds directed graphs from dependency data and calculates
transitive relationships and impact scores.
"""

from typing import Dict, List, Set, Any
import networkx as nx
from sqlalchemy.orm import Session
from app.models import API, Dependency


class GraphBuilder:
    """Build and analyze dependency graphs."""

    @staticmethod
    def build_dependency_graph(session: Session) -> nx.DiGraph:
        """
        Build directed graph from dependencies table.

        Nodes: services and APIs
        Edges: service -> API (with weight = call_frequency)

        Returns:
            networkx.DiGraph
        """
        graph = nx.DiGraph()

        # Add all APIs as nodes
        apis = session.query(API).all()
        for api in apis:
            graph.add_node(api.id, type="api", status=api.current_status)

        # Add service->API edges
        dependencies = session.query(Dependency).all()
        for dep in dependencies:
            graph.add_node(dep.source_service, type="service")
            graph.add_edge(dep.source_service, dep.target_api_id, weight=dep.call_frequency)

        return graph

    @staticmethod
    def get_dependent_services(api_id: str, session: Session) -> List[str]:
        """
        Find all services that depend on this API (including transitive).

        Uses graph traversal to find all ancestors of the API node.

        Returns:
            List of service names
        """
        graph = GraphBuilder.build_dependency_graph(session)
        if api_id not in graph:
            return []

        # Find all predecessors (in-edges) - services that call this API
        predecessors = set(graph.predecessors(api_id))
        return sorted(list(predecessors))

    @staticmethod
    def calculate_impact_score(
        api_id: str, session: Session
    ) -> Dict[str, Any]:
        """
        Calculate operational impact if API is decommissioned.

        Formula: 0.6 * traffic_percentage + 0.4 * normalized_dependent_count

        Returns:
            {
                "dependent_services": int,
                "traffic_percentage": float,
                "impact_score": float (0-1),
                "impact_severity": str (LOW/MEDIUM/HIGH)
            }
        """
        dependencies = session.query(Dependency).filter_by(target_api_id=api_id).all()

        # Unique services that depend on this API
        dependent_services = len(set(d.source_service for d in dependencies))

        # Total traffic percentage
        traffic_percentage = sum(d.traffic_percentage for d in dependencies) if dependencies else 0.0

        # Normalize dependencies to 0-1 scale (assume max 20 services)
        normalized_deps = min(dependent_services / 20.0, 1.0)

        # Weighted calculation
        impact_score = 0.6 * traffic_percentage + 0.4 * normalized_deps

        # Classify severity
        if impact_score >= 0.7:
            severity = "HIGH"
        elif impact_score >= 0.3:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        return {
            "dependent_services": dependent_services,
            "traffic_percentage": round(traffic_percentage, 3),
            "impact_score": round(impact_score, 3),
            "impact_severity": severity,
        }

    @staticmethod
    def get_graph_data(api_id: str, session: Session) -> Dict[str, Any]:
        """
        Get D3.js-compatible graph data for a specific API.

        Returns:
            {
                "nodes": [{"id": str, "type": str, "status": str}],
                "edges": [{"source": str, "target": str, "weight": int}],
                "impact": {...}
            }
        """
        graph = GraphBuilder.build_dependency_graph(session)

        # Get all nodes connected to this API (direct)
        api_node = api_id
        connected_nodes = set()
        connected_nodes.add(api_node)

        # Predecessors (services that call this API)
        connected_nodes.update(graph.predecessors(api_node))

        # Successors (APIs this calls) - if applicable
        connected_nodes.update(graph.successors(api_node))

        # Build nodes list
        nodes = []
        for node_id in connected_nodes:
            node_data = graph.nodes[node_id]
            nodes.append(
                {
                    "id": node_id,
                    "type": node_data.get("type", "service"),
                    "status": node_data.get("status"),
                }
            )

        # Build edges list
        edges = []
        for source, target in graph.edges():
            if source in connected_nodes and target in connected_nodes:
                weight = graph.edges[source, target].get("weight", 1)
                edges.append(
                    {
                        "source": source,
                        "target": target,
                        "weight": weight,
                    }
                )

        # Calculate impact
        impact = GraphBuilder.calculate_impact_score(api_id, session)

        return {
            "nodes": nodes,
            "edges": edges,
            "impact": impact,
        }

    @staticmethod
    def calculate_blast_radius(api_ids: List[str], session: Session) -> Dict[str, Any]:
        """
        Calculate aggregated blast radius for multiple APIs.

        Returns:
            {
                "dependent_services": int,
                "traffic_percentage": float,
                "impact_score": float,
                "severity": str,
                "affected_apis": List[str],
                "recommendation": str
            }
        """
        all_dependencies = []
        all_services = set()
        total_traffic = 0.0

        for api_id in api_ids:
            dependencies = session.query(Dependency).filter_by(target_api_id=api_id).all()
            all_dependencies.extend(dependencies)
            all_services.update(d.source_service for d in dependencies)
            total_traffic += sum(d.traffic_percentage for d in dependencies)

        dependent_services = len(all_services)
        normalized_deps = min(dependent_services / 20.0, 1.0)
        impact_score = 0.6 * total_traffic + 0.4 * normalized_deps

        # Classify
        if impact_score >= 0.7:
            severity = "HIGH"
            recommendation = "⚠️ Do not decommission - critical dependencies exist"
        elif impact_score >= 0.3:
            severity = "MEDIUM"
            recommendation = "⚠️ Careful planning needed - coordinate with dependent teams"
        else:
            severity = "LOW"
            recommendation = "✅ Safe to decommission"

        return {
            "dependent_services": dependent_services,
            "traffic_percentage": round(total_traffic, 3),
            "impact_score": round(impact_score, 3),
            "severity": severity,
            "affected_apis": api_ids,
            "recommendation": recommendation,
        }
