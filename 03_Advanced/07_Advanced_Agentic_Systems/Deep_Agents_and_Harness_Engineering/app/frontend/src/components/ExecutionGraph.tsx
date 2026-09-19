import React from "react";
import styles from "./ExecutionGraph.module.css";

export interface ExecNode {
  id: string;
  label: string;
  type: "start" | "agent" | "tool" | "end";
  status: "pending" | "active" | "complete";
}

export interface ExecEdge {
  from: string;
  to: string;
}

export interface ExecutionTrace {
  nodes: ExecNode[];
  edges: ExecEdge[];
}

interface Props {
  trace: ExecutionTrace;
  isStreaming: boolean;
}

const TYPE_ICON: Record<string, string> = {
  start: "▶",
  agent: "◆",
  tool: "⚙",
  end: "■",
};

function ExecutionGraphInner({ trace, isStreaming }: Props) {
  if (trace.nodes.length === 0) {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <span className={styles.headerIcon}>◈</span>
          <span className={styles.headerLabel}>Execution Graph</span>
        </div>
        <div className={styles.empty}>
          <p>Send a message to see the agent execution flow.</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <span className={styles.headerIcon}>◈</span>
        <span className={styles.headerLabel}>Execution Graph</span>
        {isStreaming && <span className={styles.live}>LIVE</span>}
      </div>
      <div className={styles.nodeList}>
        {trace.nodes.map((node) => (
          <div
            key={node.id}
            className={`${styles.node} ${styles[node.type]} ${styles[node.status]}`}
          >
            <span className={styles.icon}>{TYPE_ICON[node.type] || "●"}</span>
            <span className={styles.label}>{node.label}</span>
            {node.status === "active" && <span className={styles.dot} />}
            {node.status === "complete" && <span className={styles.check}>✓</span>}
          </div>
        ))}
      </div>
    </div>
  );
}

const ExecutionGraph = React.memo(ExecutionGraphInner);
export default ExecutionGraph;
