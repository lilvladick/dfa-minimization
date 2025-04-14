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
  const [minimizeDialogOpen, setMinimizeDialogOpen] = useState(false);
  const [minimizedJSON, setMinimizedJSON] = useState(""); // для показа ответа сервера

  // Обработка клика по холсту для добавления вершины
  const handleCanvasClick = (e) => {
    if (e.target !== e.currentTarget) return;
    if (mode !== "state") return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const newState = { id: states.length, x, y, isFinal: false, isStart: states.length === 0 };
    setStates([...states, newState]);
  };

  // Обработка клика по вершине
  const handleStateClick = (id, e) => {
    e.stopPropagation();
    if (mode === "state") {
      // Переключаем финальное состояние (начальное состояние не трогаем)
      setStates(states.map(s => s.id === id ? { ...s, isFinal: !s.isFinal } : s));
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

  // Функция сборки JSON для отправки на сервер
  const buildAutomataJSON = () => {
    return {
      num_states: states.length,
      alphabet: Array.from(new Set(transitions.map(t => t.symbol))),
      transitions: transitions.map(t => ({
        from: t.from,
        input: t.symbol,
        to: t.to,
      })),
      start_state: states.find(s => s.isStart)?.id || 0, // начальное состояние
      final_states: states.filter(s => s.isFinal).map(s => s.id),
    };
  };

  // Функция запроса минимизации автомата
  const handleMinimize = async () => {
    const payload = buildAutomataJSON();
    try {
      const response = await fetch("http://localhost:8000/minimize_dfa", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error("Ошибка сервера");
      const minimized = await response.json();
      // Сохраняем JSON ответа для показа в диалоге
      setMinimizedJSON(JSON.stringify(minimized, null, 2));

      // Создаем новое расположение вершин — по кругу
      const newStates = [];
      const angleStep = (2 * Math.PI) / minimized.num_states;
      const centerX = window.innerWidth / 2;
      const centerY = window.innerHeight / 2;
      const radius = 200;
      for (let i = 0; i < minimized.num_states; i++) {
        newStates.push({
          id: i,
          x: centerX + radius * Math.cos(i * angleStep),
          y: centerY + radius * Math.sin(i * angleStep),
          isFinal: minimized.final_states.includes(i),
          isStart: i === minimized.start_state, // Учитываем начальное состояние
        });
      }

      // Переходы: преобразуем поле "input" в "symbol" для UI
      const newTransitions = minimized.transitions.map(t => ({
        from: t.from,
        to: t.to,
        symbol: t.input,
      }));

      // Обновляем состояние
      setStates(newStates);
      setTransitions(newTransitions);
      setSelected([]); // Сбрасываем выбор после минимизации
      setMinimizeDialogOpen(true); // Открываем диалог с JSON-ответом
    } catch (error) {
      console.error(error);
      alert("Ошибка при минимизации автомата");
    }
  };

  return (
    <div style={{ position: "relative", width: "100vw", height: "100vh" }}>
      <Toolbar
        mode={mode}
        setMode={(m) => { setMode(m); setSelected([]); }}
        onCheckDeterminism={handleCheckDeterminism}
        onMinimize={handleMinimize}
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

      {/* Диалог для отображения результата минимизации */}
      <Dialog
        open={minimizeDialogOpen}
        onClose={() => { setMinimizeDialogOpen(false); }}
        fullWidth
        maxWidth="md"
      >
        <DialogTitle>Минимизированный автомат</DialogTitle>
        <DialogContent>
          <pre style={{ whiteSpace: "pre-wrap" }}>{minimizedJSON}</pre>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setMinimizeDialogOpen(false)}>Закрыть</Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default App;