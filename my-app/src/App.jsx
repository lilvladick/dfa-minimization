import { useState } from "react";
import Toolbar from "./components/Toolbar";
import Canvas from "./components/Canvas";
import { checkDeterminism } from "./utils/Utils";
import { Dialog, DialogActions, DialogContent, DialogTitle, TextField, Button } from "@mui/material";

const App = () => {
  const [states, setStates] = useState([]);
  const [transitions, setTransitions] = useState([]);
  const [mode, setMode] = useState("state");
  const [selected, setSelected] = useState([]); // выбранные вершины для построения перехода
  const [dialogOpen, setDialogOpen] = useState(false);
  const [transitionSymbol, setTransitionSymbol] = useState("");

  // Обработка клика по холсту для добавления вершины
  const handleCanvasClick = (e) => {
    if (e.target !== e.currentTarget) return;
    if (mode !== "state") return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const newState = { id: states.length, x, y, isFinal: false };
    setStates([...states, newState]);
  };

  // Обработка клика по вершине
  const handleStateClick = (id, e) => {
    e.stopPropagation();
    if (mode === "state") {
      // Переключаем финальное состояние (первая вершина – начальное, не переключается)
      setStates(states.map(s => s.id === id && s.id !== 0 ? { ...s, isFinal: !s.isFinal } : s));
    } else if (mode === "transition") {
      if (selected.length === 0) {
        setSelected([id]);
      } else if (selected.length === 1) {
        setSelected([selected[0], id]);
        setDialogOpen(true);
      }
    }
  };

  // Добавление перехода после ввода символа
  const handleAddTransition = () => {
    const [from, to] = selected;
    if (transitionSymbol.trim() !== "") {
      setTransitions([...transitions, { from, to, symbol: transitionSymbol }]);
    }
    setDialogOpen(false);
    setSelected([]);
    setTransitionSymbol("");
  };

  // Проверка детерминированности автомата
  const handleCheckDeterminism = () => {
    if (checkDeterminism(transitions)) {
      alert("Автомат детерминирован.");
    } else {
      alert("Автомат недетерминирован.");
    }
  };

  return (
    <div style={{ position: "relative", width: "100vw", height: "100vh" }}>
      <Toolbar
        mode={mode}
        setMode={(m) => { setMode(m); setSelected([]); }}
        onCheckDeterminism={handleCheckDeterminism}
      />
      <Canvas
        states={states}
        transitions={transitions}
        selected={selected}
        onCanvasClick={handleCanvasClick}
        onStateClick={handleStateClick}
      />

      {/* Диалог ввода символа перехода */}
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
