import { Button } from "@mui/material";

const Toolbar = ({ mode, setMode, onCheckDeterminism }) => {
  return (
    <div
      style={{
        position: "absolute",
        top: 16,
        left: "50%",
        transform: "translateX(-50%)",
        display: "flex",
        gap: "16px",
        zIndex: 2000
      }}
    >
      <Button variant="contained" onClick={() => setMode("state")}>
        Добавить вершины
      </Button>
      <Button variant="contained" onClick={() => setMode("transition")}>
        Добавить путь
      </Button>
      <Button variant="contained" color="secondary" onClick={onCheckDeterminism}>
        Проверить ДКА
      </Button>
    </div>
  );
};

export default Toolbar;
