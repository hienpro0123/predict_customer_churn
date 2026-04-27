import { useState } from "react";

import BatchPredictionPage from "./pages/BatchPredictionPage";
import DatabasePredictionPage from "./pages/DatabasePredictionPage";
import SinglePredictionPage from "./pages/SinglePredictionPage";

const tabs = [
  { key: "single", label: "Single Prediction" },
  { key: "database", label: "Predict From Database" },
  { key: "batch", label: "Batch Prediction" }
];

export default function App() {
  const [activeTab, setActiveTab] = useState("single");

  return (
    <div className="app-bg">
      <div className="app-shell">
        <header className="hero-shell">
          <div className="hero-topline">
            <span className="hero-chip">Churn Intelligence</span>
            <span className="hero-status">Production Ready</span>
          </div>
          <div className="main-title">Customer Churn System</div>
          <div className="sub-title">Advanced Machine Learning Dashboard for Churn Prediction</div>
          <div className="hero-meta">
            <span>Real-time scoring</span>
            <span>Feature-driven analysis</span>
            <span>Decision-ready insights</span>
          </div>
        </header>

        <nav className="tab-bar">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              className={tab.key === activeTab ? "tab active" : "tab"}
              onClick={() => setActiveTab(tab.key)}
            >
              {tab.label}
            </button>
          ))}
        </nav>

        <main className="surface-panel">
          {activeTab === "single" ? <SinglePredictionPage /> : null}
          {activeTab === "database" ? <DatabasePredictionPage /> : null}
          {activeTab === "batch" ? <BatchPredictionPage /> : null}
        </main>
      </div>
    </div>
  );
}
