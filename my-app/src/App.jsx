import { useState } from "react";
import { Button, Dialog, DialogActions, DialogContent, DialogTitle, TextField } from "@mui/material";

const App = () => {
  // Состояния для вершин, переходов и работы в разных режимах
  const [states, setStates] = useState([]);
  const [transitions, setTransitions] = useState([]);
  const [mode, setMode] = useState("state"); // "state" или "transition"
  const [selected, setSelected] = useState([]);  // выбранные вершины для построения перехода
  const [dialogOpen, setDialogOpen] = useState(false);
  const [transitionSymbol, setTransitionSymbol] = useState("");

  // Обработка клика по "холсту" (контейнеру)
  const handleCanvasClick = (e) => {
    // Если клик произошёл не по самому контейнеру, а по его вложенным элементам (например, по кнопке),
    // то завершаем обработку.
    if (e.target !== e.currentTarget) return;

    if (mode !== "state") return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const newState = {
      id: states.length,
      x,
      y,
      isFinal: false
    };
    setStates([...states, newState]);
  };

  // Обработка клика по вершине
  const handleStateClick = (id, e) => {
    e.stopPropagation(); // чтобы не срабатывал клик по холсту
    if (mode === "state") {
      // Если режим добавления вершин: переключаем финальное состояние, но не для первой вершины (начального)
      setStates(states.map(s => s.id === id && s.id !== 0 ? { ...s, isFinal: !s.isFinal } : s));
    } else if (mode === "transition") {
      // Если режим добавления переходов
      if (selected.length === 0) {
        setSelected([id]);
      } else if (selected.length === 1) {
        // Позволяем создать переход и даже петлю (если id совпадают)
        setSelected([selected[0], id]);
        setDialogOpen(true);
      }
    }
  };

  // Функция добавления перехода после ввода символа
  const handleAddTransition = () => {
    const [from, to] = selected;
    if (transitionSymbol.trim() !== "") {
      setTransitions([...transitions, { from, to, symbol: transitionSymbol }]);
    }
    setDialogOpen(false);
    setSelected([]);
    setTransitionSymbol("");
  };

  // Определяем стиль для отрисовки вершин:
  // Если вершина выбрана для построения перехода, добавляем лёгкий зелёный фон.
  const getStateStyle = (state) => {
    const baseStyle = {
      position: "absolute",
      width: "48px",
      height: "48px",
      borderRadius: "50%",
      border: "2px solid black",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      cursor: "pointer",
      backgroundColor: selected.includes(state.id) && mode === "transition" ? "rgba(0,255,0,0.2)" : "white",
      userSelect: "none"
    };
    return baseStyle;
  };

  return (
    <div
      style={{
        position: "relative",
        width: "100vw",
        height: "100vh",
        backgroundImage: `
          linear-gradient(0deg, transparent 24%, rgba(0,0,0,0.1) 25%, rgba(0,0,0,0.1) 26%, transparent 27%, transparent 74%, rgba(0,0,0,0.1) 75%, rgba(0,0,0,0.1) 76%, transparent 77%, transparent),
          linear-gradient(90deg, transparent 24%, rgba(0,0,0,0.1) 25%, rgba(0,0,0,0.1) 26%, transparent 27%, transparent 74%, rgba(0,0,0,0.1) 75%, rgba(0,0,0,0.1) 76%, transparent 77%, transparent)
        `,
        backgroundSize: "40px 40px"
      }}
      onClick={handleCanvasClick}
    >
      {/* Панель кнопок в центре сверху */}
      <div
        style={{
          position: "absolute",
          top: 16,
          left: "50%",
          transform: "translateX(-50%)",
          display: "flex",
          gap: "16px",
          zIndex: 1000
        }}
      >
        <Button variant="contained" onClick={() => { setMode("state"); setSelected([]); }}>
          Добавить вершины
        </Button>
        <Button variant="contained" onClick={() => { setMode("transition"); setSelected([]); }}>
          Добавить путь
        </Button>
        <Button
          variant="contained"
          color="secondary"
          onClick={() => alert("Проверка детерминированности пока не реализована")}
        >
          Проверить ДКА
        </Button>
      </div>

      {/* Отрисовка переходов */}
      {transitions.map((t, idx) => {
        const from = states.find(s => s.id === t.from);
        const to = states.find(s => s.id === t.to);
        if (!from || !to) return null;

        // Если это петля (переход в ту же вершину), отрисовываем дугу в виде небольшой окружности.
        const isLoop = from.id === to.id;

        return (
          <svg
            key={idx}
            style={{ position: "absolute", top: 0, left: 0, pointerEvents: "none" }}
            width="100%"
            height="100%"
          >
            {isLoop ? (
              <>
                <path
                  d={`
                    M ${from.x} ${from.y - 24}
                    C ${from.x - 40} ${from.y - 60}, ${from.x + 40} ${from.y - 60}, ${from.x} ${from.y - 24}
                  `}
                  fill="none"
                  stroke="black"
                  strokeWidth="2"
                />
                <text x={from.x} y={from.y - 70} fill="black" fontSize="16" textAnchor="middle">
                  {t.symbol}
                </text>
              </>
            ) : (
              <>
                <line
                  x1={from.x}
                  y1={from.y}
                  x2={to.x}
                  y2={to.y}
                  stroke="black"
                  strokeWidth="2"
                  markerEnd="url(#arrow)"
                />
                <text
                  x={(from.x + to.x) / 2}
                  y={(from.y + to.y) / 2 - 5}
                  fill="black"
                  fontSize="16"
                  textAnchor="middle"
                >
                  {t.symbol}
                </text>
              </>
            )}
            <defs>
              <marker id="arrow" markerWidth="10" markerHeight="10" refX="10" refY="3" orient="auto">
                <path d="M0,0 L0,6 L10,3 z" fill="#000" />
              </marker>
            </defs>
          </svg>
        );
      })}

      {/* Отрисовка вершин */}
      {states.map((state) => (
        <div
          key={state.id}
          style={{
            ...getStateStyle(state),
            left: state.x - 24,
            top: state.y - 24
          }}
          onClick={(e) => handleStateClick(state.id, e)}
        >
          {state.id}
          {state.isFinal && (
            <div style={{
              position: "absolute",
              width: "64px",
              height: "64px",
              borderRadius: "50%",
              border: "2px solid black",
              top: "-8px",
              left: "-8px",
              pointerEvents: "none"
            }}></div>
          )}
          {/* Отрисовка начального состояния (первая вершина) */}
          {state.id === 0 && (
            <div style={{
              position: "absolute",
              left: "-30px",
              top: "50%",
              transform: "translateY(-50%)",
              fontSize: "24px"
            }}>
              →
            </div>
          )}
        </div>
      ))}

      {/* Диалог для ввода символа перехода */}
      <Dialog open={dialogOpen} onClose={() => { setDialogOpen(false); setSelected([]); }}>
        <DialogTitle>Введите символ перехода</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            fullWidth
            value={transitionSymbol}
            onChange={(e) => setTransitionSymbol(e.target.value)}
            inputProps={{ maxLength: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setDialogOpen(false); setSelected([]); }}>Отмена</Button>
          <Button onClick={handleAddTransition}>Добавить</Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default App;
