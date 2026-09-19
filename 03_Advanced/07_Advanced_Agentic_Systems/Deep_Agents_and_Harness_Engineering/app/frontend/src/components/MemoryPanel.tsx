import { useState } from "react";
import type { Memory } from "../api";
import { deleteMemory, saveMemory } from "../api";
import styles from "./MemoryPanel.module.css";

const CATEGORY_META: Record<string, { color: string; icon: string }> = {
  preference: { color: "#00ddb3", icon: "\u2605" },
  fact: { color: "#34d399", icon: "\u25C6" },
  decision: { color: "#a78bfa", icon: "\u25C8" },
  project: { color: "#fbbf24", icon: "\u25B2" },
  feedback: { color: "#f472b6", icon: "\u25CF" },
  general: { color: "#8d99b0", icon: "\u25CB" },
};

const CATEGORIES = ["preference", "fact", "decision", "project", "feedback", "general"];

interface Props {
  memories: Memory[];
  onRefresh: () => void;
  isOpen: boolean;
  onToggle: () => void;
}

export default function MemoryPanel({
  memories,
  onRefresh,
  isOpen,
  onToggle,
}: Props) {
  const [deleting, setDeleting] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [newContent, setNewContent] = useState("");
  const [newCategory, setNewCategory] = useState("general");
  const [saving, setSaving] = useState(false);

  const handleDelete = async (memory: Memory) => {
    setDeleting(memory.id);
    try {
      await deleteMemory(memory.content.slice(0, 30));
      onRefresh();
    } finally {
      setDeleting(null);
    }
  };

  const handleSave = async () => {
    const trimmed = newContent.trim();
    if (!trimmed || saving) return;
    setSaving(true);
    try {
      await saveMemory(trimmed, newCategory);
      setNewContent("");
      setNewCategory("general");
      setShowForm(false);
      onRefresh();
    } finally {
      setSaving(false);
    }
  };

  const grouped = memories.reduce<Record<string, Memory[]>>((acc, m) => {
    const cat = m.category || "general";
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(m);
    return acc;
  }, {});

  return (
    <aside className={`${styles.panel} ${isOpen ? styles.open : ""}`}>
      {/* Toggle rail */}
      <button className={styles.toggle} onClick={onToggle} title="Toggle memory panel">
        <div className={styles.toggleIconWrap}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="4" fill="var(--memory)" />
            <circle cx="12" cy="12" r="8" stroke="var(--memory)" strokeWidth="1.5" opacity="0.3" />
          </svg>
          {memories.length > 0 && (
            <span className={styles.badge}>{memories.length}</span>
          )}
        </div>
        <span className={styles.toggleLabel}>Memory</span>
      </button>

      {isOpen && (
        <div className={styles.content}>
          {/* Header */}
          <div className={styles.header}>
            <div className={styles.headerTitle}>
              <h3 className={styles.title}>Long-Term Memory</h3>
              <span className={styles.countPill}>{memories.length}</span>
            </div>
            <div className={styles.headerActions}>
              <button
                className={styles.addBtn}
                onClick={() => setShowForm((v) => !v)}
                title="Add a memory manually"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 5v14M5 12h14" strokeLinecap="round" />
                </svg>
              </button>
              <button className={styles.refreshBtn} onClick={onRefresh} title="Refresh memories">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M1 4v6h6M23 20v-6h-6" strokeLinecap="round" strokeLinejoin="round" />
                  <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>
            </div>
          </div>

          {/* Manual memory form */}
          {showForm && (
            <div className={styles.addForm}>
              <textarea
                className={styles.addInput}
                value={newContent}
                onChange={(e) => setNewContent(e.target.value)}
                placeholder="What should the agent remember?"
                rows={3}
              />
              <div className={styles.addFormRow}>
                <select
                  className={styles.addSelect}
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value)}
                >
                  {CATEGORIES.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
                <button
                  className={styles.addSaveBtn}
                  onClick={handleSave}
                  disabled={saving || !newContent.trim()}
                >
                  {saving ? "Saving..." : "Save"}
                </button>
              </div>
            </div>
          )}

          {/* Empty state */}
          {memories.length === 0 ? (
            <div className={styles.empty}>
              <div className={styles.emptyOrb}>
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="12" r="4" fill="var(--memory)" opacity="0.2" />
                  <circle cx="12" cy="12" r="8" stroke="var(--memory)" strokeWidth="1" opacity="0.1" />
                </svg>
              </div>
              <p className={styles.emptyText}>No memories stored yet</p>
              <p className={styles.emptyHint}>
                Ask the agent to remember something or use the + button to save manually.
              </p>
            </div>
          ) : (
            <div className={styles.memoryList}>
              {Object.entries(grouped).map(([category, mems]) => {
                const meta = CATEGORY_META[category] || CATEGORY_META.general;
                return (
                  <div key={category} className={styles.group}>
                    {/* Category header */}
                    <div className={styles.groupHeader}>
                      <span
                        className={styles.catIcon}
                        style={{ color: meta.color }}
                      >
                        {meta.icon}
                      </span>
                      <span className={styles.catName}>{category}</span>
                      <span className={styles.catCount}>{mems.length}</span>
                    </div>

                    {/* Memory items */}
                    {mems.map((mem) => (
                      <div
                        key={mem.id}
                        className={styles.memoryItem}
                        style={{ borderLeftColor: meta.color }}
                      >
                        <p className={styles.memContent}>{mem.content}</p>
                        <div className={styles.memMeta}>
                          <span className={styles.memTime}>
                            {new Date(mem.saved_at).toLocaleDateString()}
                          </span>
                          <button
                            className={styles.deleteBtn}
                            onClick={() => handleDelete(mem)}
                            disabled={deleting === mem.id}
                            title="Forget this memory"
                            aria-label="Delete memory"
                          >
                            {deleting === mem.id ? (
                              <span className={styles.deleting}>...</span>
                            ) : (
                              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M18 6L6 18M6 6l12 12" strokeLinecap="round" />
                              </svg>
                            )}
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </aside>
  );
}
