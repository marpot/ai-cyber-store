import "./AICore.scss";

export default function AICore() {
  return (
    <div className="ai-core">

      <div className="ai-core__glow" />

      <div className="ai-core__ring ai-core__ring--outer" />
      <div className="ai-core__ring ai-core__ring--middle" />
      <div className="ai-core__ring ai-core__ring--inner" />

      <div className="ai-core__nodes">
        <span className="ai-core__node ai-core__node--1" />
        <span className="ai-core__node ai-core__node--2" />
        <span className="ai-core__node ai-core__node--3" />
        <span className="ai-core__node ai-core__node--4" />
        <span className="ai-core__node ai-core__node--5" />
        <span className="ai-core__node ai-core__node--6" />
      </div>

      <div className="ai-core__center">
        <span className="ai-core__label">
          AI
        </span>

        <span className="ai-core__status">
          SYSTEM ONLINE
        </span>
      </div>

      <div className="ai-core__scan-line" />

    </div>
  );
}