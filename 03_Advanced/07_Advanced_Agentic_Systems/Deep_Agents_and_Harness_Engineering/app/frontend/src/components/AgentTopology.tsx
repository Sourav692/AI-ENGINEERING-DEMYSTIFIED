import styles from "./AgentTopology.module.css";

const AGENTS = [
  { id: "senior-developer", label: "Developer", icon: "\u2318", desc: "Plans, writes, and delivers complete Python projects" },
  { id: "code-reviewer", label: "Reviewer", icon: "\u2691", desc: "Reviews code for bugs, style issues, and best practices" },
  { id: "research-agent", label: "Research", icon: "\u2609", desc: "Conducts in-depth web research on any topic" },
  { id: "memory-manager", label: "Memory", icon: "\u2B22", desc: "Saves, recalls, and organizes long-term memory" },
  { id: "aia-customer-analytics", label: "Customer", icon: "\u2606", desc: "Queries customer segmentation, retention, and demographics" },
  { id: "aia-distribution-channels", label: "Channels", icon: "\u2B21", desc: "Queries agent performance and distribution channel data" },
  { id: "aia-policy-underwriting", label: "Policy", icon: "\u25C7", desc: "Queries policy volumes, renewals, and underwriting metrics" },
  { id: "aia-claims-analytics", label: "Claims", icon: "\u25CE", desc: "Queries claim counts, fraud scores, and regional data" },
];

interface Props {
  activeAgent: string | null;
  isStreaming: boolean;
}

export default function AgentTopology({ activeAgent, isStreaming }: Props) {
  const activeNode = AGENTS.find(
    (a) => activeAgent && activeAgent.toLowerCase().includes(a.id.split("-")[0])
  );

  return (
    <div className={styles.topology}>
      {/* Orchestrator hub */}
      <div
        className={`${styles.hub} ${isStreaming ? styles.hubActive : ""}`}
      >
        <div className={styles.hubCore} />
        <span className={styles.hubLabel}>orchestrator</span>
      </div>

      {/* Connection line */}
      <div className={styles.spine}>
        <div
          className={`${styles.spineTracer} ${isStreaming ? styles.tracing : ""}`}
        />
      </div>

      {/* Agent nodes */}
      <div className={styles.nodes}>
        {AGENTS.map((agent) => {
          const isActive =
            activeNode?.id === agent.id ||
            (activeAgent && activeAgent.toLowerCase().includes(agent.id));
          return (
            <div
              key={agent.id}
              className={`${styles.node} ${isActive ? styles.nodeActive : ""}`}
            >
              <div className={styles.nodeRing}>
                <span className={styles.nodeIcon}>{agent.icon}</span>
              </div>
              <span className={styles.nodeLabel}>{agent.label}</span>
              <div className={styles.tooltip}>{agent.desc}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
