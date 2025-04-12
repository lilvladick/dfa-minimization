import React from "react";

const VERTEX_RADIUS = 24; // Радиус вершины

// Поиск конечной точки дуги
const computeLineEndpoints = (from, to) => {
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const dist = Math.hypot(dx, dy);
  if (dist === 0) return { startX: from.x, startY: from.y, endX: to.x, endY: to.y };
  return {
    startX: from.x + (VERTEX_RADIUS * dx) / dist,
    startY: from.y + (VERTEX_RADIUS * dy) / dist,
    endX: to.x - (VERTEX_RADIUS * dx) / dist,
    endY: to.y - (VERTEX_RADIUS * dy) / dist,
  };
};

// Проверка на обратный переход
const hasReverseTransition = (transitions, fromId, toId) =>
  transitions.some(t => t.from === toId && t.to === fromId);

const Canvas = ({ states, transitions, selected, onCanvasClick, onStateClick }) => {
  return (
    <div
      style={{
        position: "absolute",
        width: "100%",
        height: "100%",
        backgroundImage: `
          linear-gradient(0deg, transparent 24%, rgba(0,0,0,0.1) 25%, rgba(0,0,0,0.1) 26%, transparent 27%, transparent 74%, rgba(0,0,0,0.1) 75%, rgba(0,0,0,0.1) 76%, transparent 77%, transparent),
          linear-gradient(90deg, transparent 24%, rgba(0,0,0,0.1) 25%, rgba(0,0,0,0.1) 26%, transparent 27%, transparent 74%, rgba(0,0,0,0.1) 75%, rgba(0,0,0,0.1) 76%, transparent 77%, transparent)
        `,
        backgroundSize: "40px 40px",
      }}
      onClick={onCanvasClick}
    >
      {/* Отрисовка переходов в одном SVG */}
      <svg
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          zIndex: 1500,
          pointerEvents: "none",
        }}
      >
        <defs>
          {/* Два маркера для дуговых переходов: один для положительного, другой – зеркальный */}
          <marker id="arrowPositive" markerWidth="10" markerHeight="10" refX="10" refY="3" orient="auto">
            <path d="M0,0 L0,6 L10,3 z" fill="#000" />
          </marker>
          <marker id="arrowNegative" markerWidth="10" markerHeight="10" refX="0" refY="3" orient="auto">
            <path d="M10,0 L10,6 L0,3 z" fill="#000" />
          </marker>
          <marker id="arrowSimple" markerWidth="10" markerHeight="10" refX="10" refY="3" orient="auto">
            <path d="M0,0 L0,6 L10,3 z" fill="#000" />
          </marker>
        </defs>
        {transitions.map((t, idx) => {
          const from = states.find(s => s.id === t.from);
          const to = states.find(s => s.id === t.to);
          if (!from || !to) return null;

          // Если петля
          if (from.id === to.id) {
            return (
              <g key={idx}>
                <path
                  d={`
                    M ${from.x} ${from.y - VERTEX_RADIUS}
                    C ${from.x - 40} ${from.y - VERTEX_RADIUS - 40},
                      ${from.x + 40} ${from.y - VERTEX_RADIUS - 40},
                      ${from.x} ${from.y - VERTEX_RADIUS}
                  `}
                  fill="none"
                  stroke="black"
                  strokeWidth="2"
                />
                <text x={from.x} y={from.y - VERTEX_RADIUS - 50} fill="black" fontSize="16" textAnchor="middle">
                  {t.symbol}
                </text>
              </g>
            );
          }

          // Если существует обратный переход для пары
          if (hasReverseTransition(transitions, from.id, to.id)) {
            // Для такой пары определим A и B как вершины с меньшим и большим id соответственно
            const A = from.id < to.id ? from : to;
            const B = from.id < to.id ? to : from;
            const endpoints = computeLineEndpoints(A, B);
            // Определяем знак дуги простым сравнением: если t.from === A.id, sign = +1, иначе -1
            const sign = t.from === A.id ? 1 : -1;
            const dx = endpoints.endX - endpoints.startX;
            const dy = endpoints.endY - endpoints.startY;
            const dist = Math.hypot(dx, dy);
            const perpX = -dy / dist;
            const perpY = dx / dist;
            const offset = 20; 

            // работа с дугами и стрелочками
            const controlX = (endpoints.startX + endpoints.endX) / 2 + sign * perpX * offset;
            const controlY = (endpoints.startY + endpoints.endY) / 2 + sign * perpY * offset;
            const textX = (endpoints.startX + 2 * controlX + endpoints.endX) / 4;
            const textY = (endpoints.startY + 2 * controlY + endpoints.endY) / 4;
            const markerId = sign > 0 ? "arrowPositive" : "arrowNegative";
  
            return (
              <g key={idx}>
                <path
                  d={`M ${endpoints.startX} ${endpoints.startY} Q ${controlX} ${controlY} ${endpoints.endX} ${endpoints.endY}`}
                  fill="none"
                  stroke="black"
                  strokeWidth="2"
                  markerEnd={`url(#${markerId})`}
                />
                <text x={textX} y={textY - 5} fill="black" fontSize="16" textAnchor="middle">
                  {t.symbol}
                </text>
              </g>
            );
          } else {
            // Обычный прямой переход без обратного
            const { startX, startY, endX, endY } = computeLineEndpoints(from, to);
            const textX = (startX + endX) / 2;
            const textY = (startY + endY) / 2 - 5;
            return (
              <g key={idx}>
                <line
                  x1={startX}
                  y1={startY}
                  x2={endX}
                  y2={endY}
                  stroke="black"
                  strokeWidth="2"
                  markerEnd="url(#arrowSimple)"
                />
                <text x={textX} y={textY} fill="black" fontSize="16" textAnchor="middle">
                  {t.symbol}
                </text>
              </g>
            );
          }
        })}
      </svg>

      {/* Отрисовка вершин */}
      {states.map((state) => {
        const baseStyle = {
          position: "absolute",
          width: `${VERTEX_RADIUS * 2}px`,
          height: `${VERTEX_RADIUS * 2}px`,
          borderRadius: "50%",
          border: "2px solid black",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          cursor: "pointer",
          userSelect: "none",
          backgroundColor: "white",
        };
        // Подсветка выбранной вершины
        const style = {
          ...baseStyle,
          left: state.x - VERTEX_RADIUS,
          top: state.y - VERTEX_RADIUS,
          backgroundColor: selected.includes(state.id) ? "rgba(0,255,0,0.2)" : "white",
        };
        return (
          <div key={state.id} style={style} onClick={(e) => onStateClick(state.id, e)}>
            {state.id}
            {/* Если вершина финальная, отрисовываем двойной круг */}
            {state.isFinal && (
              <div style={{
                position: "absolute",
                width: "56px",
                height: "56px",
                borderRadius: "50%",
                border: "2px solid black",
                top: "-4px",
                left: "-4px",
                pointerEvents: "none",
              }}></div>
            )}
            {/* Начальное состояние */}
            {state.id === 0 && (
              <div style={{
                position: "absolute",
                left: "-30px",
                top: "50%",
                transform: "translateY(-50%)",
                fontSize: "24px",
              }}>
                →
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default Canvas;
